from odoo import models, fields, api
from odoo.addons.website.tools import text_from_html


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    note = fields.Text(compute="_compute_note") # the production description
    partner_id = fields.Many2one("res.partner", string="Customer", related='sale_line_id.order_id.partner_id')
    sale_id = fields.Many2one("sale.order", string="Sale Order", related='sale_line_id.order_id')
    client_order_ref = fields.Char(string="Customer Reference", related='sale_line_id.order_id.client_order_ref')

    # getting the product description
    @api.depends("product_id")
    def _compute_note(self):
        for production in self:
            production.note = text_from_html(production.product_id.description or "").strip()

