from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_coo_required = fields.Boolean(
        string="COO Required",
        help="Country of Origin required on products, request or required by customers",
    )
    partner_contact_id = fields.Many2one("res.partner", string="Contact")
    outside_salesperson_id = fields.Many2one(
        "res.users",
        string="Outside Salesperson",
        help="The outside salesperson in charge of sales for this contact",
    )
    comment_text = fields.Text(string="Comment")

    # outside salesperson assigned from the customer's outside_salesperson_id field
    @api.onchange("partner_id")
    def _onchange_outside_salesperson_id(self):
        for order in self:
            order.outside_salesperson_id = order.partner_id.outside_salesperson_id

    # partner_contacts are any contacts from the customer specifically
    @api.onchange("partner_id")
    def _onchange_partner_contact_id(self):
        contacts = self.env["res.partner"].search(
            [
                ("parent_id", "=", self.partner_id.id),
                ("type", "=", "contact"),
            ]
        )
        for order in self:
            order.partner_contact_id = contacts.ids
