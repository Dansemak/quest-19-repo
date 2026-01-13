# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _

log = logging.getLogger(__name__).info


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    rma_id = fields.Many2one('rma.main', 'RMA Id')
    rma_count = fields.Integer(
        string="RMA",
        store=True
    )

    # def _compute_rma_count(self):
    #     for order in self:
    #         rma_count = self.env['rma.main'].search_count(
    #             [('sale_order', '=', order.id)]
    #         )
    #         order.rma_count = rma_count

    def action_view_rma_orders(self):
        rma_ids = self.env['rma.main'].search([('sale_order', 'in', [165,])]).ids
        log("====================================================")
        log("RMA IDS:", rma_ids)

        return {
            "name": "RMA Orders",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "rma.main",
            "domain": [("id", "in", rma_ids)],
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    return_order_line_id = fields.One2many('rma.lines', 'sale_line_id')

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    rma_line_id = fields.Many2one('rma.lines')
    stock_move_id = fields.Many2one('stock.move')

class AccountMove(models.Model):
    _inherit = 'account.move'

    rma_id = fields.Many2one('rma.lines', 'RMA Id.')
    picking_id = fields.Many2one('stock.picking','Picking')
    sale_id  =  fields.Many2one('sale.order', 'Sale Origin')
    rma_id = fields.Many2one('rma.main', 'RMA Id')
