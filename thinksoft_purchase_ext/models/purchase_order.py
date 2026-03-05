from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    date_ship = fields.Datetime(
        string="Ship Date",
        help="The date in which the vendor must ship the products by.",
    )

    carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Carrier",
        check_company=True,
    )
