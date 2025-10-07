from odoo import _, api, fields, models


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

    # shipping fields for display

    customer_account_info = fields.Char(
        string="Customer Account Information",
        help="Any related customer account info regarding shipping (e.g. account number)",
        readonly=True,
    )
    freight_charge = fields.Many2one(
        "sale.freight",
        string="Freight Charge",
        help="Where and how the freight is being charged",
        readonly=True,
    )
    cut_off = fields.Float(
        string="Cut Off",
        help="The time of day when the shipping cutoff occurs, in hours (0-24).",
        readonly=True,
    )

    # outside salesperson assigned from the customer's outside_salesperson_id field
    # customer account information assigned from the customer's customer_account_info field
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
            order.customer_account_info = order.partner_id.customer_account_info
            order.outside_salesperson_id = order.partner_id.outside_salesperson_id

    # opens the delivery wizard; replacing the name field
    def action_open_delivery_wizard(self):
        self.ensure_one()
        view_id = self.env.ref('delivery.choose_delivery_carrier_view_form').id
        return {
            'name': _('Apply Shipping Info'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.carrier',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_carrier_id': self.carrier_id.id if self.carrier_id else False,
                'default_total_weight': self._get_estimated_weight(),
                'default_freight_charge': self.freight_charge,
                'default_customer_account_info': self.customer_account_info,
                'default_cut_off': self.cut_off,
            }
        }