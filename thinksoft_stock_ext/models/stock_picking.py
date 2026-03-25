from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    picking_type_sequence_code = fields.Char(related='picking_type_id.sequence_code')
    picker_id = fields.Many2one("hr.employee", string="Picker")
    packer_id = fields.Many2one("hr.employee", string="Packer")
    shipper_id = fields.Many2one("hr.employee", string="Shipper")
    waybill = fields.Char(string="Waybill")
    team_responsible = fields.Selection(
        [
            ('team_one', 'Team 1'),
            ('team_two', 'Team 2'),
            ('team_three', 'Team 3'),
            ('team_four', 'Team 4'),
            ('shared', 'Shared'),
        ],
        string='Team',
        copy=False,
    )

    client_order_ref = fields.Char(related="sale_id.client_order_ref")
    salesperson_id = fields.Many2one("res.users", related="sale_id.user_id", string="Salesperson")
    partner_customer_id = fields.Many2one("res.partner", related="sale_id.partner_id", string="Customer")
    box_qty = fields.Integer(string="Number of boxes", help="Number of boxes and skids", store=True)
    skid_qty = fields.Integer(string="Number of skids", store=True)

    # transfering packer_id, team_responsible, box_qty, and skid_qty data from transfer to transfer
    def _action_done(self):
        res = super()._action_done()

        for picking in self:
            next_pickings = picking.move_ids.move_dest_ids.picking_id

            if next_pickings:
                next_pickings.write({'packer_id': picking.packer_id})
                next_pickings.write({'team_responsible': picking.team_responsible})
                next_pickings.write({'box_qty': picking.box_qty})
                next_pickings.write({'skid_qty': picking.skid_qty})

        return res

