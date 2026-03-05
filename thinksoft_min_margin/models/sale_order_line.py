from odoo import models, fields, api,_

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"



    min_margin_rate = fields.Float(
        related="product_id.categ_id.min_margin_rate",
        string="Min Margin (%)",
        store=True,
        readonly=True
    )

    min_sale_price = fields.Float(
        string="Min Sale Price",
        compute="_compute_min_margin",
        track=True
    )

    min_margin = fields.Float(
        string="Min Margin",
        compute="_compute_min_margin",
        help="Minimum margin percentage calculated based on the cost and minimum sale price. This is used to compare against the actual margin percentage to ensure that the sale price does not go below the minimum sale price.",
    )

    price_unit = fields.Float(
        help="This price is calculated based on the above price list"
    )

    list_price = fields.Float(
        string="List Price",
        related="product_id.list_price",
        help="List Price is the sale price on the product template"
    )

    @api.depends("product_id", "min_margin_rate")
    def _compute_min_margin(self):
        for line in self:
            cost = line.purchase_price
            rate = line.min_margin_rate or 0.0

            if rate and cost:
                line.min_sale_price = round(cost * (1 + rate), 2)
                line.min_margin = round((cost * (1 + rate) - cost), 2)
            else:
                line.min_sale_price = 0.0
                line.min_margin = 0.0
