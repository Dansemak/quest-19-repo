# -*- coding: utf-8 -*-
"""
OAuth 2.0 Controller — Client Credentials Flow
Runs on YOUR COMPANY's Odoo instance.

POST /oauth/token   → issue a JWT access token
POST /oauth/revoke  → revoke a token
GET  /oauth/health  → health check (no auth required)
"""
import jwt
import uuid
import logging
from datetime import datetime, timedelta
from odoo import http, fields
from odoo.http import request

_logger = logging.getLogger(__name__)


class OAuthController(http.Controller):

    ALGORITHM = 'HS256'

    def _jwt_secret(self):
        """Read JWT secret from Odoo system parameters so it can be changed without code edits."""
        return request.env['ir.config_parameter'].sudo().get_param(
            'helpdesk.jwt_secret_key',
            default='CHANGE-THIS-SECRET-IN-PRODUCTION',
        )

    # ── Token Endpoint ────────────────────────────────────────────────────────
    @http.route('/oauth/token', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def get_token(self, **post):
        """
        Issue an access token using the OAuth 2.0 Client Credentials flow.

        Request (form-encoded):
            grant_type    = client_credentials
            client_id     = <your client ID>
            client_secret = <your client secret>

        Response (JSON):
            {
                "access_token": "eyJ...",
                "token_type":   "Bearer",
                "expires_in":   3600,
                "scope":        "ticket:create ticket:read ticket:list"
            }
        """
        try:
            grant_type    = post.get('grant_type')
            client_id_str = post.get('client_id')
            client_secret = post.get('client_secret')

            _logger.info('Token request for client_id=%s', client_id_str)

            # ── Validate grant type
            if grant_type != 'client_credentials':
                return self._error('unsupported_grant_type')

            if not client_id_str or not client_secret:
                return self._error('invalid_request', 'client_id and client_secret are required')

            # ── Authenticate client
            ClientModel = request.env['client.subscription']
            client = ClientModel.verify_client_credentials(client_id_str, client_secret)
            if not client:
                return self._error('invalid_client', 'Invalid credentials')

            # ── Check subscription
            if not client.subscription_active:
                return self._error('inactive_subscription', 'Subscription is not active')
            if client.expiry_date and client.expiry_date < fields.Date.today():
                return self._error('expired_subscription',
                                   f'Subscription expired on {client.expiry_date}')

            # ── Build JWT
            now        = datetime.utcnow()
            expires_at = now + timedelta(hours=client.token_expiry_hours)
            token_id   = str(uuid.uuid4())
            scope      = 'ticket:create ticket:read ticket:list'

            payload = {
                'jti':             token_id,
                'iss':             'helpdesk_ticketing',
                'sub':             str(client.id),       # client DB id
                'client_id':       client.client_id,     # OAuth client_id string
                'client_name':     client.name,
                'scope':           scope,
                'iat':             int(now.timestamp()),
                'exp':             int(expires_at.timestamp()),
            }

            access_token = jwt.encode(payload, self._jwt_secret(), algorithm=self.ALGORITHM)

            # ── Persist token record
            request.env['oauth.token'].sudo().create({
                'token_id':    token_id,
                'client_id':   client.id,
                'access_token': access_token,
                'scope':       scope,
                'issued_at':   now,
                'expires_at':  expires_at,
            })

            _logger.info('Token issued to %s (expires in %dh)', client.name, client.token_expiry_hours)

            return request.make_json_response({
                'access_token': access_token,
                'token_type':   'Bearer',
                'expires_in':   client.token_expiry_hours * 3600,
                'scope':        scope,
            })

        except Exception:
            _logger.exception('Error in /oauth/token')
            return self._error('server_error', status=500)

    # ── Revoke Endpoint ───────────────────────────────────────────────────────
    @http.route('/oauth/revoke', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def revoke_token(self, **post):
        """
        Revoke an access token (RFC 7009 — always returns 200).

        Request (form-encoded):
            token = <access_token>
        """
        try:
            token_value = post.get('token', '')
            if token_value:
                token = request.env['oauth.token'].sudo().search(
                    [('access_token', '=', token_value)], limit=1,
                )
                if token:
                    token.write({
                        'revoked': True,
                        'revoked_at': fields.Datetime.now(),
                    })
        except Exception:
            _logger.exception('Error in /oauth/revoke')
        # Per RFC 7009, always respond 200 OK
        return request.make_json_response({'status': 'ok'})

    # ── Health Check ──────────────────────────────────────────────────────────
    @http.route('/oauth/health', type='json', auth='public', methods=['GET'], csrf=False, cors='*')
    def health(self, **kwargs):
        return {
            'status': 'ok',
            'service': 'Helpdesk Ticketing OAuth 2.0',
            'version': '1.0.0',
        }

    # ── Static Helper: Verify Bearer Token ───────────────────────────────────
    @staticmethod
    def verify_bearer_token(required_scope=None):
        """
        Verify the JWT Bearer token sent in the Authorization header.

        Called by every protected API endpoint.

        Returns:
            dict  — decoded JWT payload, plus a 'client' key containing
                    the client.subscription record.

        Raises:
            ValueError — if authentication fails for any reason.
        """
        auth_header = request.httprequest.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            raise ValueError('Missing or invalid Authorization header')

        token_value = auth_header[7:]   # strip "Bearer "

        # Decode JWT
        try:
            secret = request.env['ir.config_parameter'].sudo().get_param(
                'helpdesk.jwt_secret_key',
                default='CHANGE-THIS-SECRET-IN-PRODUCTION',
            )
            payload = jwt.decode(token_value, secret, algorithms=[OAuthController.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise ValueError('Token has expired')
        except jwt.InvalidTokenError as exc:
            raise ValueError(f'Invalid token: {exc}')

        # Check the token record (not revoked, not expired)
        token_record = request.env['oauth.token'].sudo().search([
            ('token_id', '=', payload.get('jti')),
            ('revoked',  '=', False),
            ('expires_at', '>', fields.Datetime.now()),
        ], limit=1)

        if not token_record:
            raise ValueError('Token not found, revoked, or expired')

        # Track usage
        token_record.update_usage()

        # Scope check
        if required_scope:
            granted = payload.get('scope', '').split()
            if required_scope not in granted:
                raise ValueError(f'Insufficient scope: {required_scope} required')

        # Load and validate client
        client = request.env['client.subscription'].sudo().browse(int(payload['sub']))
        if not client.exists():
            raise ValueError('Client not found')
        if not client.subscription_active:
            raise ValueError('Client subscription is not active')
        if client.expiry_date and client.expiry_date < fields.Date.today():
            raise ValueError('Client subscription has expired')

        payload['client'] = client
        return payload

    # ── Private Helper ────────────────────────────────────────────────────────
    def _error(self, code, description=None, status=400):
        messages = {
            'invalid_request':        'Missing required parameter',
            'invalid_client':         'Client authentication failed',
            'unsupported_grant_type': 'Only client_credentials is supported',
            'inactive_subscription':  'Subscription is not active',
            'expired_subscription':   'Subscription has expired',
            'server_error':           'Internal server error',
        }
        return request.make_json_response({
            'error': code,
            'error_description': description or messages.get(code, 'Unknown error'),
        }, status=status)
