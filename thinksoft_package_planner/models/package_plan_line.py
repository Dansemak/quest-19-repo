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
    qty_packed = fields.Integer('Qty Packed')
    is_skid = fields.Boolean("Skid")
    skid_number = fields.Integer('Skid #')
    available_mtr_template_ids = fields.One2many('mtr.template', compute='_compute_pack_mtr_template_ids')
    mtr_template_ids = fields.Many2many(comodel_name="mtr.template", relation="mtr_template_package_plan_line_rel",
                                   column1="id", column2="name", string="MTR")
    
    def _compute_pack_mtr_template_ids(self):
        for record in self:
            record.available_mtr_template_ids = record.package_plan_id.mtr_template_ids
