from odoo import _, api, fields, models


class NcrClaim(models.Model):
    _name = "ncr.claim"
    _inherit = ["mail.thread"]
    _description = "Non-Conformance Report"

    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed"), ("cancelled", "Cancelled")],
        string="State",
        default="open",
        tracking=True,
        copy=False,
        readonly=False,
    )
    name = fields.Char(
        string="Name",
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _("New"),
    )
    classification = fields.Selection(
        [("nc", "Non-Conformance"), ("find", "Finding")],
        string="Classification",
        required=True,
    )

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("ncr.claim") or _("New")
        return super(NcrClaim, self).create(vals)
