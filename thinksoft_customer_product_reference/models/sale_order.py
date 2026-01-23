from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    part_number = fields.Char(compute="_compute_part_number")

    # @api.depends("product_id")
    # def _compute_part_number(self):
    #     for line in self:
    #         partner_id = line.order_id.partner_id
    #         customer_line = line.product_id.customer_part_ids.filtered(
    #             lambda l: l.partner_id == partner_id
    #         )
    #         line.part_number = customer_line and customer_line[0].part_number or ""
