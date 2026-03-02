# -*- coding: utf-8 -*-
"""
Ticket REST API Controller
All endpoints require a valid OAuth 2.0 Bearer token.

POST /api/v1/tickets/create       → create ticket, returns full data for local storage
GET  /api/v1/tickets/<id>         → get full ticket data
GET  /api/v1/tickets              → list tickets (supports updated_since filter)
POST /api/v1/tickets/sync         → batch sync — returns only changed tickets
POST /api/v1/tickets/status-check → lightweight status poll
GET  /api/v1/health               → health check (no auth)
"""
import logging
from odoo import http, fields
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.addons.helpdesk_server.controllers.oauth_controller import OAuthController

_logger = logging.getLogger(__name__)

PRIORITY_VALUES = {'0', '1', '2', '3'}


class TicketAPIController(http.Controller):

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _ticket_data(self, ticket, client_ticket_id=None):
        """
        Serialise a ticket record into a dict suitable for client-side storage.
        Every relevant field and timestamp is included so the client never
        needs to request the same ticket twice just to get a missing field.
        """
        def fmt(dt):
            return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else None

        return {
            # Server identifiers
            'server_ticket_id':    ticket.id,
            'ticket_number':       ticket.name,
            # Client's own reference (echoed back)
            'client_ticket_id':    client_ticket_id or ticket.client_reference,
            # Core fields
            'subject':             ticket.subject,
            'description':         ticket.description,
            'priority':            ticket.priority,
            'status':              ticket.state,
            'resolution':          ticket.resolution,
            # Assignment
            'assigned_to':         ticket.assigned_to.name if ticket.assigned_to else None,
            'assigned_to_email':   ticket.assigned_to.email if ticket.assigned_to else None,
            # Client info
            'client_name':         ticket.client_name,
            # Timestamps — store ALL of these locally
            'created_at':          fmt(ticket.create_date),
            'updated_at':          fmt(ticket.write_date),
            'assigned_at':         fmt(ticket.assigned_date),
            'solved_at':           fmt(ticket.solved_date),
            'closed_at':           fmt(ticket.closed_date),
            # Metrics
            'response_time_hours': ticket.response_time,
            'resolution_time_hours': ticket.resolution_time,
        }

    def _ok(self, data, status=200):
        return {'success': True, 'data': data}

    def _err(self, message, code='ERROR'):
        return {'success': False, 'error': {'message': message, 'code': code}}

    def _auth(self, scope):
        """Verify token and return (payload, client). Raises ValueError on failure."""
        payload = OAuthController.verify_bearer_token(required_scope=scope)
        return payload, payload['client']

    # ── Health Check ─────────────────────────────────────────────────────────
    @http.route('/api/v1/health', type='json', auth='public', methods=['GET'], csrf=False, cors='*')
    def health(self, **kwargs):
        return {
            'status': 'ok',
            'service': 'Helpdesk Ticketing API',
            'version': '1.0.0',
            'auth': 'OAuth 2.0 Bearer Token',
        }

    # ── Create Ticket ─────────────────────────────────────────────────────────
    @http.route('/api/v1/tickets/create', type='json', auth='public', methods=['POST'], csrf=False, cors='*')
    def create_ticket(self, **kwargs):
        """
        Create a new support ticket.

        Request JSON:
            {
                "subject":          "Cannot login",
                "description":      "Getting a 404 error.",
                "priority":         "2",          // optional, default "1"
                "client_ticket_id": "local-42"   // optional — your local ID
            }

        Response JSON:
            { "success": true, "data": { <full ticket data> } }
        """
        try:
            _payload, client = self._auth('ticket:create')
            data = request.jsonrequest or {}

            # Validate
            if not data.get('subject'):
                raise ValidationError('Field "subject" is required')
            if not data.get('description'):
                raise ValidationError('Field "description" is required')
            priority = str(data.get('priority', '1'))
            if priority not in PRIORITY_VALUES:
                raise ValidationError('priority must be 0, 1, 2, or 3')

            # Check monthly ticket limit (from subscription plan)
            allowed, remaining, limit = client.check_ticket_limit()
            if not allowed:
                raise ValidationError(
                    f'Monthly ticket limit of {limit} reached. Please upgrade your plan.'
                )

            client_ticket_id = data.get('client_ticket_id')

            ticket = request.env['ticket.helpdesk'].sudo().create({
                'client_id':       client.id,
                'subject':         data['subject'][:256],
                'description':     data['description'],
                'priority':        priority,
                'state':           'new',
                'client_reference': client_ticket_id,
            })

            _logger.info('Ticket %s created for client %s', ticket.name, client.name)
            return self._ok(self._ticket_data(ticket, client_ticket_id))

        except ValueError as exc:
            return self._err(str(exc), 'AUTHENTICATION_FAILED')
        except ValidationError as exc:
            return self._err(str(exc), 'VALIDATION_ERROR')
        except Exception:
            _logger.exception('Error creating ticket')
            return self._err('An unexpected error occurred', 'INTERNAL_ERROR')

    # ── Get Single Ticket ────────────────────────────────────────────────────
    @http.route('/api/v1/tickets/<int:ticket_id>', type='json', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_ticket(self, ticket_id, **kwargs):
        """
        Get full ticket data by server ticket ID.
        Only returns the ticket if it belongs to the authenticated client.
        """
        try:
            _payload, client = self._auth('ticket:read')

            ticket = request.env['ticket.helpdesk'].sudo().search([
                ('id',        '=', ticket_id),
                ('client_id', '=', client.id),
            ], limit=1)

            if not ticket:
                return self._err('Ticket not found or access denied', 'NOT_FOUND')

            return self._ok(self._ticket_data(ticket))

        except ValueError as exc:
            return self._err(str(exc), 'AUTHENTICATION_FAILED')
        except Exception:
            _logger.exception('Error fetching ticket %s', ticket_id)
            return self._err('An unexpected error occurred', 'INTERNAL_ERROR')

    # ── List Tickets ─────────────────────────────────────────────────────────
    @http.route('/api/v1/tickets', type='json', auth='public', methods=['GET'], csrf=False, cors='*')
    def list_tickets(self, **kwargs):
        """
        List tickets for the authenticated client.

        Optional request JSON filters:
            {
                "status":        "new",                    // filter by status
                "priority":      "2",                      // filter by priority
                "updated_since": "2025-02-09 10:00:00",   // only changed tickets
                "limit":         50,
                "offset":        0
            }
        """
        try:
            _payload, client = self._auth('ticket:list')
            data   = request.jsonrequest or {}
            limit  = min(int(data.get('limit', 50)), 100)
            offset = int(data.get('offset', 0))

            domain = [('client_id', '=', client.id)]
            if data.get('status'):
                domain.append(('state', '=', data['status']))
            if data.get('priority'):
                domain.append(('priority', '=', str(data['priority'])))
            if data.get('updated_since'):
                domain.append(('write_date', '>', data['updated_since']))

            Ticket = request.env['ticket.helpdesk'].sudo()
            tickets = Ticket.search(domain, limit=limit, offset=offset, order='write_date desc')
            total   = Ticket.search_count(domain)

            return self._ok({
                'tickets': [self._ticket_data(t) for t in tickets],
                'total':   total,
                'limit':   limit,
                'offset':  offset,
            })

        except ValueError as exc:
            return self._err(str(exc), 'AUTHENTICATION_FAILED')
        except Exception:
            _logger.exception('Error listing tickets')
            return self._err('An unexpected error occurred', 'INTERNAL_ERROR')

    # ── Batch Sync ───────────────────────────────────────────────────────────
    @http.route('/api/v1/tickets/sync', type='json', auth='public', methods=['POST'], csrf=False, cors='*')
    def sync_tickets(self, **kwargs):
        """
        Return only the tickets that changed since the client's last sync.

        Request JSON:
            {
                "ticket_ids": [123, 124, 125],
                "last_sync":  "2025-02-09 10:00:00"   // optional
            }

        Response JSON:
            {
                "success": true,
                "data": {
                    "updated_tickets": [ <full ticket data>, ... ],
                    "total_updated":   1,
                    "sync_time":       "2025-02-09 12:00:00"   // use as next last_sync
                }
            }
        """
        try:
            _payload, client = self._auth('ticket:read')
            data       = request.jsonrequest or {}
            ticket_ids = data.get('ticket_ids', [])
            last_sync  = data.get('last_sync')

            domain = [
                ('id',        'in', ticket_ids),
                ('client_id', '=',  client.id),
            ]
            if last_sync:
                domain.append(('write_date', '>', last_sync))

            tickets = request.env['ticket.helpdesk'].sudo().search(domain)
            client.update_last_sync()

            updated = [self._ticket_data(t) for t in tickets]
            _logger.info('Sync: %d updated ticket(s) returned to %s', len(updated), client.name)

            return self._ok({
                'updated_tickets': updated,
                'total_updated':   len(updated),
                'sync_time':       fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })

        except ValueError as exc:
            return self._err(str(exc), 'AUTHENTICATION_FAILED')
        except Exception:
            _logger.exception('Error during sync')
            return self._err('An unexpected error occurred', 'INTERNAL_ERROR')

    # ── Quick Status Check ────────────────────────────────────────────────────
    @http.route('/api/v1/tickets/status-check', type='json', auth='public', methods=['POST'], csrf=False, cors='*')
    def status_check(self, **kwargs):
        """
        Lightweight status poll — returns only id, status, and updated_at.
        Use this to detect which tickets changed, then call /sync or /tickets/<id>
        for full details.

        Request JSON:
            { "ticket_ids": [123, 124, 125] }
        """
        try:
            _payload, client = self._auth('ticket:read')
            data       = request.jsonrequest or {}
            ticket_ids = data.get('ticket_ids', [])

            tickets = request.env['ticket.helpdesk'].sudo().search([
                ('id',        'in', ticket_ids),
                ('client_id', '=',  client.id),
            ])

            return self._ok({
                'tickets': [{
                    'server_ticket_id': t.id,
                    'ticket_number':    t.name,
                    'status':           t.state,
                    'updated_at':       t.write_date.strftime('%Y-%m-%d %H:%M:%S') if t.write_date else None,
                } for t in tickets]
            })

        except ValueError as exc:
            return self._err(str(exc), 'AUTHENTICATION_FAILED')
        except Exception:
            _logger.exception('Error in status-check')
            return self._err('An unexpected error occurred', 'INTERNAL_ERROR')
