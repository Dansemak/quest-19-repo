from odoo import fields, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    department_id = fields.Many2one(
        "mrp.department",
        string="Department",
        help="The manufacturing department responsible for this BoM",
    )
