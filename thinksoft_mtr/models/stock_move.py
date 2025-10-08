from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    mtr_template_ids = fields.Many2many(
        "mtr.template", "mtr_template_stock_move_rel", string="MTR"
    )
