{
    "name": "Thinksoft Sale Extension",
    "summary": "Thinksoft Sales Extension",
    "description": """
        This module adds features to the Sales module.
    """,
    "author": "Thinksoft Inc.",
    "website": "http://www.thinksoft.ca",
    "license": "AGPL-3",
    "category": "Addons Custom/Thinksoft",
    "version": "19.0.1.1",
    "depends": [
        "base",
        "sale",
        "delivery",
        "stock",
        "sale_stock",
        "crm",
        "purchase",
        "thinksoft_contact_ext",
    ],
    "data": [
        "security/sale_security_groups.xml",
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "views/sale_freight_views.xml",
        "views/sale_note_views.xml",
        "views/delivery_carrier_views.xml",
        "views/stock_picking_views.xml",
        "views/purchase_order_views.xml",
        "views/account_move_views.xml",
        "views/company_user_views.xml",
        "views/crm_lead_views.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'thinksoft_sale_ext/static/src/**/*',
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
