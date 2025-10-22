from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    mtr_template_ids = fields.Many2many(
        "mtr.template", "mtr_template_stock_move_line_rel", string="MTR"
    )

    def write(self, vals):
        res = super().write(vals)
        if "mtr_template_ids" in vals:
            for move_line in self:
                move_line.move_id.mtr_template_ids = move_line.mtr_template_ids
        return res
