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