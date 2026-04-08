{
    "name": "Thinksoft Stock Extension",
    "summary": "Thinksoft Stock Extension",
    "description": """
        This module adds features to the Stock management module.
    """,
    "author": "Thinksoft Inc.",
    "website": "http://www.thinksoft.ca",
    "license": "AGPL-3",
    "category": "Addons Custom/Thinksoft",
    "version": "19.0.1.2",
    "depends": ["base", "stock", "stock_delivery"],
    "data": [
        "security/stock_extended_security.xml",
        "views/stock_location_views.xml",
        "views/stock_move_line_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_quant_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}