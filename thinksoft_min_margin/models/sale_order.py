import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

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

        group_approvers = self.env.ref('thinksoft_min_margin.group_approve_low_margin')
        users_to_notify = group_approvers.user_ids

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


        message_body = f"""
            <p><strong>Low Margin Sale Order Approval</strong></p>
                <ul>
                    <li><strong>Order:</strong> {self.name}</li>
                    <li><strong>Customer:</strong> {self.partner_id.name}</li>
                    <li><strong>Amount:</strong> {self.amount_total} {self.currency_id.name}</li>
                </ul>
            <p>This order has one or more lines with a margin below the minimum threshold and needs approval approved.</p>


                        """

        for user in users_to_notify:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                summary=f'Low Margin Approved: {self.name}',
                note=message_body,
                user_id=user.id,
            )

        self.message_post(
            body=f"Approval requested for low margin order:<br/>{self.name}",
            subject="Approval Request - Low margin",
            message_type="notification",
            subtype_xmlid="mail.mt_comment",
        )

        self._send_inbox_notification(users_to_notify)
        # self._notify_approvers(users_to_notify)

        self.write({'state': 'approval_pending'})

    def _notify_approvers(self, users):
        """Send inbox notification to approvers"""
        if not users:
            return

        # Send to inbox (bell icon)
        self.env['bus.bus']._sendone(
            users.mapped('partner_id'),
            'simple_notification',
            {
                'title': 'Approval Required',
                'message': f'Order {self.name} needs your approval',
                'sticky': True,
                'type': 'warning',
            }
        )

    def _send_inbox_notification(self, users):
        """Send notification to user's inbox"""
        # This creates a notification in the user's inbox (bell icon)
        self.message_notify(
            partner_ids=users.mapped('partner_id').ids,
            body=f"""
                <p><strong>Low Margin Approval Required</strong></p>
                <p>Order <strong>{self.name}</strong> for customer <strong>{self.partner_id.name}</strong>
                requires your approval due to low margins.</p>
            """,
            subject=f'Approval Required: {self.name}',
        )


    def action_approve_low_margin(self):
        self.ensure_one()
        self.state = "draft"
        self.require_low_margin_approval = False
        self.low_margin_approved = True

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
        # Call parent with context flag
        res = super(
            SaleOrder, self.with_context(confirming_order=True)
        ).action_confirm()

        self.require_low_margin_approval = False
        return res
