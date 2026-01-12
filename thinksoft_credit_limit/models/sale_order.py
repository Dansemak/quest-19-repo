from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    credit_hold = fields.Boolean(string="Credit Hold", readonly=True, copy=False)
    approve_sale_order = fields.Boolean(string="Approve Sale Order", readonly=True, copy=False)

    def button_approve_sale_order(self):
        self.approve_sale_order = True
        self.message_post(body="\u2022 Sale Order Approved")
        return
    
    def action_confirm(self):
        if self.partner_credit_warning == '' or self.approve_sale_order:
            self.credit_hold = False
            return super().action_confirm()
        else:
            self.credit_hold = True
            self.message_post(body="\u2022 Credit Hold")
            return
