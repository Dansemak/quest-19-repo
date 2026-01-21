# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProcurementBatchGenerator(models.TransientModel):
    _name = 'procurement.batch.generator'
    _description = 'Wizard to create procurements from product tree'

    po_id = fields.Many2one(
        'purchase.order', string='PO Number', required=True)

    @api.model
    def _default_lines(self):
        assert isinstance(self.env.context['active_ids'], list),\
            "context['active_ids'] must be a list"
        assert self.env.context['active_model'] in ['product.product','stock.warehouse.orderpoint','sale.order.line', 'purchase.review.report'],\
            "context['active_model'] must be 'product.product'"
        res = []
#         warehouses = self.env['stock.warehouse'].search(
#             [('company_id', '=', self.env.user.company_id.id)])
#         warehouse_id = warehouses and warehouses[0].id or False
        today = fields.Date.context_today(self)
        if self.env.context['active_model'] == 'product.product':
            for product in self.env['product.product'].browse(
                    self.env.context['active_ids']):

                res.append((0,0,{
                    'product_id': product.id,
                    'uom_id': product.uom_id.id,
                    'procurement_qty': 0.0,
                    'date_planned': today,
                    'cost_select':'standard_cost',
                    'cost_price':product.standard_price
                    }))
        if self.env.context['active_model'] == 'stock.warehouse.orderpoint':
            for product in self.env['stock.warehouse.orderpoint'].browse(
                    self.env.context['active_ids']):

                res.append((0,0,{
                    'product_id': product.product_id.id,
                    'uom_id': product.product_id.uom_id.id,
                    'procurement_qty': 0.0,
                    'date_planned': today,
                    'cost_select':'standard_cost',
                    'cost_price':product.product_id.standard_price,
                    }))
        if self.env.context['active_model'] == 'purchase.review.report':
            for product in self.env['stock.warehouse.orderpoint'].browse(
                    self.env.context['active_ids']):

                res.append((0,0,{
                    'product_id': product.product_id.id,
                    'uom_id': product.product_id.uom_id.id,
                    'procurement_qty': 0.0,
                    'date_planned': today,
                    'cost_select':'standard_cost',
                    'cost_price':product.product_id.standard_price,
                    }))
        if self.env.context['active_model'] == 'sale.order.line':
            for product in self.env['sale.order.line'].browse(
                    self.env.context['active_ids']):

                res.append((0,0,{
                    'product_id': product.product_id.id,
                    'uom_id': product.product_id.uom_id.id,
                    'procurement_qty': product.product_uom_qty,
                    'date_planned': today,
                    'cost_select':'standard_cost',
                    'cost_price':product.product_id.standard_price,
                    }))
        return res

    line_ids = fields.One2many(
        'procurement.batch.generator.line', 'parent_id',
        string='Procurement Request Lines', default=_default_lines)

    def validate(self):
        purchaseline_obj = self.env.get('purchase.order.line')
        for val in self.line_ids:
            if val.product_id:
                result = purchaseline_obj.create({
                    'product_id': val.product_id.id,
                    'name': val.product_id.description_picking or val.product_id.display_name,
                    'product_qty': val.procurement_qty,
                    'order_id': val.parent_id.po_id.id,
                    'product_uom_id': val.uom_id.id,
                    'price_unit': val.cost_price,
                    'date_planned': val.date_planned,
                    })
            if self.env.context['active_model'] == 'sale.order.line':
                if result:
                    for product in self.env['sale.order.line'].browse(self.env.context['active_ids']):
                        if product.product_id.id == val.product_id.id:
                            product.po_number = val.parent_id.po_id
                            continue
        return True


class ProcurementBatchGeneratorLine(models.TransientModel):
    _name = 'procurement.batch.generator.line'
    _description = 'Lines of the wizard to request procurements'

    parent_id = fields.Many2one(
        'procurement.batch.generator', string='Parent')
    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    procurement_qty = fields.Float(
        string='Requested Quantity',
        digits='Product Unit of Measure', required=True)
    uom_id = fields.Many2one(
        'uom.uom', string='Unit of Measure', required=True)
    date_planned = fields.Date(string='Planned Date', required=True)
    cost_price = fields.Float(
        string='Unit Cost',
        digits='Product Price')
    cost_select = fields.Selection([
        ('standard_cost', 'Cost Price from Product Procurement tab'),
        ('supplier_cost', 'Supplier Cost from Product Vendor List'),
        ('last_cost', 'Cost Last Paid')
        ], string='Cost', required=True,default='standard_cost')
    cost_subtotal = fields.Float(compute="get_subtotal", string="Subtotal")

    @api.onchange('product_id','cost_select','parent_id')
    def onchange_cost_amount(self):
        product_br = self.product_id
        if self.cost_select == 'standard_cost':
            self.cost_price = product_br.standard_price
        elif self.cost_select == 'supplier_cost':
            purchase_br = self.parent_id.po_id
            supplier_br = self.env.get('product.supplierinfo')
            if purchase_br:
                supplier_id = supplier_br.search([('name', '=', purchase_br.partner_id.id), ('product_tmpl_id', '=', product_br.product_tmpl_id.id)], limit=1)
                self.cost_price = supplier_id and supplier_id.price or 0
        elif self.cost_select == 'last_cost':
            if product_br:
                account_invoice_line_obj = self.env.get('account.move.line')
                acc_line_id = account_invoice_line_obj.search([('product_id', '=', product_br.id), ('move_id.state', '=', 'posted')],order="id desc",limit=1)
                self.cost_price = acc_line_id and acc_line_id.price_unit

    @api.depends('cost_price','procurement_qty')
    def get_subtotal(self):
        for line in self:
            line.cost_subtotal = line.cost_price * line.procurement_qty

