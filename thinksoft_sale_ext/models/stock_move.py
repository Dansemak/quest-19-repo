from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    # adding relational fields to stock.picking in the thinksoft_sale_ext module
    # to avoid hard dependancies between extension modules

    tagging = fields.Char(
        help="Customer Line Item Reference for custom identification",
        readonly=True,
        related="sale_line_id.tagging"
    )
