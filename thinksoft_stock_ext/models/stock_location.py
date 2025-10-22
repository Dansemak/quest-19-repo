from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    is_inventory_admin = fields.Boolean(
        string="Is Inventory Config Admin",
        default=False,
        compute="_compute_is_inventory_admin",
    )

    def _compute_is_inventory_admin(self):
        for location in self:
            location.is_inventory_admin = self.env.user.has_group(
                "thinksoft_stock_ext.group_inventory_config_admin"
            )
