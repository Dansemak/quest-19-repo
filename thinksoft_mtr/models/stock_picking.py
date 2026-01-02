from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    mtr_move_ids = fields.One2many(
        "stock.move", "picking_id", string="MTR Stock Moves", copy=True
    )

    def action_print_all_mtrs(self):
        mtr_ids = set()  # Use a set to avoid duplicates
        for line in self.mtr_move_ids:
            if line.mtr_template_ids:
                for mtr in line.mtr_template_ids:
                    mtr_ids.add(mtr.id)
        
        if mtr_ids:
            return self.env.ref('thinksoft_mtr.action_report_mtr').report_action(list(mtr_ids))
        
        return
