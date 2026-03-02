# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class TicketHelpdesk(models.Model):
    """
    Support ticket received from a client via the OAuth API.
    Designed to support client-side storage: every response includes
    all timestamps and fields so clients can keep a local copy in sync.
    """
    _name = 'ticket.helpdesk'
    _description = 'Helpdesk Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date desc'

    # ── Identity ──────────────────────────────────────────────────────────────
    name = fields.Char(
        string='Ticket Number', required=True, copy=False,
        readonly=True, index=True, default=lambda self: _('New'),
    )
    client_reference = fields.Char(
        string='Client Reference', readonly=True, index=True,
        help="The client's own local ticket ID, stored for two-way linking.",
    )

    # ── Content ───────────────────────────────────────────────────────────────
    subject = fields.Char(string='Subject', required=True, tracking=True)
    description = fields.Text(string='Description', required=True)
    resolution = fields.Text(string='Resolution', tracking=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    # ── Relations ─────────────────────────────────────────────────────────────
    client_id = fields.Many2one(
        'client.subscription', string='Client',
        required=True, readonly=True, tracking=True, ondelete='restrict', index=True,
    )
    client_name = fields.Char(related='client_id.name', store=True, readonly=True)
    assigned_to = fields.Many2one(
        'res.users', string='Assigned To',
        domain=[('share', '=', False)], tracking=True,
    )

    # ── Classification ────────────────────────────────────────────────────────
    priority = fields.Selection([
        ('0', 'Low'), ('1', 'Normal'), ('2', 'High'), ('3', 'Urgent'),
    ], default='1', index=True, tracking=True)

    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('waiting', 'Waiting on Client'),
        ('solved', 'Solved'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], default='new', required=True, index=True, tracking=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    # create_date and write_date are provided by Odoo automatically.
    assigned_date = fields.Datetime(string='Assigned On', readonly=True)
    solved_date = fields.Datetime(string='Solved On', readonly=True)
    closed_date = fields.Datetime(string='Closed On', readonly=True)

    # ── Computed Metrics ──────────────────────────────────────────────────────
    response_time = fields.Float(
        string='Response Time (h)', compute='_compute_times', store=True,
    )
    resolution_time = fields.Float(
        string='Resolution Time (h)', compute='_compute_times', store=True,
    )

    active = fields.Boolean(default=True)

    # ── ORM Overrides ─────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ticket.helpdesk') or _('New')
        return super().create(vals_list)

    def write(self, vals):
        now = fields.Datetime.now()
        for ticket in self:
            # Auto-set assigned_date when agent is first assigned
            if 'assigned_to' in vals and vals['assigned_to'] and not ticket.assigned_date:
                vals['assigned_date'] = now
                if ticket.state == 'new':
                    vals.setdefault('state', 'in_progress')
        if vals.get('state') == 'solved':
            for ticket in self:
                if not ticket.solved_date:
                    vals['solved_date'] = now
        if vals.get('state') == 'closed':
            for ticket in self:
                if not ticket.closed_date:
                    vals['closed_date'] = now
        return super().write(vals)

    @api.depends('create_date', 'assigned_date', 'solved_date')
    def _compute_times(self):
        for ticket in self:
            if ticket.create_date and ticket.assigned_date:
                ticket.response_time = (ticket.assigned_date - ticket.create_date).total_seconds() / 3600
            else:
                ticket.response_time = 0.0
            if ticket.create_date and ticket.solved_date:
                ticket.resolution_time = (ticket.solved_date - ticket.create_date).total_seconds() / 3600
            else:
                ticket.resolution_time = 0.0

    # ── UI Actions ────────────────────────────────────────────────────────────
    def action_assign_to_me(self):
        self.write({'assigned_to': self.env.user.id})

    def action_set_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_set_waiting(self):
        self.write({'state': 'waiting'})

    def action_set_solved(self):
        self.write({'state': 'solved'})

    def action_set_closed(self):
        self.write({'state': 'closed'})

    def action_reopen(self):
        self.write({'state': 'in_progress'})
