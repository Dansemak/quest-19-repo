from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    waybill = fields.Char(string="Waybill", compute="_compute_waybill")

    # getting the waybill data from the related sales orders', related stock pickings' waybill
    @api.depends("invoice_line_ids")
    def _compute_waybill(self):
        for move in self:
            waybills = []

            # getting all related sale orders from invoice lines
            sale_orders = move.invoice_line_ids.sale_line_ids.order_id

            # looking through all pickings from sales orders
            for order in sale_orders:
                # finding all the OUT pickings with waybills
                outgoing_pickings = order.picking_ids.filtered(
                    lambda p: p.picking_type_id.sequence_code == "OUT" and p.waybill
                )

                # getting all the waybills
                for picking in outgoing_pickings:
                    if picking.waybill and picking.waybill not in waybills:
                        waybills.append(picking.waybill)

            move.waybill = ", ".join(waybills) if waybills else False
