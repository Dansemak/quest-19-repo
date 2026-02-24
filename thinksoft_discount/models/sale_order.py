from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def hijack_base_lines(self, base_lines):
        """
        This takes the 'base_lines' and sets 'price_unit' to 'price_reduce_taxexcl' and
        'discount' to '0.0' so that it can do all the calculations with the rounded
        discounted unit price (price_reduce_taxexcl) instead.
        """
        for base_line in base_lines:
            record = base_line.get('record')
            if record and getattr(record, 'price_reduce_taxexcl', None) is not None:
                base_line['price_unit'] = record.price_reduce_taxexcl
                base_line['discount'] = 0.0
        return base_lines

    # 2026-02-24
    # _compute_amounts is copied directly from https://github.com/odoo/odoo/blob/19.0/addons/sale/models/sale_order.py#L512
    # (The line the link points to may move over time but _compute_amounts is in sale_order.py)
    # 
    # This is to hijack base_lines to temporarily set 'price_unit' to 'price_reduce_taxexcl'
    # and 'discount' to '0.0' so that it can do the calculations with the rounded discounted
    # unit price instead.
    # The only modified part of _compute_amounts is the section titled 'Hijack'.
    @api.depends('order_line.price_subtotal', 'currency_id', 'company_id', 'payment_term_id')
    def _compute_amounts(self):
        AccountTax = self.env['account.tax']
        for order in self:
            order_lines = order._get_priced_lines()
            base_lines = [line._prepare_base_line_for_taxes_computation() for line in order_lines]
            base_lines += order._add_base_lines_for_early_payment_discount()
            ################################## Hijack ##################################
            base_lines = order.hijack_base_lines(base_lines)
            ############################################################################
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )
            order.amount_untaxed = tax_totals['base_amount_currency']
            order.amount_tax = tax_totals['tax_amount_currency']
            order.amount_total = tax_totals['total_amount_currency']

    # 2026-02-24
    # _compute_tax_totals is copied directly from https://github.com/odoo/odoo/blob/19.0/addons/sale/models/sale_order.py#L792
    # (The line the link points to may move over time but _compute_tax_totals is in sale_order.py)
    # 
    # This is to hijack base_lines to temporarily set 'price_unit' to 'price_reduce_taxexcl'
    # and 'discount' to '0.0' so that it can do the calculations with the rounded discounted
    # unit price instead.
    # The only modified part of _compute_tax_totals is the section titled 'Hijack'.
    @api.depends_context('lang')
    @api.depends('order_line.price_subtotal', 'currency_id', 'company_id', 'payment_term_id')
    def _compute_tax_totals(self):
        AccountTax = self.env['account.tax']
        for order in self:
            order_lines = order._get_priced_lines()
            base_lines = [line._prepare_base_line_for_taxes_computation() for line in order_lines]
            base_lines += order._add_base_lines_for_early_payment_discount()
            ################################## Hijack ##################################
            base_lines = order.hijack_base_lines(base_lines)
            ############################################################################
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            order.tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )
