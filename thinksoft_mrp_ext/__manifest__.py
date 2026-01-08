{
    "name": "Thinksoft Manufacturing Extension",
    "summary": "Thinksoft Manufacturing Extension",
    "description": """
        This module adds features to the Manufacturing module.
    """,
    "author": "Thinksoft Inc.",
    "website": "http://www.thinksoft.ca",
    "license": "AGPL-3",
    "category": "Addons Custom/Thinksoft",
    "version": "19.0.1.1",
    "depends": [
        "base",
        "mrp",
        "sale_mrp",
        "website",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mrp_department_views.xml",
        "views/mrp_production_views.xml",
        "views/mrp_bom_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
