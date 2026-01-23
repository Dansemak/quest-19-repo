from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.addons.website.tools import text_from_html


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    note = fields.Text(compute="_compute_note") # the product description
    partner_id = fields.Many2one("res.partner", string="Customer", related='sale_line_id.order_id.partner_id')
    sale_id = fields.Many2one("sale.order", string="Sale Order", related='sale_line_id.order_id')
    client_order_ref = fields.Char(string="Customer Reference", related='sale_line_id.order_id.client_order_ref')
    department_id = fields.Many2one(related="bom_id.department_id", string="Department")

    # getting the product description
    @api.depends("product_id")
    def _compute_note(self):
        for production in self:
            if production.sale_line_id and not production.sale_line_id.name == production.product_id.name:
                production.note = production.sale_line_id.name
            else:
                production.note = text_from_html(production.product_id.description or "").strip()

    # prevent completing MO if pick components transfer is not done
    def button_mark_done(self):
        for order in self:
            if order.delivery_count:
                for picking_id in order.picking_ids:
                    if picking_id.state not in ['cancel', 'done']:
                        raise UserError("Please Complete the Transfers before Completing the Manufacturing Order.")
                    if picking_id.state == 'cancel' and order.delivery_count == 1:
                        raise UserError("Please Create and Complete a new Transfer to Replace the Canceled" 
                                          " Transfer before Completing the Manufacturing Order.")

        return super().button_mark_done()
