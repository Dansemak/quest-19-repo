{
    "name": "MTR",
    "description": """
        Metal Treatment Report (MTR) module for Odoo.
    """,
    "author": "Thinksoft Inc.",
    "website": "http://www.thinksoft.ca",
    "license": "LGPL-3",
    "category": "Addons Custom/Thinksoft MTR",
    "application": True,
    "version": "0.1",
    "depends": ["base", "mail", "stock"],
    "data": [
        "security/mtr_groups.xml",
        "security/ir.model.access.csv",
        "views/mtr_template_views.xml",
        "views/mtr_menu_views.xml",
    ],
}
