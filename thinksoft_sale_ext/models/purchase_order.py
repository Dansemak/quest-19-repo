from odoo import api, models, fields

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    partner_contact_id = fields.Many2one("res.partner", string="Vendor Contact")
    sale_freight_id = fields.Many2one(
        "sale.freight",
        string="Freight Charge",
        help="Where and how the freight is being charged",
    )