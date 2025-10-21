from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # adding relational fields to stock.picking in the thinksoft_sale_ext module
    # to avoid hard dependancies between extension modules

    is_coo_required = fields.Boolean(related="sale_id.is_coo_required", readonly=True)
    sale_note_id = fields.Many2one(
        "sale.note",
        string="Note",
        help="Important notes relating to the PICK, PACK, and OUT",
        readonly=True,
        related='sale_id.sale_note_id'
    )
    comment_text = fields.Text(
        string="Comment",
        help="Specific comments relating to the Note and the PICK, PACK, and OUT",
        readonly=True,
        related="sale_id.comment_text"
    )
    sale_freight_id = fields.Many2one(
        "sale.freight",
        string="Freight Charge",
        help="Where and how the freight is being charged",
        readonly=True,
        related="sale_id.sale_freight_id"
    )
    cut_off = fields.Float(
        related="carrier_id.cut_off",
        string="Cut Off",
        help="The time of day when the shipping cutoff occurs, in hours (0-24).",
    )
    picking_type_sequence_code = fields.Char(related='picking_type_id.sequence_code')

    # check that the country of origin is on the product if COO is required
    def button_validate(self):
        if self.picking_type_id.code == "outgoing" and self.is_coo_required:
            missing_coo_products = self.move_ids.filtered(
                lambda m: not m.product_id.country_of_origin
                and m.product_id.type == "consu"
            )

            if missing_coo_products:
                product_names = ", ".join(
                    missing_coo_products.mapped("product_id.display_name")
                )
                raise UserError(
                    _(
                        f"Country Of Origin is required for the following products:\n\n{product_names}\n\n"
                        "Country Of Origin must be filled out on all line items before this order can be validated."
                    )
                )

        return super().button_validate()
