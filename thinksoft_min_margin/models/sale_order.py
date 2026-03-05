from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    require_approval = fields.Boolean(
        string="Require Approval",
        compute="_check_min_margin",
        default=False,
        help="Indicates whether or not this order requires approval to be confirmed",
        store=True,
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
            order.require_approval = any(
                line.min_margin_rate > line.margin_percent for line in order.order_line
            )

    def send_for_approval(self):
        self.ensure_one()
        self.state = 'approval_pending'

    def action_approve(self):
        self.ensure_one()
        self.state = 'draft'
        self.require_approval = False

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        self.require_approval = False
        return res


