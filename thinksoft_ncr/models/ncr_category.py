from odoo import fields, models


class NcrCategory(models.Model):
    _name = "ncr.category"
    _description = "NCR Category"

    name = fields.Char(string="Category", required=True)
    parent_category_id = fields.Many2one("ncr.category", string="Parent Category")
