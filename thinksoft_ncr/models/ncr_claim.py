from odoo import fields, models, _


class NcrClaim(models.Model):
    _name = 'ncr.claim'
    _description = 'Non-Conformance Report'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
