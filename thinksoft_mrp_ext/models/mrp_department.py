from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MrpDepartment(models.Model):
    _name = "mrp.department"
    _description = "Manufacturing Department"

    name = fields.Char("Department")
    active = fields.Boolean(default=True)

    _unique_mrp_department_name = models.Constraint(
        "UNIQUE(name)",
        "The manufacturing department name must be unique.",
    )

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
                        "The department name must be unique among active records."
                    )
