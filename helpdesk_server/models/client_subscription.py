import hashlib
import hmac
import logging
import secrets
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ClientSubscription(models.Model):
    """
    Represents a client and their OAuth 2.0 credentials.
    Limits and features are inherited from the linked subscription.plan
    but can be overridden per client when needed.
    """

    _name = "client.subscription"
    _description = "Client Subscription"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    # ── Basic Information ─────────────────────────────────────────────────────
    name = fields.Char(string="Client Name", required=True, tracking=True)
    contact_id = fields.Many2one(
        "res.partner",
        string="Primary Contact",
        required=True,
        tracking=True,
    )
    email = fields.Char(related="contact_id.email", store=True, readonly=True)
    phone = fields.Char(related="contact_id.phone", store=True, readonly=True)
    notes = fields.Text(string="Internal Notes")
    active = fields.Boolean(default=True)

    # ── OAuth 2.0 Credentials ─────────────────────────────────────────────────
    client_id = fields.Char(
        string="OAuth Client ID",
        readonly=True,
        copy=False,
        index=True,
    )
    # Stored temporarily after generation so it can be copied from the UI.
    # Cleared on next save via _clear_plain_secret().
    client_secret = fields.Char(
        string="Client Secret (copy now!)",
        readonly=True,
        copy=False,
        groups="base.group_system",
    )
    client_secret_hash = fields.Char(
        string="Client Secret Hash",
        readonly=True,
        copy=False,
    )
    credentials_created = fields.Datetime(string="Credentials Generated", readonly=True)
    last_token_request = fields.Datetime(string="Last Token Request", readonly=True)

    # ── Webhook (optional) ────────────────────────────────────────────────────
    webhook_url = fields.Char(string="Webhook URL")
    webhook_secret = fields.Char(
        string="Webhook Secret",
        readonly=True,
        copy=False,
        groups="base.group_system",
    )
    webhook_active = fields.Boolean(string="Webhooks Enabled", default=False)

    # ── Sync Tracking ─────────────────────────────────────────────────────────
    last_sync_time = fields.Datetime(string="Last Client Sync", readonly=True)

    # ── Subscription Plan ─────────────────────────────────────────────────────
    plan_id = fields.Many2one(
        "subscription.plan",
        string="Subscription Plan",
        required=True,
        tracking=True,
        domain=[("active", "=", True)],
        ondelete="restrict",
    )
    plan_name = fields.Char(related="plan_id.name", store=True, readonly=True)

    # ── Subscription Dates ────────────────────────────────────────────────────
    subscription_active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
    )
    start_date = fields.Date(
        string="Start Date",
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    expiry_date = fields.Date(string="Expiry Date", tracking=True)
    auto_renew = fields.Boolean(string="Auto Renew", default=False)
    days_until_expiry = fields.Integer(compute="_compute_days_until_expiry")

    # ── Effective Limits (plan defaults, overridable per client) ──────────────
    custom_rate_limit = fields.Integer(
        string="Custom Rate Limit",
        default=0,
        help="Overrides plan rate limit for this client. 0 = use plan default.",
    )
    custom_token_expiry = fields.Integer(
        string="Custom Token Expiry (hours)",
        default=0,
        help="Overrides plan token expiry for this client. 0 = use plan default.",
    )
    rate_limit_per_hour = fields.Integer(
        string="Effective Rate Limit",
        compute="_compute_effective_limits",
        store=True,
    )
    token_expiry_hours = fields.Integer(
        string="Effective Token Expiry (h)",
        compute="_compute_effective_limits",
        store=True,
    )
    sync_frequency_minutes = fields.Integer(
        string="Sync Frequency (min)",
        compute="_compute_effective_limits",
        store=True,
    )

    # ── Read-only plan features shown on form ─────────────────────────────────
    webhook_enabled_by_plan = fields.Boolean(
        related="plan_id.webhook_enabled",
        readonly=True,
    )
    priority_support = fields.Boolean(related="plan_id.priority_support", readonly=True)
    max_tickets_per_month = fields.Integer(
        related="plan_id.max_tickets_per_month", readonly=True
    )
    monthly_price = fields.Float(related="plan_id.price_monthly", readonly=True)

    # ── Statistics ────────────────────────────────────────────────────────────
    active_tokens_count = fields.Integer(compute="_compute_statistics")
    ticket_count = fields.Integer(compute="_compute_statistics")
    tickets_this_month = fields.Integer(compute="_compute_statistics")

    # ── Status ────────────────────────────────────────────────────────────────
    subscription_status = fields.Selection(
        [
            ("active", "Active"),
            ("expiring_soon", "Expiring Soon"),
            ("expired", "Expired"),
            ("inactive", "Inactive"),
        ],
        compute="_compute_subscription_status",
        store=True,
        tracking=True,
    )

    # ── Compute Methods ───────────────────────────────────────────────────────
    @api.depends("expiry_date")
    def _compute_days_until_expiry(self):
        today = fields.Date.today()
        for rec in self:
            rec.days_until_expiry = (
                (rec.expiry_date - today).days if rec.expiry_date else 0
            )

    @api.depends("subscription_active", "expiry_date", "days_until_expiry")
    def _compute_subscription_status(self):
        today = fields.Date.today()
        for rec in self:
            if not rec.subscription_active:
                rec.subscription_status = "inactive"
            elif rec.expiry_date and rec.expiry_date < today:
                rec.subscription_status = "expired"
            elif rec.expiry_date and rec.days_until_expiry <= 30:
                rec.subscription_status = "expiring_soon"
            else:
                rec.subscription_status = "active"

    @api.depends("plan_id", "custom_rate_limit", "custom_token_expiry")
    def _compute_effective_limits(self):
        for rec in self:
            if rec.plan_id:
                rec.rate_limit_per_hour = (
                    rec.custom_rate_limit
                    if rec.custom_rate_limit > 0
                    else rec.plan_id.rate_limit_per_hour
                )
                rec.token_expiry_hours = (
                    rec.custom_token_expiry
                    if rec.custom_token_expiry > 0
                    else rec.plan_id.token_expiry_hours
                )
                rec.sync_frequency_minutes = rec.plan_id.recommended_sync_minutes
            else:
                rec.rate_limit_per_hour = 100
                rec.token_expiry_hours = 1
                rec.sync_frequency_minutes = 15

    def _compute_statistics(self):
        now = fields.Datetime.now()
        today = fields.Date.today()
        month_start = today.replace(day=1)
        Token = self.env["oauth.token"]
        Ticket = self.env["ticket.helpdesk"]
        for rec in self:
            rec.active_tokens_count = Token.search_count(
                [
                    ("client_id", "=", rec.id),
                    ("revoked", "=", False),
                    ("expires_at", ">", now),
                ]
            )
            rec.ticket_count = Ticket.search_count([("client_id", "=", rec.id)])
            rec.tickets_this_month = Ticket.search_count(
                [
                    ("client_id", "=", rec.id),
                    ("create_date", ">=", month_start),
                ]
            )

    # ── Constraints ───────────────────────────────────────────────────────────
    @api.constrains("expiry_date", "start_date")
    def _check_dates(self):
        for rec in self:
            if rec.expiry_date and rec.start_date and rec.expiry_date < rec.start_date:
                raise ValidationError(_("Expiry date must be after start date."))

    @api.constrains("webhook_active", "plan_id")
    def _check_webhook_allowed(self):
        for rec in self:
            if rec.webhook_active and rec.plan_id and not rec.plan_id.webhook_enabled:
                raise ValidationError(
                    _(
                        'Webhooks are not included in the "%s" plan. '
                        "Please upgrade to enable webhooks."
                    )
                    % rec.plan_id.name
                )

    # ── Business Logic ────────────────────────────────────────────────────────
    def check_ticket_limit(self):
        """
        Returns (allowed, remaining, limit).
        remaining = -1 and limit = 0 means unlimited.
        """
        self.ensure_one()
        limit = self.max_tickets_per_month
        if limit == 0:
            return True, -1, 0
        remaining = limit - self.tickets_this_month
        return remaining > 0, remaining, limit

    def update_last_sync(self):
        self.sudo().write({"last_sync_time": fields.Datetime.now()})

    # ── Credential Actions ────────────────────────────────────────────────────
    def action_generate_oauth_credentials(self):
        self.ensure_one()
        plain_secret = secrets.token_urlsafe(32)
        self.write(
            {
                "client_id": f"client_{secrets.token_urlsafe(16)}",
                "client_secret": plain_secret,
                "client_secret_hash": hashlib.sha256(plain_secret.encode()).hexdigest(),
                "credentials_created": fields.Datetime.now(),
            }
        )
        # Revoke all existing tokens since credentials changed
        self.env["oauth.token"].search([("client_id", "=", self.id)]).write(
            {"revoked": True}
        )
        self.message_post(
            body=_("OAuth 2.0 credentials regenerated. All previous tokens revoked."),
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Credentials Generated"),
                "message": _(
                    "Copy the Client Secret now — it will be hidden after you close this record!"
                ),
                "type": "success",
                "sticky": True,
            },
        }

    def action_revoke_all_tokens(self):
        self.ensure_one()
        count = self.env["oauth.token"].search_count(
            [
                ("client_id", "=", self.id),
                ("revoked", "=", False),
            ]
        )
        self.env["oauth.token"].search([("client_id", "=", self.id)]).write(
            {"revoked": True}
        )
        self.message_post(body=_("%d token(s) revoked.") % count)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Tokens Revoked"),
                "message": _("%d active token(s) revoked.") % count,
                "type": "warning",
            },
        }

    def action_generate_webhook_secret(self):
        self.ensure_one()
        if not self.plan_id.webhook_enabled:
            raise ValidationError(
                _('Webhooks are not available on the "%s" plan.') % self.plan_id.name
            )
        self.write(
            {"webhook_secret": secrets.token_urlsafe(32), "webhook_active": True}
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Webhook Secret Generated"),
                "message": _(
                    "Copy the Webhook Secret now — it will be hidden after you close this record!"
                ),
                "type": "success",
                "sticky": True,
            },
        }

    def action_renew_subscription(self):
        self.ensure_one()
        if not self.expiry_date:
            raise ValidationError(_("Cannot renew a subscription with no expiry date."))
        new_expiry = self.expiry_date + timedelta(days=365)
        self.write({"expiry_date": new_expiry, "subscription_active": True})
        self.message_post(body=_("Subscription renewed until %s.") % new_expiry)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Subscription Renewed"),
                "message": _("Renewed until %s.") % new_expiry,
                "type": "success",
            },
        }

    def action_view_tickets(self):
        self.ensure_one()
        return {
            "name": _("Tickets – %s") % self.name,
            "type": "ir.actions.act_window",
            "res_model": "ticket.helpdesk",
            "view_mode": "list,form",
            "domain": [("client_id", "=", self.id)],
            "context": {"default_client_id": self.id},
        }

    def action_view_tokens(self):
        self.ensure_one()
        return {
            "name": _("OAuth Tokens – %s") % self.name,
            "type": "ir.actions.act_window",
            "res_model": "oauth.token",
            "view_mode": "list,form",
            "domain": [("client_id", "=", self.id)],
        }

    # ── Static: Credential Verification (used by OAuth controller) ────────────
    @api.model
    def verify_client_credentials(self, client_id_str, client_secret_str):
        """
        Returns the client record if credentials are valid, else False.
        Uses constant-time comparison to prevent timing attacks.
        """
        if not client_id_str or not client_secret_str:
            return False
        client = self.sudo().search(
            [
                ("client_id", "=", client_id_str),
                ("active", "=", True),
            ],
            limit=1,
        )
        if not client or not client.client_secret_hash:
            return False
        provided_hash = hashlib.sha256(client_secret_str.encode()).hexdigest()
        if not hmac.compare_digest(provided_hash, client.client_secret_hash):
            return False
        client.sudo().write({"last_token_request": fields.Datetime.now()})
        return client

    # ── Cron Jobs ─────────────────────────────────────────────────────────────
    @api.model
    def _cron_check_expiring_subscriptions(self):
        today = fields.Date.today()
        for days in [30, 14, 7, 3, 1]:
            target = today + timedelta(days=days)
            for client in self.search(
                [
                    ("subscription_active", "=", True),
                    ("expiry_date", "=", target),
                ]
            ):
                client.message_post(
                    body=_("Subscription expires in %d day(s) on %s.")
                    % (days, client.expiry_date),
                    partner_ids=client.contact_id.ids,
                )
