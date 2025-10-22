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
            locations = {}

            for record in line.product_stock_quant_ids:
                if record.location_id:
                    locations.append(record.location_id.id)

            line.available_location_ids = [(6, 0, locations)] if locations else False