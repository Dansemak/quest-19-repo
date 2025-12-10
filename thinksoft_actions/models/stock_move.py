from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def action_print_label(self):
        return self.env.ref("thinksoft_labels.4x4_label").report_action(self)
