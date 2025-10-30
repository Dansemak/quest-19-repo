from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    mtr_template_ids = fields.Many2many(
        "mtr.template", "mtr_template_stock_move_line_rel", string="MTR"
    )

    def write(self, vals):
        if self.env.context.get("skip_mtr_sync"):
            return super().write(vals)

        res = super().write(vals)
        if "mtr_template_ids" in vals:
            for move_line in self:
                move = move_line.move_id
                if move:
                    move.with_context(skip_mtr_sync=True).write(
                        {"mtr_template_ids": [(6, 0, move_line.mtr_template_ids.ids)]}
                    )
        return res
