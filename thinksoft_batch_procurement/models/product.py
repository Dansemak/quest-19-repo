# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_stock(self):
        self._get_stocks(12)
        self._get_stocks(21)

    def _get_all_stock(self):
        for product in self:
            product.qty_on_hand = 0
            product.update({
                'qty_on_hand': product.qty_edm_available + product.qty_edm_reserved + product.qty_clgy_available + product.qty_clgy_reserved + product.incoming_qty
            })

    qty_edm_available = fields.Float(compute= get_stock, type="float", string="EWH", index=True, digits='Product Unit of Measure')
    qty_clgy_available = fields.Float(compute= get_stock, type="float", string="CWH", index=True, digits='Product Unit of Measure')
    qty_edm_reserved = fields.Float(compute= get_stock, type="float", string="EWHr", help='Reserved Quantity in Edm', index=True, digits='Product Unit of Measure')
    qty_clgy_reserved = fields.Float(compute= get_stock, type="float", string="CWHr", help='Reserved Quantity in Cal', index=True, digits='Product Unit of Measure')
    qty_on_hand = fields.Float(compute=_get_all_stock, type="float", string="QoH + Incoming", index=True, digits='Product Unit of Measure')

    def _get_stocks(self, location_id):
        domain_qty = ['&',('product_id', 'in', self.ids), ('location_id','=', location_id)]
        states = ['done', 'cancel', 'draft']
        domain_reserved = domain_qty + [('state','not in', states)]

        prod_qty = self.env['stock.quant'].read_group(domain_qty, ['product_id', 'quantity'], ['product_id'])
        qty_available = dict(map(lambda x: (x['product_id'][0],x['quantity']), prod_qty))

        qty_out = self.env['stock.move'].read_group(domain_reserved, ['product_id', 'product_qty'], ['product_id'])
        move_out = dict(map(lambda x: (x['product_id'][0],x['product_qty']), qty_out))

        for product in self:
            if location_id == 12:
                product.qty_edm_available = 0
                product.qty_edm_reserved = 0
                outgoing_qty = float_round(move_out.get(product.id, 0.0), precision_rounding=product.uom_id.rounding)
                product.update({
                    'qty_edm_available': qty_available.get(product.id, 0.0) - outgoing_qty,
                    'qty_edm_reserved': outgoing_qty,
                })
            elif location_id == 21:
                product.qty_clgy_available = 0
                product.qty_clgy_reserved = 0
                outgoing_qty = float_round(move_out.get(product.id, 0.0), precision_rounding=product.uom_id.rounding)
                product.update({
                    'qty_clgy_available': qty_available.get(product.id, 0.0) - outgoing_qty,
                    'qty_clgy_reserved': outgoing_qty,
                })
