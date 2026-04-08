import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

log = logging.getLogger(__name__).info


class SaleOrder(models.Model):
    _inherit = "sale.order"

    require_low_margin_approval = fields.Boolean(
        string="Require Approval",
        compute="_check_min_margin",
        default=False,
        help="Indicates whether or not this order requires approval to be confirmed",
        store=True,
        copy=False,
    )

    low_margin_approved = fields.Boolean(
        string="Low Margin Approved", default=False, store=True, copy=False
    )

    state = fields.Selection(
        selection_add=[
            ("approval_pending", "Approval Pending"),
            ("sent",),
        ],
        ondelete={
            "approval_pending": "set default",
            "approved": "set default",
        },
    )



    @api.depends("order_line", "order_line.min_margin", "order_line.margin_percent")
    def _check_min_margin(self):
        for order in self:
            order.require_low_margin_approval = any(
                line.min_margin_rate > line.margin_percent for line in order.order_line
            )

    def action_request_low_margin_approval(self):
        self.ensure_one()

        if not self.require_low_margin_approval:
            raise UserError("This order does not require approval.")

        # Get Approvers
        group_approvers = self.env.ref('thinksoft_min_margin.group_approve_low_margin')
        users_to_notify = group_approvers.user_ids

        # __Display a notification if no approver is set_____________
        if not users_to_notify:
            return {
                "type": 'ir.actions.client',
                "tag": "display_notification",
                "params": {
                    "title": "No Approvers Set",
                    "message": "No one is set yet to approve Low Margin Sale Orders. Contact Management immediately",
                    "type": "danger",
                    "sticky": True
                }
            }

        # __Creates an activity for the approvers__________________
        message_body = f"""
                    <p><strong>Low Margin Sale Order Approval</strong></p>
                        <ul>
                            <li><strong>Order:</strong> {self.name}</li>
                            <li><strong>Customer:</strong> {self.partner_id.name}</li>
                        </ul>
                    <p>This order has one or more lines with a margin below the minimum threshold and needs approval.</p>
                        """
        summary = f'Low Margin Approval Requested: {self.name}'

        for user in users_to_notify:
            self._schedule_margin_activities(user, summary, message_body)


        # __Sends a notification to the approvers___________________
        title = 'Approval Required'
        message = f'Order {self.name} needs your approval'
        type = 'info'

        for user in users_to_notify:
            self._notify_partner(user, title, message, type)

        self.write({'state': 'approval_pending'})


    def action_approve_low_margin(self):
        self.ensure_one()
        self.state = "draft"
        self.require_low_margin_approval = False
        self.low_margin_approved = True

        # __Closes the Approval Activity_____________________________________________
        if self.min_margin_activities():
            self.min_margin_activities().action_feedback(feedback=_("Low Margin Approved."))


        # __Posts message on the chatter____________________________________________
        self.message_post(
            body=_("Low margin approved by %s") % self.env.user.name,
            subtype_xmlid="mail.mt_comment",
        )

        salesperson = self.user_id

        # __Creates an activity for the Salesperson______________________________
        summary = f'Low Margin Approved on {self.name}'
        self._schedule_margin_activities(salesperson, summary)

        # __Sends a notification to the Salesperson that the sale order has been approved
        title = 'Sale Order Approved'
        message = f'Order {self.name} is now approved. You can now proceed to the next step.'
        type = 'success'
        self._notify_partner(salesperson, title, message, type)


    def _schedule_margin_activities(self, user, summary='', note=''):
        self.activity_schedule(
            'thinksoft_min_margin.mail_activity_type_low_margin_approval',
            summary=summary,
            note=note,
            user_id=user.id,
        )


    def _notify_partner(self, user, title, message, type):

        return self.env['bus.bus']._sendone(
                user.partner_id,
                'simple_notification',
                {
                    'title': title,
                    'message': message,
                    'sticky': True,
                    'type': type,
                }
            )


    def write(self, vals):
        # If we're in confirmation and low_margin_approved is being set to True
        # but it was False, prevent the change
        if "low_margin_approved" in vals and vals["low_margin_approved"] is True:
            # Check if we're in a confirmation context and it was previously False
            if (
                self.env.context.get("confirming_order")
                and not self.low_margin_approved
            ):
                vals.pop("low_margin_approved")  # Remove from vals to prevent change

        return super().write(vals)

    def action_confirm(self):

        if self.require_low_margin_approval and not self.low_margin_approved:
            raise ValidationError("An approval is needed before confirming a Sale Order \nthat has one or more products that do noe meet the margin threshold.")

        if self.min_margin_activities():
            self.min_margin_activities().action_feedback(feedback=_("Sale Order completed."))

        res = super().action_confirm()

        self.require_low_margin_approval = False
        return res


    def action_quotation_send(self):

        if self.require_low_margin_approval and not self.low_margin_approved:
            raise ValidationError("An approval is needed before sending a Sale Order \nthat has one or more products that do noe meet the margin threshold.")

        return super().action_quotation_send()

    def min_margin_activities(self):

        activity_type = self.env.ref("thinksoft_min_margin.mail_activity_type_low_margin_approval")
        activities = self.env["mail.activity"].search([
            ("res_model", "=", "sale.order"),
            ("res_id", "=", self.id),
            ("activity_type_id", "=", activity_type.id),
        ])

        return activities