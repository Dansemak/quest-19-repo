from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleNote(models.Model):
    _name = "sale.note"
    _description = "Sale Note"

    name = fields.Char("Note", required=True)
    active = fields.Boolean(default=True)

    _unique_sale_note_name = models.Constraint(
        "UNIQUE(name)",
        "The sale note name must be unique.",
    )

    # setting the record name in ALL CAPS
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

    # setting the record name in ALL CAPS when there are any changes
    @api.onchange("name")
    def _onchange_name(self):
        for record in self:
            if record.name:
                record.name = record.name.upper()

    # adding python level constraint
    @api.constrains("name", "active")
    def _check_unique_active_name(self):
        for record in self:
            if record.active:
                existing = self.search_count(
                    [
                        ("name", "=", record.name),
                        ("active", "=", True),
                        ("id", "!=", record.id),
                    ]
                )

                if existing:
                    raise ValidationError(
                        "The note name must be unique among active records."
                    )
