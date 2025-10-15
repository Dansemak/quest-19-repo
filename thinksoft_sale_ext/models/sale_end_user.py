import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleEndUser(models.Model):
    _name = "sale.end.user"
    _description = "End User"

    name = fields.Char(string="End User")
    active = fields.Boolean(default=True)

    _unique_sale_end_user_name = models.Constraint(
        "UNIQUE(name)",
        "The End User should be unique!",
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
                        "The end user must be unique among active records."
                    )
