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

    # Order Details fields
    classification = fields.Selection(
        [("nc", "Non-Conformance"), ("find", "Finding")],
        string="Classification",
        required=True,
    )
    issue_type = fields.Selection(
        [
            ("vendor", "Vendor"),
            ("customer", "Customer"),
            ("internal", "Internal"),
            ("opp_imp", "Opportunity for Improvement"),
            ("audit", "Audit"),
        ],
        string="Issue Type",
        required=True,
    )
    sale_order_id = fields.Many2one(
        "sale.order",
        string="Sale Order",
        help="Sale order related to this NCR, if applicable.",
    )
    purchase_order_id = fields.Many2one(
        "purchase.order",
        string="Purchase Order",
        help="Purchase order related to this NCR, if applicable.",
    )

    # NCR Details fields
    date = fields.Date(string="Date")
    resolved_by = fields.Many2one(
        "res.users", string="Resolved By", help="User who resolved the NCR."
    )
    responsible_id = fields.Many2one("hr.employee", string="Responsible For Error")
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major"), ("critical", "Critical")],
        string="Severity",
    )
    cost_impact = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")], string="Cost Impact"
    )
    resolution_lead_time = fields.Selection(
        [
            ("same_day", "Same Day"),
            ("next_day", "Next Day"),
            ("over_two_days", "Over 2 Days"),
            ("cancelled", "Cancelled"),
        ],
        string="Resolution Lead Time",
    )

    # Category fields
    category_source_id = fields.Many2one("ncr.category", string="Source")
    category_department_id = fields.Many2one("ncr.category", string="Department")
    category_section_id = fields.Many2one("ncr.category", string="Section")
    category_issue_id = fields.Many2one("ncr.category", string="Issue")

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("ncr.claim") or _("New")
        return super(NcrClaim, self).create(vals)

    @api.onchange("category_source_id", "category_department_id", "category_section_id")
    def _onchange_category_fields(self):
        if self.category_department_id.parent_category_id != self.category_source_id:
            self.category_department_id = None
            self.category_section_id = None
            self.category_issue_id = None

        elif self.category_section_id.parent_category_id != self.category_department_id:
            self.category_section_id = None
            self.category_issue_id = None

        elif self.category_issue_id.parent_category_id != self.category_section_id:
            self.category_issue_id = None

    def button_close(self):
        self.write({"state": "closed"})

    def button_cancel(self):
        self.write({"state": "cancelled"})

    def button_reopen(self):
        self.write({"state": "open"})
