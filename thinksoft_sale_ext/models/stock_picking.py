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
        related="sale_id.sale_note_id",
    )
    comment_text = fields.Text(
        string="Comment",
        help="Specific comments relating to the Note and the PICK, PACK, and OUT",
        readonly=True,
        related="sale_id.comment_text",
    )
    sale_freight_id = fields.Many2one(
        "sale.freight",
        string="Freight Charge",
        help="Where and how the freight is being charged",
        readonly=True,
        compute="_compute_order_fields",
        store=True,
    )
    cut_off = fields.Float(
        related="carrier_id.cut_off",
        string="Cut Off",
        help="The time of day when the shipping cutoff occurs, in hours (0-24).",
    )
    carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Shipping Method",
        domain="[('id', 'in', allowed_carrier_ids)]",
        check_company=True,
        store=True,
        compute="_compute_order_fields",
    )
    picking_type_sequence_code = fields.Char(related="picking_type_id.sequence_code")
    partner_contact_id = fields.Many2one("res.partner", compute="_compute_order_fields", string="Contact", store=True)

    # sets fields to related fields from sale.order or purchase.order
    @api.depends(
        "sale_id.partner_contact_id",
        "purchase_id.partner_contact_id",
        "sale_id.sale_freight_id",
        "purchase_id.sale_freight_id",
        "sale_id.carrier_id",
        "purchase_id.carrier_id",
    )
    def _compute_order_fields(self):
        for picking in self:
            picking.partner_contact_id = picking.sale_id.partner_contact_id or picking.purchase_id.partner_contact_id
            picking.sale_freight_id = picking.sale_id.sale_freight_id or picking.purchase_id.sale_freight_id
            picking.carrier_id = picking.sale_id.carrier_id or picking.purchase_id.carrier_id

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
