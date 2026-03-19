{
    "name": "Thinksoft Labels",
    "summary": "All labels live here.",
    "description": """
        All labels live here.
    """,
    "author": "Thinksoft Inc.",
    "website": "http://www.thinksoft.ca",
    "license": "AGPL-3",
    "category": "Addons Custom/Thinksoft",
    "version": "19.0.1.3",
    "depends": ["base"],
    "data": [
        "reports/reports_paperformats.xml",
        "reports/print_label_1_25x4_templates.xml",
        "reports/shipping_label_3x4_templates.xml",
        "reports/print_label_3x4_templates.xml",
        "reports/shipping_label_4x4_templates.xml",
        "reports/location_labels.xml",
        "reports/4x4_label_for_all_templates.xml",
        "reports/4x4_label_templates.xml",
        "reports/4x4_label.xml",
        "reports/print_label_4x4_templates.xml",
        "reports/rack_label_12x4.xml",
        "reports/customer_1_25x4_templates.xml",
        "reports/customer_2x4_templates.xml",
        # Actions and menus always last
        "reports/ir_actions_report.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
