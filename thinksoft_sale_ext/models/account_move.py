from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # adding relational fields to account.move in the thinksoft_sale_ext module
    # to avoid hard dependancies between extension modules

    carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Shipping Method",
        readonly=True,
        compute="_compute_sale_fields",
    )
    sale_freight_id = fields.Many2one(
        "sale.freight",
        string="Freight Charge",
        help="Where and how the freight is being charged",
        readonly=True,
        compute="_compute_sale_fields",
    )

    @api.depends("invoice_line_ids.sale_line_ids.order_id")
    def _compute_sale_fields(self):
        for move in self:
            sale_order = move.invoice_line_ids.sale_line_ids.order_id[:1]

            if sale_order:
                move.sale_freight_id = sale_order.sale_freight_id
                move.carrier_id = sale_order.carrier_id
            else:
                move.sale_freight_id = False
                move.carrier_id = False
