from odoo import models, fields, api, _
import time
from datetime import datetime


class PoGenerator(models.TransientModel):
    _name = 'po.generator'
    _description = 'Wizard to create procurements from purchase review tree'

    @api.model
    def get_lines(self):
        stock_wh = self.env['stock.warehouse.orderpoint']
        lines = []
        wh_line = stock_wh.browse(self._context.get('active_ids'))
        for line in wh_line:
            vendors = []
            purchase = False
            product = line.product_id
            vendors = [vendor.name.id for vendor in product.seller_ids]
            if product.seller_ids:
                purchase = self.env['purchase.order'].search(
                    [('partner_id', '=', product.seller_ids[0].name.id), ('state', 'in', ('draft', 'sent'))])
                if line.location_id and purchase:
                    purchase = self.env['purchase.order'].search([('id', 'in', purchase.ids), (
                        'picking_type_id.default_location_dest_id', '=', line.location_id.id)])
            d1 = {
                'product_id': line.product_id.id,
                'vendor_id': product.seller_ids and product.seller_ids[0].name.id or False,
                'vendor_ids': vendors and [(6, 0, vendors)] or False,
                'cost_select': self.cost_select or False,
                'cost_price': product.standard_price,
                'qty_available': product.qty_available,
                'outgoing_qty': product.outgoing_qty,
                'incoming_qty': product.incoming_qty,
                'uom_id': product.uom_id.id,
                'procurement_qty': line.suggested_by or 0.0,
                'date_planned': datetime.today(),
                'purchase_id': purchase and purchase[0].id or False,
                'location_id': line.location_id and line.location_id.id or False,
                'picking_type_id': purchase and purchase[0].picking_type_id.id or False,
            }
            lines.append((0, 0, d1))
        return lines

    line_ids = fields.One2many(
        'po.generatorline', 'parent_id',
        string='Procurement Request Lines', default=get_lines)
    cost_select = fields.Selection([
        ('standard_cost', 'Standard Cost'),
        ('supplier_cost', 'Vendor Price'),
        ('last_cost', 'Last Price')
    ], string='Cost Method', help="""(('standard cost', 'Cost Price from Product Procurement tab'),
        ('Vendor Price', 'Vendor Cost from Product Vendor List'),
        ('last_cost', 'Last Purchase Price'))""", required=True, default="standard_cost")

    def update_cost(self):
        supp_obj = self.env['product.supplierinfo']
        pur_line = self.env['purchase.order.line']
        for line in self.line_ids:
            cost_method = line.cost_select or self.cost_select
            if cost_method == 'standard_cost':
                line.cost_price = line.product_id.standard_price
            if cost_method == 'supplier_cost':
                s_line = supp_obj.search(
                    [('name', '=', line.vendor_id.id), ('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])
                line.cost_price = s_line and s_line[0].price or 0
            if cost_method == 'last_cost':
                p_line = pur_line.search([('product_id', '=', line.product_id.id),
                                          ('order_id.partner_id', '=', line.vendor_id.id),
                                          ('order_id.state', 'not in', ('draft', 'sent', 'cancel'))],
                                         order="date_planned desc")
                line.cost_price = p_line and p_line[0].price_unit or 0
        result = self.env.ref('thinksoft_purchase_review.po_generator_tree_action').read()
        result[0]['res_id'] = self.id
        return result[0]

    #
    def validate(self):
        vals = {}
        purchase_obj = self.env['purchase.order']
        supp_obj = self.env['product.supplierinfo']
        purchaseline_obj = self.env.get('purchase.order.line')
        purchase_field = purchase_obj.fields_get()
        purchase_default = purchase_obj.default_get(purchase_field)
        for val in self.line_ids:
            if val.purchase_id and val.procurement_qty > 0:
                vals = {
                    'product_id': val.product_id.id,
                    'name': val.product_id.display_name,
                    'product_qty': val.procurement_qty,
                    'order_id': val.purchase_id.id,
                    'product_uom': val.uom_id.id,
                    'price_unit': val.cost_price,
                    'date_planned': val.date_planned,
                    #                     'box_qty': val.product_id.box_qty,
                    'qty_edm_available': val.product_id.with_context({'location': 'Stock.e'}).virtual_available,
                    'qty_clgy_available': val.product_id.with_context({'location': 'Stock.c'}).virtual_available,
                }
                purchaseline_obj.create(vals)
            if val.vendor_id:
                flag = True
                if val.vendor_ids:
                    if val.vendor_id not in val.vendor_ids.ids:
                        flag = False
                elif not val.vendor_ids:
                    flag = False
                if flag == False:
                    supp_obj.create({'product_tmpl_id': val.product_id.product_tmpl_id.id,
                                     'price': val.cost_price,
                                     'name': val.vendor_id.id})
            if not val.purchase_id and val.procurement_qty > 0:
                purchase = purchase_obj.search([('partner_id', '=', val.vendor_id.id),
                                                ('state', 'in', ('draft', 'sent')),
                                                ('picking_type_id', '=', val.picking_type_id.id)])
                if not purchase:
                    purchase_default_val = purchase_default.copy()
                    purchase_default_val.update({'partner_id': val.vendor_id.id,
                                                 'picking_type_id': val.picking_type_id.id})
                    purchase = [purchase_obj.create(purchase_default_val)]
                vals = {
                    'product_id': val.product_id.id,
                    'name': val.product_id.display_name,
                    'product_qty': val.procurement_qty,
                    'order_id': purchase and purchase[0].id,
                    'product_uom': val.uom_id.id,
                    'price_unit': val.cost_price,
                    'date_planned': val.date_planned,
                    #                     'box_qty': val.product_id.box_qty,
                    #                     'qty_edm_available': val.product_id.qty_edm_available,
                    #                     'qty_clgy_available': val.product_id.qty_clgy_available,
                }
                purchaseline_obj.create(vals)

        return True


class PoGeneratorLine(models.TransientModel):
    _name = 'po.generatorline'
    _description = 'Lines of the wizard to request procurements'

    def get_vendor_list(self):
        if self.product_id:
            vendors = [vendor.name.id for vendor in self.product_id.seller_ids]
            if vendors:
                self.vendor_ids = [(6, 0, vendors)]

    @api.onchange('vendor_id', 'picking_type_id')
    def onchange_vendor_id(self):
        if self.vendor_id or self.picking_type_id:
            po = self.env['purchase.order'].search(
                [('partner_id', '=', self.vendor_id.id), ('state', 'in', ('draft', 'sent',))])
            if self.picking_type_id and po:
                po = self.env['purchase.order'].search(
                    [('id', 'in', po.ids), ('picking_type_id', '=', self.picking_type_id.id)])
                if po:
                    self.purchase_id = po[0].id
                if not po:
                    self.purchase_id = False
            if not po:
                self.purchase_id = False

    po_id = fields.Many2one('purchase.order', string='PO Number')
    vendor_ids = fields.Many2many('res.partner', compute="get_vendor_list", string="Vendors")
    vendor_id = fields.Many2one('res.partner', 'Vendor')
    parent_id = fields.Many2one('po.generator', string='Parent')
    product_id = fields.Many2one('product.product', string='Product')
    qty_available = fields.Float(string='Quantity Available', digits='Product Unit of Measure')
    outgoing_qty = fields.Float(digits='Product Unit of Measure')
    incoming_qty = fields.Float(string='Incoming Quantity', digits='Product Unit of Measure')
    procurement_qty = fields.Float(string='Suggested Buy', digits='Product Unit of Measure', required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', )
    #     warehouse_id = fields.Many2one(
    #         'stock.warehouse', string='Warehouse', required=True)
    date_planned = fields.Date(string='Planned Date', required=True)
    cost_price = fields.Float(string='Purchase Price', digits='Product Price')
    cost_select = fields.Selection([
        ('standard_cost', 'Standard Price'),
        ('supplier_cost', 'Vendor Price'),
        ('last_cost', 'Last Price')
    ], string='Cost Method', )
    location_id = fields.Many2one('stock.location', 'Location')
    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    picking_type_id = fields.Many2one('stock.picking.type', 'Source Receive')

#     def onchange_cost_amount(self):
#         res = {}
#         res['cost_price'] = self.env.get('po.generator').get_cost_price(cr, uid, product_id, cost_select, po_id, context)
#         return {'value': res}
