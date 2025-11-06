from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    mobile = fields.Char(
        string="Mobile Phone", help="The mobile phone number of this contact"
    )
    fax = fields.Char(string="Fax", help="The fax number of this contact")

    outside_salesperson_id = fields.Many2one(
        "res.users",
        string="Outside Salesperson",
        help="The outside salesperson in charge of sales for this contact",
    )

    team_id = fields.Many2one(
        "crm.team",
        string="Sales Team",
        help="The sales team responsible for this contact",
    )

    display_name = fields.Char(compute="_compute_display_name", store=True)

    # formatting the partner_id fields (partner_invoice_id, partner_shipping_id)
    # without the parent_id in the string

    @api.depends("name", "type", "company_name", "parent_id", "email")
    @api.depends_context(
        "show_address_only", "show_address", "show_email", "html_format"
    )
    def _compute_display_name(self):
        for partner in self:
            name = partner.name or ""

            # Use label for address types if name is empty
            if (partner.company_name or partner.parent_id) and not name:
                if partner.type in ["invoice", "delivery", "other"]:
                    type_label = dict(
                        self.fields_get(["type"])["type"]["selection"]
                    ).get(partner.type)
                    name = type_label or ""

            # show_address_only context → show only the address
            if self._context.get("show_address_only"):
                name = partner._display_address(without_company=True)

            # show_address context → append address under the name
            elif self._context.get("show_address"):
                name += "\n" + partner._display_address(without_company=True)

            # clean up newlines
            name = name.replace("\n\n", "\n").replace("\n\n", "\n")

            # show_email context → add email to name
            if self._context.get("show_email") and partner.email:
                name = f"{name} <{partner.email}>"

            # html_format context → convert newlines to <br/>
            if self._context.get("html_format"):
                name = name.replace("\n", "<br/>")

            partner.display_name = name
