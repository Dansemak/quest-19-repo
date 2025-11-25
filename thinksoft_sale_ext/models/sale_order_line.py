from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _order = 'seq_no, id'

    seq_no = fields.Integer(string="#", compute="_compute_line_number", readonly=True, store=True)
    tagging = fields.Char(help="Customer Line Item Reference for custom identification or referencing of product in accordance to the customer")
    purchase_order_id = fields.Many2one("purchase.order", string="PO Number")

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
