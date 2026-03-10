from odoo import fields, models

class ProductCategory(models.Model):
    _inherit = 'product.category'

    min_margin_rate = fields.Float(
        string='Minimum Margin Rate (%)',
        help='Minimum margin percentage for products in this category.'
    )