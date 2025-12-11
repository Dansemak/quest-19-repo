from odoo import fields, models


class PackagePlanLine(models.Model):
    _name = "package.plan.line"
    _description = "Package Plan Line"

    package_plan_id = fields.Many2one('package.plan', 'Package', readonly=True)
    seq_no = fields.Integer('#')
    package_type = fields.Selection([
        ('box', 'Box'),
        ('sleeve', 'Sleeve'),
    ], 'Package Type')
    in_box = fields.Integer('In Box')
    packed_qty = fields.Integer('Packed Qty')
    is_skid = fields.Boolean("Skid")
    skid_number = fields.Integer('On Skid #')
