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

    @api.onchange("partner_id", "partner_shipping_id")
    def _onchange_partner_id(self):
        """
        outside salesperson assigned from the customer's outside_salesperson_id field
        customer account information assigned from the customer"s customer_account_info field
        partner_contacts are any contacts from the customer specifically
        """
        contacts = self.env["res.partner"].search(
            [
                ("parent_id", "=", self.partner_id.id),
                ("type", "=", "contact"),
            ]
        )
        for order in self:
            order.partner_contact_id = contacts.ids
            order.outside_salesperson_id = order.partner_shipping_id.outside_salesperson_id

    @api.onchange("partner_shipping_id")
    def _onchange_partner_shipping_id(self):
        """
        team_id assigned to the partner's shipping address sales team
        """
        for order in self:
            order.team_id = order.partner_shipping_id.team_id

    def write(self, values):
        """
        This is to override the built-in set 'date_deadline' to 'commitment_date'. Here
        is the link: https://github.com/odoo/odoo/blob/19.0/addons/sale_stock/models/sale_order.py#L173
        (The line the link points to may move over time).

        All we're doing is removing the filter in the lambda so that the 'date_deadline'
        on the PICK can also be updated when the 'commitment_date' is changed on the
        sale order.
        """
        res = super().write(values)
        if 'commitment_date' in values:
            deadline_datetime = values.get('commitment_date')
            for order in self:
                moves = order.order_line.move_ids.filtered(
                    lambda m: m.state not in ('done', 'cancel')
                )
                productions = order.mrp_production_ids.filtered(lambda m: m.state not in ('done', 'cancel'))
                moves.date_deadline = deadline_datetime or order.expected_date
                productions.date_deadline = deadline_datetime or order.expected_date
        return res
