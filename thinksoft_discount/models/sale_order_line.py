from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_reduce_taxexcl = fields.Monetary(compute="_compute_amount")

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_ids')
    def _compute_amount(self):
        AccountTax = self.env['account.tax']
        for line in self:
            ##################### Set price_reduce_taxexcl #####################
            if line.discount > 0.0:
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
