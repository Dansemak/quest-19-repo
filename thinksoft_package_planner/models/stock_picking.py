from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def test_button_skid_label(self):
        # return self.env.ref( PLACE SKID REPORT HERE ).report_action(self)
        return

    def test_button_box_label(self):
        # return self.env.ref( PLACE BOX REPORT HERE ).report_action(self)
        return
    