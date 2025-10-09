from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    # adding relational fields to stock.picking in the thinksoft_sale_ext module
    # to avoid hard dependancies between extension modules

    tagging = fields.Char(
        compute="_get_tagging",
        help="Customer Line Item Reference for custom identification",
        readonly=True,
    )

    def _get_tagging(self):
        for move in self:
            move.tagging = move.sale_line_id.tagging        
