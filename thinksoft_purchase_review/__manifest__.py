# -*- coding: utf-8 -*-
{
    'name': "thinksoft_purchase_review",

    'summary': """
        This module adds two list views to Purchase / Reporting called Purchase Review and Min Max Review.""",

    'description': """
        This module is used to help Purchasers determine which products to purchase and what quantity to order.
        It provides a suggested Buy, and a suggested Min Max. It takes into account total sales in the past 365 days,
        Quantity on Hand, amount incoming, average sales per day, and any ship delays expected.  Using these values,
        Purchase Review will calculate a Suggested Buy quantity.  It will display a date Last Updated column.
        If this column is green, then the product calculation is current as of today.  If it is amber,
        then the calculation needs to be refreshed.  Select the line with a check box on the far left.
        Then go to the Action menu, and click Update Review to refresh the calculation.
        It also helps to determine what quantities should be used for Min Max on a reorder point.
    """,

    'author': "Thinksoft Inc.",
    'website': "http://www.thinksoft.ca",
    'license': 'LGPL-3',
    'category': 'Addons Custom/Thinksoft Purchase Review',
    'version': '19.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'purchase', 'thinksoft_batch_procurement'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_review_report.xml',
        "wizard/po_generator_view.xml",
        # "data/refresh_ir_cron.xml",
    ],
}
