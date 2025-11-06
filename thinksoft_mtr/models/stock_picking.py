from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    mtr_move_ids = fields.One2many(
        "stock.move", "picking_id", string="MTR Stock Moves", copy=True
    )
