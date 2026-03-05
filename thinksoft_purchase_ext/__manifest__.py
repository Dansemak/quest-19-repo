{
    "name": "Thinksoft Purchase Extension",
    "summary": "Thinksoft Purchase Extension",
    "description": """
        This module adds features to the Purchase management module.
    """,
    "author": "Thinksoft Inc.",
    "website": "http://www.thinksoft.ca",
    "license": "AGPL-3",
    "category": "Addons Custom/Thinksoft",
    "version": "19.0.1.1",
    "depends": ["base", "purchase", "delivery"],
    "data": [
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}