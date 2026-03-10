{
    "name": "Thinksoft No Studio",
    "description": """
        Prevent Odoo Studio from being installed easily.
    """,
    "author": "Thinksoft Inc.",
    "website": "http://www.thinksoft.ca",
    "license": "LGPL-3",
    "category": "Addons Custom/Thinksoft",
    "version": "19.0.1.1",
    "depends": ["web", "web_enterprise"],
    "assets": {
        "web.assets_backend": [
            ("remove", "web_enterprise/static/src/views/list/list_renderer_desktop.js"),
            ("remove", "web_enterprise/static/src/views/list/list_renderer_desktop.xml"),
            ("remove", "web_studio/static/src/systray_item/systray_item.js"),
            ("remove", "web_studio/static/src/systray_item/systray_item.xml"),
            ("remove", "web_studio/static/src/views/list/list_renderer.js"),
            "thinksoft_no_studio/static/src/obstruct_studio_systray_item.xml",
            "thinksoft_no_studio/static/src/obstruct_studio_dialog.xml",
            ],
    },
}
