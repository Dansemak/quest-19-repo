from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    package_line_id = fields.Many2one("package.line", string="Package Line")
