import logging
from odoo import fields, models, api, _

log = logging.getLogger(__name__).info


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    rma_id = fields.Many2one('rma.main', 'RMA Id', copy=False)

    rma_count = fields.Integer(
        string="RMA",
        copy=False,
        compute='_compute_rma_count'
    )

    cr_note_count = fields.Integer(
        string="Credit Notes",
        copy=False,
        compute = '_compute_credit_note_count'
    )

    def _compute_rma_count(self):
        for order in self:
            rma_ids = self.env['rma.main'].search([('sale_order', '=', order.id)])
            order.rma_count = len(rma_ids)

    def _compute_credit_note_count(self):
        for order in self:
            refunds_ids = self.env['account.move'].search([('sale_id', '=',order.id), ('move_type', '=', 'out_refund')])
            order.cr_note_count = len(refunds_ids)

    def action_view_rma_orders(self):
        """This function displays the list view of all the RMAs related to the current Sale Order.

        Returns:
            _type_: View
        """
        rma_ids = self.env['rma.main'].search([('sale_order', '=', self.id)]).ids

        return {
            "name": "RMA Orders",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "rma.main",
            "domain": [("id", "in", rma_ids)],
        }

    def action_view_credit_notes(self):
        """This function displays the list view of all the Credit Notes related to the current Sale Order.

        Returns:
            _type_: View
        """
        credit_note_ids = self.env['account.move'].search(
            [('sale_id', '=', self.id), ('move_type', '=', 'out_refund')]).ids

        return {
            "name": "Credit Notes",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "account.move",
            "domain": [("id", "in", credit_note_ids)],
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
