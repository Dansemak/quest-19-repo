from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # This switches and repurposes the compute field use to _compute_amount
    price_reduce_taxexcl = fields.Monetary(compute="_compute_amount")

    # 2026-02-20
    # _compute_amount is copied directly from https://github.com/odoo/odoo/blob/19.0/addons/sale/models/sale_order_line.py#L844
    # (The line the link points to may move over time but _compute_amount is in sale_order_line.py)
    # 
    # It sets the price_reduce_taxexcl field and it also hijacks base_line to temporarily
    # set 'price_unit' to 'price_reduce_taxexcl' and 'discount' to '0.0' so that it can 
    # do the calculations with the rounded discounted unit price instead.
    # The only modified parts of _compute_amount is the sections 'Set price_reduce_taxexcl'
    # and 'Hijack'.
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_ids')
    def _compute_amount(self):
        AccountTax = self.env['account.tax']
        for line in self:
            ##################### Set price_reduce_taxexcl #####################
            if line.discount != 0.0:
                line.price_reduce_taxexcl = round(line.price_unit * (1 - (line.discount / 100.0)), 2)
            else:
                line.price_reduce_taxexcl = line.price_unit
            ####################################################################
            
            company = line.company_id or self.env.company
            base_line = line._prepare_base_line_for_taxes_computation()
            ############################## Hijack ##############################
            base_line['price_unit'] = line.price_reduce_taxexcl
            base_line['discount'] = 0.0
            ####################################################################
            AccountTax._add_tax_details_in_base_line(base_line, company)
            AccountTax._round_base_lines_tax_details([base_line], company)
            line.price_subtotal = base_line['tax_details']['total_excluded_currency']
            line.price_total = base_line['tax_details']['total_included_currency']
            line.price_tax = line.price_total - line.price_subtotal
