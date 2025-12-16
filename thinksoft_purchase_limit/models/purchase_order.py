from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_hold = fields.Boolean(string="On Hold", default=False, copy=False)

    def button_confirm(self):
        for order in self:
            if order.amount_total > self.env.user.purchase_limit:
                order.write({"purchase_hold": True})
                order.message_post(body="Purchase Hold")
                return
            if order.amount_total <= self.env.user.purchase_limit:
                order.write({"purchase_hold": False})
                order.message_post(body=f"Purchase Order Confirmed By: {self.env.user.name}")
        return super().button_confirm()
