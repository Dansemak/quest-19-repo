from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _order = 'seq_no, id'

    seq_no = fields.Integer(string="#", compute="_compute_line_number", readonly=True, store=True)
    tagging = fields.Char(help="Customer Line Item Reference for custom identification or referencing of product in accordance to the customer")
    string_availability_info = fields.Char(string="Availability", help="Estimated time when the product will be available from now (i.g 3-5 BUSINESS DAYS, 2 WEEKS, etc.)")
    purchase_order_id = fields.Many2one("purchase.order", string="PO Number")
    weight = fields.Char(compute="_compute_weight")

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
