{
    "name": "NCR",
    "description": """
        Non-Conformance Report (NCR) module for Odoo.
    """,
    "author": "Thinksoft Inc.",
    "website": "http://www.thinksoft.ca",
    "license": "LGPL-3",
    "category": "Addons Custom/Thinksoft NCR",
    "application": True,
    "version": "19.0.1.0",
    "depends": ["base", "mail", "sale", "purchase", "hr", "account"],
    "data": [
        "security/ncr_groups.xml",
        "security/ir.model.access.csv",
        "views/ncr_claim_views.xml",
        "views/ncr_product_line_views.xml",
        "views/ncr_category_views.xml",
        "views/ncr_menu_views.xml",
        "reports/ncr_templates.xml",
        "reports/ir_actions_report.xml",
        "data/ir_sequence_data.xml",
    ],
}
