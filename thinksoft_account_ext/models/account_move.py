from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    waybill = fields.Char(string="Waybill")