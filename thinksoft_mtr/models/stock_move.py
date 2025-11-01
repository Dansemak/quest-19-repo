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
