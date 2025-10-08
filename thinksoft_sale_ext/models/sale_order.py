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
    freight_charge = fields.Many2one(
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
    end_user_id = fields.Many2one(
        "end.user",
        string="End User",
        help="The user/company/project at the end of the sales flow that will inevitably receive these products",
    )
    job_project_id = fields.Many2one(
        "job.project",
        string="Job Project",
        help="The name of the partner's project",
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
            order.outside_salesperson_id = order.partner_id.outside_salesperson_id
