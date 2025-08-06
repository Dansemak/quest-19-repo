from odoo import fields, models


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
