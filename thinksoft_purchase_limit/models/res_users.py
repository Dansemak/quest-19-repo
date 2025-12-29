from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    purchase_limit = fields.Monetary(string="Purchase Order Limit")
