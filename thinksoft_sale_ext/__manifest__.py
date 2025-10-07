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
    "depends": ["base", "sale", "delivery"],
    "data": [
        'security/ir.model.access.csv',
        "wizard/choose_delivery_carrier_views.xml",
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "views/sale_freight_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
