{
    "name": "Thinksoft Credit Limit",
    "description": """
        Puts Sale Orders on hold if the Customer's credit limit is exceeded.
    """,
    "author": "Thinksoft Inc.",
    "website": "http://www.thinksoft.ca",
    "license": "LGPL-3",
    "category": "Addons Custom/Thinksoft Credit Limit",
    "version": "19.0.1.0",
    "depends": ["base", "sale"],
    "data": [
        "security/credit_limit_groups.xml",
        "views/sale_order_views.xml",
    ],
}
