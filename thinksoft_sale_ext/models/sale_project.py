import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleProject(models.Model):
    _name = "sale.project"
    _description = "Project"

    name = fields.Char(string="Project")
    active = fields.Boolean(default=True)

    _unique_sale_project_name = models.Constraint(
        "UNIQUE(name)",
        "The Sale Project name should be unique!",
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
                        "The sale project name must be unique among active records."
                    )
