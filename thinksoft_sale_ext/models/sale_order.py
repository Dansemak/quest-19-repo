from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_coo_required = fields.Boolean(
        string="COO Required",
        help="Country of Origin required on products, requested or required by customer",
    )
    partner_contact_id = fields.Many2one("res.partner", string="Contact")
    outside_salesperson_id = fields.Many2one(
        "res.users",
        string="Outside Salesperson",
        help="The outside salesperson in charge of sales for this contact",
    )
    sale_freight_id = fields.Many2one(
        "sale.freight",
        string="Freight Charge",
        help="Where and how the freight is being charged",
    )
    sale_note_id = fields.Many2one(
        "sale.note",
        string="Note",
        help="Important notes relating to the PICK, PACK, and OUT",
    )
    comment_text = fields.Text(
        string="Comment",
        help="Specific comments relating to the Note and the PICK, PACK, and OUT",
    )
    customer_end_user_id = fields.Many2one(
        "company.user",
        string="End User",
        help="The user/company/project at the end of the sales flow that will inevitably receive these products",
    )
    carrier_cut_off = fields.Float(related="carrier_id.cut_off")

    # outside salesperson assigned from the customer"s outside_salesperson_id field
    # customer account information assigned from the customer"s customer_account_info field
    # partner_contacts are any contacts from the customer specifically
    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        contacts = self.env["res.partner"].search(
            [
                ("parent_id", "=", self.partner_id.id),
                ("type", "=", "contact"),
            ]
        )
        for order in self:
            order.partner_contact_id = contacts.ids
            order.outside_salesperson_id = order.partner_id.outside_salesperson_id
<<<<<<< HEAD
=======

    # team_id assigned to the partner's shipping address sales team
    @api.onchange("partner_shipping_id")
    def _onchange_partner_shipping_id(self):
        for order in self:
            order.team_id = order.partner_shipping_id.team_id
>>>>>>> thinksoft/main
