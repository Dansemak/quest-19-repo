from odoo import api, fields, models
from odoo.exceptions import ValidationError


class NcrCategory(models.Model):
    _name = "ncr.category"
    _description = "NCR Category"

    name = fields.Char(string="Category", required=True)
    parent_category_id = fields.Many2one("ncr.category", string="Parent Category")

    @api.model
    def create(self, vals_list):
        if isinstance(vals_list, list):
            for vals in vals_list:
                if "name" in vals and vals["name"]:
                    vals["name"] = vals["name"].upper()
        else:
            if "name" in vals_list and vals_list["name"]:
                vals_list["name"] = vals_list["name"].upper()
        return super().create(vals_list)

    @api.onchange("name")
    def _onchange_name(self):
        for record in self:
            if record.name:
                record.name = record.name.upper()

    @api.constrains("name", "parent_category_id")
    def _check_unique_name(self):
        for record in self:
            existing = self.search_count(
                [
                    ("name", "=", record.name),
                    ("parent_category_id", "=", record.parent_category_id),
                    ("id", "!=", record.id),
                ]
            )

            if existing:
                raise ValidationError(
                    "The category name must be unique among active records."
                )
