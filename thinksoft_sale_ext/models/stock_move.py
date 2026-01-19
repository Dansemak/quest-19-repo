from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    # adding relational fields to stock.picking in the thinksoft_sale_ext module
    # to avoid hard dependancies between extension modules

    tagging = fields.Char(
        help="Customer Line Item Reference for custom identification",
        readonly=True,
        related="sale_line_id.tagging"
    )
    purchase_order_id = fields.Many2one(related="sale_line_id.purchase_order_id", string="PO Number")


    @api.depends('product_id', 'picking_type_id', 'description_picking_manual', 'sale_line_id')
    def _compute_description_picking(self):
        for move in self:
            # adding this line so that it pulls from the sales line first before the rest
            if move.sale_line_id:
                move.description_picking = move.sale_line_id.name
            elif move.description_picking_manual:
                move.description_picking = move.description_picking_manual
            elif move.product_id:
                product = move.product_id.with_context(lang=move._get_lang())
                move.description_picking = product._get_picking_description(move.picking_type_id) or move._get_description()
            else:
                move.description_picking = ""