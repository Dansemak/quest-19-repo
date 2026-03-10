{
    "name": "Thinksoft Discount",
    "summary": "Thinksoft Discount",
    "description": """
        This module makes the subtotals on Sale Order Lines use the rounded discount unit price.
    """,
    "author": "Thinksoft Inc.",
    "website": "http://www.thinksoft.ca",
    "license": "AGPL-3",
    "category": "Addons Custom/Thinksoft",
    "version": "19.0.1.2",
    "depends": ["base", "sale", "account"],
    "data": [
        "security/update_sale_groups.xml",
        "views/account_move_views.xml",
        "views/sale_order_views.xml",
    ],
}
