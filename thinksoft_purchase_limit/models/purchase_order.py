from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_limit = fields.Monetary(related="user_id.purchase_limit")
    purchase_hold = fields.Boolean(string="On Hold", default=False, copy=False)

    def button_confirm(self):
        for order in self:
            if order.amount_total > order.purchase_limit:
                order.message_post(body="\u2022 Purchase Hold")
                order.write({"purchase_hold": True})
                return
            if order.amount_total <= order.purchase_limit:
                order.write({"purchase_hold": False})
        return super().button_confirm()
