{
    "name": "Thinksoft Account Extension",
    "summary": "Thinksoft Account Extension",
    "description": """
        This module adds features to the Account management module.
    """,
    "author": "Thinksoft Inc.",
    "website": "http://www.thinksoft.ca",
    "license": "AGPL-3",
    "category": "Addons Custom/Thinksoft",
    "version": "19.0.1.0",
    "depends": ["base", "account"],
    "data": [
        "views/account_batch_payment_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}