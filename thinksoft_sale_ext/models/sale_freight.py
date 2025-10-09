import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleFreight(models.Model):
    _name = "sale.freight"
    _description = "Sale Freight"

    name = fields.Char()
    active = fields.Boolean(default=True)

    _unique_sale_freight_name = models.Constraint(
        "UNIQUE(name)",
        "The frieght charge name must be unique.",
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

    # adding "(COPY)" or "(COPY)(n)" to duplicates of a sale.ship record
    def _get_unique_name_copy(self, original_name):
        # the first copy and every other copy
        copied_once = re.search(r"\s+\(COPY\)$", original_name)
        copied_more_than_once = re.search(r"\s+\(COPY\)(?:\((\d+)\))?$", original_name)

        # return first copied name
        if not copied_once and not copied_more_than_once:
            return f"{original_name} (COPY)"

        # the base name (without the "(COPY)" or "(COPY)(n)")
        base_name = re.sub(
            r"\s+\(COPY\)(?:\((\d+)\))?$", "", original_name, flags=re.IGNORECASE
        )

        # return second copied name
        if copied_once:
            return f"{base_name} (COPY)(2)"

        # getting the number from the first group '(copy)(n)'for every copy after the second
        number = int(copied_more_than_once.group(1))

        return f"{base_name} (COPY)({number + 1})"

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if "name" not in default:
            default["name"] = self._get_unique_name_copy(self.name)
        return super().copy(default)

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
                        "The freight charge name must be unique among active records."
                    )
