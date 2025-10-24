{
    "name": "Thinksoft Reports",
    "summary": "All reports live here.",
    "description": """
        This module contains the custom report overrides of standard Odoo reports.
    """,
    "author": "Thinksoft Inc.",
    "website": "http://www.thinksoft.ca",
    "license": "AGPL-3",
    "category": "Addons Custom/Thinksoft",
    "version": "19.0.0.0.1",
    "depends": ["base"],
    "data": [
        "reports/ir_actions_report.xml",
        "reports/reports_paperformats.xml",
        "reports/report_quotation.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
