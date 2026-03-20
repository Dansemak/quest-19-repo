{
    "name": "Thinksoft Minimum Margin",
    "summary": "Forces authorization of sales orders that do not meet the minimum margin threshold.",
    "description": """
        This module adds a minimum margin check to sales orders. If the margin of a sales
        order falls below the defined threshold, the order will require authorization
        before it can be confirmed. This helps ensure that sales are profitable and meet
        the company's financial goals.
    """,
    "author": "Thinksoft Inc.",
    "website": "https://www.thinksoft.ca",
    "category": "Addons Custom",
    "version": "19.0.0.1",
    "depends": [
        "base",
        "sale",
        "sale_stock",
        "product",
    ],
    "data": [
        'security/security.xml',
        "views/sale_order_views.xml",
        "views/product_category_views.xml",
        "data/mail_activity_type.xml"
    ],
}
