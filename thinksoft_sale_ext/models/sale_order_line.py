from odoo import api, fields, models
import logging

log = logging.getLogger(__name__).info

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _order = 'seq_no, id'

    seq_no = fields.Integer(
        string="#",
        compute="_compute_line_number",
        readonly=True,
        store=True
    )

    tagging = fields.Char(
        help="Customer Line Item Reference for custom identification or referencing of product in accordance to the customer"
    )

    string_availability_info = fields.Char(
        string="Availability",
        help="Estimated time when the product will be available from now (i.g 3-5 BUSINESS DAYS, 2 WEEKS, etc.)"
    )

    purchase_order_id = fields.Many2one(
        "purchase.order",
        string="PO Number"
    )

    weight = fields.Char(
        compute="_compute_weight"
    )

    total_weight = fields.Char(
        compute="_compute_weight"
    )

    min_margin_rate = fields.Float(
        related="product_id.categ_id.min_margin_rate",
        string="Min Margin (%)",
        store=True,
        readonly=True
    )

    min_sale_price = fields.Float(
        string="Min Sale Price",
        compute="_compute_min_margin",
        track=True
    )

    min_margin = fields.Float(
        string="Min Margin",
        compute="_compute_min_margin",
        help="Minimum margin percentage calculated based on the cost and minimum sale price. This is used to compare against the actual margin percentage to ensure that the sale price does not go below the minimum sale price.",
    )

    price_unit = fields.Float(
        help="This price is calculated based on the above price list"
    )

    list_price = fields.Float(
        string="List Price",
        related="product_id.list_price",
        help="List Price is the sale price on the product template"
    )

    @api.depends("product_id", "min_margin_rate")
    def _compute_min_margin(self):
        for line in self:
            cost = line.purchase_price
            rate = line.min_margin_rate or 0.0

            if rate and cost:
                line.min_sale_price = round(cost * (1 + rate), 2)
                line.min_margin = round((cost * (1 + rate) - cost), 2)
            else:
                line.min_sale_price = 0.0
                line.min_margin = 0.0


    # determining the line number of the sale.order.line record
    @api.depends("order_id", "order_id.order_line", "sequence")
    def _compute_line_number(self):
        for line in self:
            if line.order_id:
                # getting all of the lines in the order
                lines = line.order_id.order_line.filtered(lambda i: not i.display_type).sorted(key=lambda l: (l.sequence, l.id))

                # finding the position of this line and assigning its line number
                for i, o_l, in enumerate(lines, start=1):
                    if o_l == line:
                        line.seq_no = i * 10
                        break
            else:
                line.seq_no = 0

    # concatenating the weight and UoM
    @api.depends("product_id", "product_id.weight", "product_id.weight_uom_name")
    def _compute_weight(self):
        for line in self:
            line.weight = f"{line.product_id.weight} {line.product_id.weight_uom_name}"
            rounded_total = round((line.product_id.weight * line.product_uom_qty), 2)
            line.total_weight = f"{rounded_total} {line.product_id.weight_uom_name}"

    # setting the record string_availability_info in ALL CAPS; trimming string_availability_info and tagging
    @api.model
    def create(self, vals_list):
        if isinstance(vals_list, list):
            for vals in vals_list:
                if "string_availability_info" in vals and vals["string_availability_info"]:
                    vals["string_availability_info"] = vals["string_availability_info"].upper().strip()
                if "tagging" in vals and vals["tagging"]:
                    vals["tagging"] = vals["tagging"].strip()
        else:
            if "string_availability_info" in vals_list and vals_list["string_availability_info"]:
                vals_list["string_availability_info"] = vals_list["string_availability_info"].upper().strip()
            if "tagging" in vals_list and vals_list["tagging"]:
                vals_list["tagging"] = vals_list["tagging"].strip()

        return super().create(vals_list)

    # setting the string_availability_info to ALL CAPS for consistency sake; trimming end whitespace
    @api.onchange("string_availability_info")
    def _onchange_string_availability_info(self):
        for record in self:
            if record.string_availability_info:
                record.string_availability_info = record.string_availability_info.upper().strip()

    # trimming tagging whitespace on ends
    @api.onchange("tagging")
    def _onchange_tagging(self):
        for record in self:
            if record.tagging:
                record.tagging = record.tagging.strip()
