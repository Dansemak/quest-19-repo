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

        originals = [(line, line.price_unit, line.discount) for line in self]

        for line, _, _ in originals:
            line.price_unit = line.price_reduce_taxexcl
            line.discount = 0.0

        res = super(SaleOrderLine, self)._compute_amount()

        for line, orig_price, orig_discount in originals:
            line.price_unit = orig_price
            line.discount = orig_discount

        return res
