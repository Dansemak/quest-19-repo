from odoo import api, fields, models


class MtrTemplate(models.Model):
    _name = "mtr.template"
    _inherit = ["mail.thread"]
    _description = "MTR"

    active = fields.Boolean(default=True, tracking=True)
    name = fields.Char("Name", readonly=True)
    category = fields.Selection(
        [
            ("bar", "BAR"),
            ("stud", "STUD"),
            ("nut", "NUT"),
            ("rtj", "RTJ"),
        ],
        string="Category",
        copy=False,
        index=True,
        required=True,
    )
    heat_number = fields.Char("Heat Number", required=True, index=True)
    product_id = fields.Many2one(
        "product.product", required=True, string="Product", tracking=True
    )

    description = fields.Char("Description")
    dimension = fields.Char("Dimension")
    diameter = fields.Char("Diameter")
    length = fields.Char("Length")
    product_type = fields.Char("Type")
    country_of_origin = fields.Char("Country Of Origin")
    manufacturer_id = fields.Char("Manufacturer ID")
    standard = fields.Char("Standard")
    material = fields.Char("Material")
    marking = fields.Char("Marking")
    lot_batch_number = fields.Char("Lot/Batch Number")
    reference = fields.Char("Reference")
    year = fields.Char("Year")
    test_date = fields.Char("Test Date")
    certificate_number = fields.Char("Certificate Number")
    supplier_certificate = fields.Char("Supplier Certificate")
    macroetch = fields.Char("Macroetch")
    dimensional_inspection = fields.Char("Dimensional Inspection")
    visual_inspection = fields.Char("Visual Inspection")
    nace_value = fields.Char("Nace")
    three_digit_traceability = fields.Char("3 Digit Traceability")
    po_number = fields.Char("PO Number")

    # Physical Properties
    tensile_strength_requirement = fields.Char("Tensile Strength Requirement")
    tensile_strength_value = fields.Char("Tensile Strength Value")
    yield_strength_requirement = fields.Char("Yield Strength Requirement")
    yield_strength_value = fields.Char("Yield Strength Value")
    elongation_requirement = fields.Char("Elongation Requirement")
    elongation_value = fields.Char("Elongation Value")
    reduction_requirement = fields.Char("Reduction Requirement")
    reduction_value = fields.Char("Reduction Value")
    tempering_requirement = fields.Char("Tempering Requirement")
    tempering_value = fields.Char("Tempering Value")
    quenching_requirement = fields.Char("Quenching Requirement")
    quenching_value = fields.Char("Quenching Value")
    charpy_requirement = fields.Char("Charpy Requirement")
    charpy_value = fields.Char("Charpy Value")
    hardness_requirement = fields.Char("Hardness Requirement")
    hardness_value = fields.Char("Hardness Value")
    heat_treatment_requirement = fields.Char("Heat Treatment Requirement")
    heat_treatment_value = fields.Char("Heat Treatment Value")
    sample_nut_hardness_requirement = fields.Char("Sample NUT Hardness Requirement")
    sample_nut_hardness_value = fields.Char("Sample NUT Hardness Value")
    completed_nut_hardness_requirement = fields.Char("Completed NUT Hardness Requirement")
    completed_nut_hardness_value = fields.Char("Completed NUT Hardness Value")
    proof_load_requirement = fields.Char("Proof Load Requirement")
    proof_load_value = fields.Char("Proof Load Value")

    # Chemical Analysis
    carbon_requirement = fields.Char("Carbon (C) Requriement")
    carbon_value = fields.Char("Carbon (C) Value")
    silicon_requirement = fields.Char("Silicon (Si) Requirement")
    silicon_value = fields.Char("Silicon (Si) Value")
    manganese_requirement = fields.Char("Manganese (Mn) Requirement")
    manganese_value = fields.Char("Manganese (Mn) Value")
    phosphorus_requirement = fields.Char("Phosphorus (P) Requirement")
    phosphorus_value = fields.Char("Phosphorus (P) Value")
    sulfur_requirement = fields.Char("Sulfur (S) Requirement")
    sulfur_value = fields.Char("Sulfur (S) Value")
    chromium_requirement = fields.Char("Chromium (Cr)% Requirement")
    chromium_value = fields.Char("Chromium (Cr)% Value")
    molybdenum_requirement = fields.Char("Molybdenum (Mo)% Requirement")
    molybdenum_value = fields.Char("Molybdenum (Mo)% Value")
    nickel_requirement = fields.Char("Nickel (Ni)% Requirement")
    nickel_value = fields.Char("Nickel (Ni)% Value")
    vanadium_requirement = fields.Char("Vanadium (V) Requirement")
    vanadium_value = fields.Char("Vanadium (V) Value")
    aluminium_requirement = fields.Char("Aluminium (Al) Requirement")
    aluminium_value = fields.Char("Aluminium (Al) Value")
    nitrogen_requirement = fields.Char("Nitrogen (N)% Requirement")
    nitrogen_value = fields.Char("Nitrogen (N)% Value")

    @api.model_create_multi
    def create(self, vals_list):
        mtrs = super().create(vals_list)
        for mtr in mtrs:
            mtr.name = f"{mtr.product_id.name}-{mtr.heat_number}-{self.env['ir.sequence'].next_by_code('mtr.template')}"
        return mtrs
