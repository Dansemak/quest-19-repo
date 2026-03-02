from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SubscriptionPlan(models.Model):
    """
    Defines service tiers available to clients.
    Each plan controls API limits, features, pricing and SLAs.
    """

    _name = "subscription.plan"
    _description = "Subscription Plan"
    _order = "sequence, name"

    name = fields.Char(string="Plan Name", required=True, translate=True)
    code = fields.Char(string="Plan Code", required=True, copy=False)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)
    description = fields.Text(string="Description", translate=True)
    color = fields.Integer(string="Color")

    # ── Pricing ──────────────────────────────────────────────────────────────
    price_monthly = fields.Float(string="Monthly Price")
    price_yearly = fields.Float(string="Yearly Price")
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    # ── API & Token Limits ───────────────────────────────────────────────────
    rate_limit_per_hour = fields.Integer(
        string="API Rate Limit (per hour)",
        default=100,
        required=True,
        help="Maximum API requests allowed per hour",
    )
    token_expiry_hours = fields.Integer(
        string="Token Expiry (hours)",
        default=1,
        required=True,
        help="How long an OAuth access token remains valid (1–24)",
    )
    max_active_tokens = fields.Integer(
        string="Max Simultaneous Tokens",
        default=10,
        help="0 = unlimited",
    )

    # ── Ticket Limits ────────────────────────────────────────────────────────
    max_tickets_per_month = fields.Integer(
        string="Max Tickets / Month",
        default=50,
        help="0 = unlimited",
    )
    max_open_tickets = fields.Integer(
        string="Max Open Tickets",
        default=10,
        help="0 = unlimited",
    )

    # ── Features ─────────────────────────────────────────────────────────────
    webhook_enabled = fields.Boolean(string="Webhooks", default=False)
    priority_support = fields.Boolean(string="Priority Support", default=False)
    custom_fields_enabled = fields.Boolean(string="Custom Fields", default=False)
    api_analytics_enabled = fields.Boolean(string="API Analytics", default=False)

    # ── SLA ──────────────────────────────────────────────────────────────────
    sla_response_hours = fields.Float(
        string="SLA Response Time (hours)",
        help="0 = no SLA guarantee",
    )
    sla_resolution_hours = fields.Float(
        string="SLA Resolution Time (hours)",
        help="0 = no SLA guarantee",
    )

    # ── Sync Recommendation ──────────────────────────────────────────────────
    recommended_sync_minutes = fields.Integer(
        string="Recommended Sync Frequency (min)",
        default=15,
        help="Suggested interval for clients to poll for ticket updates",
    )

    # ── Statistics ───────────────────────────────────────────────────────────
    client_count = fields.Integer(
        string="Active Clients",
        compute="_compute_client_count",
    )

    # ── Constraints & Compute ─────────────────────────────────────────────────
    def _compute_client_count(self):
        for plan in self:
            plan.client_count = self.env["client.subscription"].search_count(
                [
                    ("plan_id", "=", plan.id),
                    ("active", "=", True),
                ]
            )

    @api.constrains("code")
    def _check_unique_code(self):
        for plan in self:
            if self.search_count([("code", "=", plan.code), ("id", "!=", plan.id)]):
                raise ValidationError(_('Plan code "%s" already exists.') % plan.code)

    @api.constrains("rate_limit_per_hour", "token_expiry_hours")
    def _check_limits(self):
        for plan in self:
            if plan.rate_limit_per_hour < 1:
                raise ValidationError(_("Rate limit must be at least 1."))
            if not (1 <= plan.token_expiry_hours <= 24):
                raise ValidationError(_("Token expiry must be between 1 and 24 hours."))

    # ── Actions ───────────────────────────────────────────────────────────────
    def action_view_clients(self):
        self.ensure_one()
        return {
            "name": _("Clients – %s") % self.name,
            "type": "ir.actions.act_window",
            "res_model": "client.subscription",
            "view_mode": "list,form",
            "domain": [("plan_id", "=", self.id)],
            "context": {"default_plan_id": self.id},
        }
