from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    mtr_template_ids = fields.Many2many(
        "mtr.template", "mtr_template_stock_move_rel", string="MTR"
    )

    def write(self, vals):
        res = super().write(vals)
        if "mtr_template_ids" in vals:
            for move in self:
                mtr_ids = move.mtr_template_ids.ids
                if move.move_line_ids:
                    move.move_line_ids.with_context(skip_mtr_sync=True).write(
                        {"mtr_template_ids": [(6, 0, mtr_ids)]}
                    )
        return res
    
    def button_pull_from_mo(self):
        for move in self:
            if move.created_production_id:
                mtr_ids = []
                mo_pick_ids = move.created_production_id.picking_ids

                for mo_pick in mo_pick_ids:
                    for mo_pick_move in mo_pick.move_ids:
                        mtr_ids.extend(mo_pick_move.mtr_template_ids.ids)
                        
                move.mtr_template_ids = [(6, 0, list(set(mtr_ids)))]

    def action_print_mtrs(self):
        if self.mtr_template_ids:
            return self.env.ref('thinksoft_mtr.action_report_mtr').report_action(self.mtr_template_ids)
        return
