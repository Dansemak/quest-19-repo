{
    "name": "Thinksoft Actions",
    "summary": "All actions live here.",
    "description": """
        All actions (specifically for labels and reports) live here.
    """,
    "author": "Thinksoft Inc.",
    "website": "http://www.thinksoft.ca",
    "license": "AGPL-3",
    "category": "Addons Custom/Thinksoft",
    "version": "19.0.1.2",
    "depends": [
        "base",
        "thinksoft_labels",
        "thinksoft_reports",
        "stock",
        "sale",
        "sale_timesheet",
        "sale_pdf_quote_builder",
        "stock",
        "thinksoft_stock_ext",
        "purchase",
        "mrp",
    ],
    "data": [
        "views/stock_picking_views.xml",
        "views/sale_order_views.xml",
        "views/purchase_order_views.xml",
        "report/ir_actions_report.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
