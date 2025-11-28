{
    'name': 'Package Planner',
    'version': '1.3',
    'category': 'Addons Custom/Thinksoft Package Planner',
    'description': """ Order Fullfillment Packaging Tool July 2021

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
    'init_xml': [],
    'data': [
        'security/ir.model.access.csv',
        'views/package_planner_view.xml',
        'report/3x4_qweb.xml',
        'report/3x4_qweb_template.xml',
        'report/1.25x4_qweb.xml',
        'report/1.25x4_qweb_template.xml',
        'report/box_labels_qweb.xml',
        'report/box_labels_qweb_template.xml',
        'report/box_labels_skid_qweb_template.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
