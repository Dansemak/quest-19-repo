from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # adding relational fields to account.move in the thinksoft_sale_ext module
    # to avoid hard dependancies between extension modules

    sale_freight_id = fields.Many2one(
        "sale.freight",
        string="Freight Charge",
        help="Where and how the freight is being charged",
        readonly=True,
        compute="_compute_sale_freight_id"
    )

    @api.depends("invoice_line_ids.sale_line_ids.order_id")
    def _compute_sale_freight_id(self):
        for move in self:
            sale_order = move.invoice_line_ids.sale_line_ids.order_id[:1]

            if sale_order:
                move.sale_freight_id = sale_order.sale_freight_id
            else:
                move.sale_freight_id = False
