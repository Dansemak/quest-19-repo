# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import models, fields, api, _


class OAuthToken(models.Model):
    """
    Stores every JWT access token issued to clients.
    Enables per-token revocation and usage tracking.
    """
    _name = 'oauth.token'
    _description = 'OAuth 2.0 Access Token'
    _order = 'create_date desc'
    _rec_name = 'token_id'

    token_id = fields.Char(
        string='JWT ID (jti)', required=True, index=True, readonly=True,
        help='The unique identifier embedded in the JWT (jti claim).',
    )
    client_id = fields.Many2one(
        'client.subscription', string='Client',
        required=True, ondelete='cascade', index=True,
    )
    client_name = fields.Char(related='client_id.name', store=True, readonly=True)
    access_token = fields.Text(string='JWT Token', required=True, readonly=True)
    token_type = fields.Char(default='Bearer', readonly=True)
    scope = fields.Char(string='Scope', readonly=True)
    issued_at = fields.Datetime(string='Issued At', required=True, readonly=True)
    expires_at = fields.Datetime(string='Expires At', required=True, index=True, readonly=True)

    # Revocation
    revoked = fields.Boolean(default=False, index=True)
    revoked_at = fields.Datetime(readonly=True)
    revoked_by = fields.Many2one('res.users', readonly=True)

    # Usage
    last_used = fields.Datetime(readonly=True)
    usage_count = fields.Integer(default=0, readonly=True)

    # Computed status
    status = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ], compute='_compute_status', string='Status')

    @api.depends('revoked', 'expires_at')
    def _compute_status(self):
        now = fields.Datetime.now()
        for token in self:
            if token.revoked:
                token.status = 'revoked'
            elif token.expires_at <= now:
                token.status = 'expired'
            else:
                token.status = 'active'

    def action_revoke(self):
        self.ensure_one()
        if self.revoked:
            return
        self.write({
            'revoked': True,
            'revoked_at': fields.Datetime.now(),
            'revoked_by': self.env.user.id,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Token Revoked'),
                'message': _('The access token has been revoked.'),
                'type': 'success',
            },
        }

    def update_usage(self):
        """Called every time this token authenticates a request."""
        self.ensure_one()
        self.sudo().write({
            'last_used': fields.Datetime.now(),
            'usage_count': self.usage_count + 1,
        })

    @api.model
    def cleanup_expired_tokens(self, days=7):
        """Cron: delete tokens that expired more than `days` days ago."""
        cutoff = fields.Datetime.now() - timedelta(days=days)
        old_tokens = self.search([('expires_at', '<', cutoff)])
        count = len(old_tokens)
        old_tokens.unlink()
        return count
