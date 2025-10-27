from odoo import api, fields, models
from odoo.exceptions import ValidationError


class jobProject(models.Model):
    _name = "job.project"
    _description = "Job Project"

    name = fields.Char(string="Job Project")
    active = fields.Boolean(default=True)

    _unique_job_project_name = models.Constraint(
        "UNIQUE(name)",
        "The Job Project name should be unique!",
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
                        "The job project name must be unique among active records."
                    )
