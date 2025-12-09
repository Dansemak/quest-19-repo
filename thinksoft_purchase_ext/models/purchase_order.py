from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Carrier",
        check_company=True,
    )
