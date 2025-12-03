from odoo import fields, models


class PackagePlanLine(models.Model):
    _name = "package.plan.line"
    _description = "Package Plan Line"

    pack_id = fields.Many2one('package.plan', 'Package', readonly=True)
    seq_no = fields.Integer('#')
    pack_in = fields.Selection([
        ('box', 'Box'),
        ('bag', 'Bag'),
        ('sleeve', 'Sleeve'),
    ], 'Package Type')
    pack_in_no = fields.Integer('Pack-in No')
    qty_packed = fields.Integer('Qty Packed')
    is_skid = fields.Boolean("Skid")
    skid_number = fields.Integer('No')
    available_mtr_template_ids = fields.One2many('mtr.template', compute='_compute_pack_mtr_template_ids')
    mtr_template_ids = fields.Many2many(comodel_name="mtr.template", relation="mtr_template_package_plan_line_rel",
                                   column1="id", column2="name", string="MTR")
    
    def _compute_pack_mtr_template_ids(self):
        for record in self:
            record.available_mtr_template_ids = record.pack_id.mtr_template_ids
