from odoo import models


class AccountBatchPayment(models.Model):
    _inherit = "account.batch.payment"

    # resets sent batch payments to draft + unmarks payments that are sent
    def reset_draft(self):
        if self.state == "sent":
            self.write({"state": "draft"})
            self.payment_ids.unmark_as_sent()
