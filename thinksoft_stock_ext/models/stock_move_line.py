from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    seq_no = fields.Integer(related="move_id.seq_no", help="Line Number")
    available_locations_ids = fields.One2many(
        "stock.location",
        string="Available Locations",
        compute="_compute_available_locations_ids",
    )

    @api.depends('product_id')
    def _compute_available_locations_ids(self):
        for line in self:
            if not line.product_id:
                line.available_locations_ids = [(5, 0, 0)]
                continue

            stock_quants = self.env["stock.quant"].search([
                ("product_id", "=", line.product_id.id),
                ("quantity", ">", "0"),
            ])

            locations = stock_quants.mapped("location_id")

            line.available_locations_ids = [(6, 0, locations.ids)]