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
        "reports/reports_paperformats.xml",
        "reports/report_quotation.xml",
        "reports/certificate_of_compliance_templates.xml",
        "reports/commercial_invoice_templates.xml",
        "reports/coo_templates.xml",
        "reports/manufacture_copy_templates.xml",
        "reports/order_confirmation_templates.xml",
        "reports/oxygen_clean_certificate_templates.xml",
        "reports/ir_actions_report.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
