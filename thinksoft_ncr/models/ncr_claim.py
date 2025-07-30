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
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
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

    # Customer/Vendor Details fields
    partner_source = fields.Selection(
        [("customer", "Customer"), ("vendor", "Vendor")], string="Source"
    )
    partner_id = fields.Many2one("res.partner", string="Customer/Vendor")
    partner_shipping_id = fields.Many2one("res.partner", string="Delivery Address")

    # Category fields
    category_source_id = fields.Many2one("ncr.category", string="Source")
    category_department_id = fields.Many2one("ncr.category", string="Department")
    category_section_id = fields.Many2one("ncr.category", string="Section")
    category_issue_id = fields.Many2one("ncr.category", string="Issue")

    # Products
    is_pull_button_clicked = fields.Boolean(default=False)
    product_line = fields.One2many(
        comodel_name="ncr.product_line", inverse_name="ncr_claim_id", string="Products"
    )
    amount_total = fields.Monetary(
        string="Total", store=True, readonly=True, compute="_compute_amount_all"
    )

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("ncr.claim") or _("New")
        return super(NcrClaim, self).create(vals)

    # Onchange methods

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

    @api.onchange("partner_source")
    def _onchange_partner_source(self):
        if self.partner_source == "customer" and self.sale_order_id:
            self.partner_id = self.sale_order_id.partner_id
            self.partner_shipping_id = self.sale_order_id.partner_shipping_id

        elif self.partner_source == "vendor" and self.purchase_order_id:
            self.partner_id = self.purchase_order_id.partner_id
            self.partner_shipping_id = False

        else:
            self.partner_id = False
            self.partner_shipping_id = False

    # Compute methods

    @api.depends("product_line.product_subtotal")
    def _compute_amount_all(self):
        for claim in self:
            total = sum(line.product_subtotal for line in claim.product_line)
            currency = claim.currency_id or self.env.company.currency_id
            claim.amount_total = currency.round(total)
            if claim.amount_total > 1000.00:
                claim.cost_impact = "high"
            elif claim.amount_total > 500.00:
                claim.cost_impact = "medium"
            else:
                claim.cost_impact = "low"

    # Buttons

    def button_populate_product_line_sale(self):
        if self.sale_order_id:
            sale_order_line = self.sale_order_id.order_line
            for line in sale_order_line:
                self.product_line = [
                    (
                        0,
                        0,
                        {
                            "ncr_claim_id": self.id,
                            "sale_order_id": line.order_id.id,
                            "sale_order_line_id": line.id,
                            "product_id": line.product_id.id,
                            "product_line_desc": line.name,
                            "product_qty": line.product_qty,
                            "product_cost": line.purchase_price,
                            "currency_id": line.currency_id.id,
                        },
                    )
                ]
            self.is_pull_button_clicked = True
        else:
            return

    def button_populate_product_line_purchase(self):
        if self.purchase_order_id:
            purchase_order_line = self.purchase_order_id.order_line
            for line in purchase_order_line:
                self.product_line = [
                    (
                        0,
                        0,
                        {
                            "ncr_claim_id": self.id,
                            "purchase_order_id": line.order_id.id,
                            "purchase_order_line_id": line.id,
                            "product_id": line.product_id.id,
                            "product_line_desc": line.name,
                            "product_qty": line.product_qty,
                            "product_cost": line.price_unit,
                            "currency_id": line.currency_id.id,
                        },
                    )
                ]
            self.is_pull_button_clicked = True
        else:
            return

    def button_clear_product_line(self):
        self.product_line.unlink()
        self.is_pull_button_clicked = False

    def button_close(self):
        self.write({"state": "closed"})

    def button_cancel(self):
        self.write({"state": "cancelled"})

    def button_reopen(self):
        self.write({"state": "open"})
