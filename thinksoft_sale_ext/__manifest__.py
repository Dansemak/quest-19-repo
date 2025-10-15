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
    "version": "19.0.0.0.1",
    "depends": ["base", "sale", "delivery", "stock", 'sale_stock', 'crm',],
    "data": [
        'security/sales_extended_security.xml',
        'security/ir.model.access.csv',
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "views/sale_freight_views.xml",
        "views/sale_note_views.xml",
        "views/job_project_views.xml",
        "views/company_user_views.xml",
        "views/delivery_carrier_views.xml",
        "views/stock_picking_views.xml",
        "views/crm_lead_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
