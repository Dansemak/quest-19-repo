from odoo import fields, models


class package_planner_line(models.Model):
    _name = "package.planner.line"
    _description = "Package Planner Line"

    pack_id = fields.Many2one('package.line', 'Package', readonly=True, )
    seq_no = fields.Integer('#')
    pack_in = fields.Selection([
        ('box', 'Box'),
        ('bag', 'Bag'),
        ('sleeve', 'Sleeve'),
    ], 'Package Type')
    pack_in_no = fields.Integer('Pack-in No')
    qty_packed = fields.Integer('Qty Packed')
    crate_skid = fields.Selection([
        ('skid', 'Skid'),
        ('crate', 'Crate'),
    ], 'Crate/Skid')
    no = fields.Integer('No')
    # Heat field will need to be removed, since mtr_tag_ids will be used instead.
    heat = fields.Char('Archived Heat#', size=20, readonly=True)
    available_mtr_tag_ids = fields.One2many('mtr.template', compute='_compute_pack_mtr_tag_ids')
    mtr_tag_ids = fields.Many2many(comodel_name="mtr.template", relation="mtr_template_package_planner_line_rel",
                                   column1="id", column2="name", string="MTR")
    
    def _compute_pack_mtr_tag_ids(self):
        for record in self:
            record.available_mtr_tag_ids = record.pack_id.mtr_tag_ids
