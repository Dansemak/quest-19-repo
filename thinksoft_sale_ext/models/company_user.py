from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CompanyUser(models.Model):
    _name = "company.user"
    _description = "Company User"

    name = fields.Char(string="Company User")
    active = fields.Boolean(default=True)

    _unique_company_user_name = models.Constraint(
        "UNIQUE(name)",
        "The Company User should be unique!",
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
                        "The company user must be unique among active records."
                    )
