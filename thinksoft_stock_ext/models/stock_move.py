from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    seq_no = fields.Integer(string="#", compute="_compute_line_number", readonly=True, store=True)
    unit_weight = fields.Float(related="product_id.weight", help="The weight of each product", string="Weight")
    weight_uom = fields.Char(related="product_id.weight_uom_name", help="the weight unit of measure", string="Unit")
    subtotal_weight = fields.Float(compute="_compute_subtotal_weight", help="The weight of the all the products by quanity", string="Total Weight")
    country_of_origin = fields.Many2one('res.country', related='product_id.country_of_origin', readonly=True)
    hs_code = fields.Char(related="product_id.hs_code")

    # determining the line number of the stock.move record
    @api.depends("picking_id", "picking_id.move_ids", "sequence")
    def _compute_line_number(self):
        for move in self:
            if move.picking_id:
                # getting all the moves in the picking
                moves = move.picking_id.move_ids.sorted(key=lambda m: (m.sequence, m.id))

                # finding the position of this move and assigning its line number
                for i, o_l, in enumerate(moves, start=1):
                    if o_l == move:
                        move.seq_no = i * 10
                        break
            else:
                move.seq_no = 0

    def _compute_subtotal_weight(self):
        for move in self:
            move.subtotal_weight = move.unit_weight * move.product_qty