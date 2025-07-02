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
    "version": "0.1",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/ncr_claim_views.xml",
    ],
}
