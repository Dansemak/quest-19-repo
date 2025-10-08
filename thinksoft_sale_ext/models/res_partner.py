from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    outside_salesperson_id = fields.Many2one(
        "res.users",
        string="Outside Salesperson",
        help="The outside salesperson in charge of sales for this contact"
    )
