{
    'name': 'Procurement Batch Generator',
    'version': '19.0.0.1',
    'category': 'Addons Custom/Thinksoft Batch Procurment',
    'license': 'AGPL-3',
    'summary': 'Wizard to create procurements from product variants',
    'author': 'Thinksoft',
    'website': 'http://www.thinksoft.ca',
    'depends': ['stock', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/procurement_batch_generator_view.xml',
        'views/product.xml'
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
}
