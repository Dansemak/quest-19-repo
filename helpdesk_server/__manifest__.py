# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk Server (Company Side)',
    'version': '19.0.1.0.0',
    'category': 'Services/Helpdesk',
    'summary': 'SERVER: Receive and manage tickets from clients via OAuth 2.0 API',
    'description': """
        Helpdesk Server Module
        =======================
        
        Install this on YOUR COMPANY'S Odoo instance.
        
        This module provides:
        - OAuth 2.0 API for clients to submit tickets
        - Subscription plan management (Basic/Pro/Enterprise)
        - Client credential management
        - Full ticket management system
        - Client sync tracking
        
        Clients will use the 'helpdesk_client' module on their Odoo.
    """,
    'author': 'Your Company',
    'depends': ['base', 'mail'],
    'external_dependencies': {'python': ['PyJWT']},
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'data/default_plans.xml',
        'data/cron_jobs.xml',
        'views/subscription_plan_views.xml',
        'views/client_subscription_views.xml',
        'views/oauth_token_views.xml',
        'views/ticket_helpdesk_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
