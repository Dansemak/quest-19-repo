from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    package_plan_id = fields.Many2one("package.plan", string="Package")
