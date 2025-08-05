from odoo import models, fields, api


class MtrTemplate(models.Model):
    _name = 'mtr.template'
    _inherit = ['mail.thread']
    _description = "MTR"

    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char("Name", readonly=True)