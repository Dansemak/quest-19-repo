from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tagging = fields.Char(help="Customer Line Item Reference for custom identification or referencing of product in accordance to the customer")
