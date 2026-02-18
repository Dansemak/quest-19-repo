{
    'name': 'Package Planner',
    'version': '19.0.1.2',
    'category': 'Addons Custom/Thinksoft Package Planner',
    'description': """
        The purpose of this module is to generate the labels needed for a shipment when an order
        is fullfilled.  By using this planner the user will be able to print labels for each
        box and pallet required in an order.  The labels will list the product and 
        quantities that are in the box or pallet.  If more than one box is used in the
        shipment, the label will indicate a box number of quantity value such as BOX 1 of 3.
        The same is true for pallets.  The labels will dislay the order number,
        shipping address and quantities.  This makes it easier for receivers to quickly 
        locate a specific product when receiving a shipment.
    """,
    'author': 'Thinksoft Inc',
    'website': 'http://www.thinksoft.ca',
    'license': 'LGPL-3',
    'depends': ['stock','thinksoft_mtr'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'report/3x4_label_template.xml',
        'report/1_25x4_label_template.xml',
        'report/box_label_template.xml',
        'report/skid_label_template.xml',
    ],
    "application": True,
}
