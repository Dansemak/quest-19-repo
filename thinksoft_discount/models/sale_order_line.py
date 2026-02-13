from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_reduce_taxexcl = fields.Monetary(compute="_compute_amount")

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_ids')
    def _compute_amount(self):
        for line in self:
            if line.discount > 0.0:
                line.price_reduce_taxexcl = round(line.price_unit * (1 - (line.discount / 100.0)), 2)
            else:
                line.price_reduce_taxexcl = line.price_unit

            original_price_unit = line.price_unit
            original_discount = line.discount

            line.price_unit = line.price_reduce_taxexcl
            line.discount = 0.0

            super(SaleOrderLine, self)._compute_amount()

            line.price_unit = original_price_unit
            line.discount = original_discount
