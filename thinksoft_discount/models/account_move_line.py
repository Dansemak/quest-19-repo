import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    price_reduce_taxexcl = fields.Monetary(string='Disc Unit Price', compute="_compute_price_unit", store=True, readonly=False, precompute=True)
    # price_unit = fields.Float(
    #     string='Unit Price',
    #     compute="_compute_price_unit", store=True, readonly=False, precompute=True,
    #     digits='Product Price',
    # )

    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id')
    def _compute_price_unit(self):
        super(AccountMoveLine, self)._compute_price_unit()
        for line in self:
            if line.discount > 0.0:
                line.price_reduce_taxexcl = round(line.price_unit * (1 - (line.discount / 100.0)), 2)
            else:
                line.price_reduce_taxexcl = line.price_unit


    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id')
    def _compute_totals(self):
        """ Compute 'price_subtotal' / 'price_total' outside of `_sync_tax_lines` because those values must be visible for the
        user on the UI with draft moves and the dynamic lines are synchronized only when saving the record.
        """
        AccountTax = self.env['account.tax']
        for line in self:
            # TODO remove the need of cogs lines to have a price_subtotal/price_total
            if line.display_type not in ('product', 'cogs', 'non_deductible_product', 'non_deductible_product_total') or not line.move_id:
                line.price_total = line.price_subtotal = False
                continue

            company = line.company_id or self.env.company
            base_line = line.move_id._prepare_product_base_line_for_taxes_computation(line)
            ############################################################################
            base_line['price_unit'] = line.price_reduce_taxexcl
            base_line['discount'] = 0.0
            ############################################################################
            _logger.warning("####CUSTOM###############################################################################################################")
            _logger.warning(f"BASE LINE: {base_line}")
            _logger.warning("#########################################################################################################################")
            AccountTax._add_tax_details_in_base_line(base_line, company)
            AccountTax._round_base_lines_tax_details([base_line], company)
            line.price_subtotal = base_line['tax_details']['total_excluded_currency']
            line.price_total = base_line['tax_details']['total_included_currency']

    # def _compute_totals(self):
    #     for line in self:
    #         if line.discount > 0.0:
    #             line.price_reduce_taxexcl = round(line.price_unit * (1 - (line.discount / 100.0)), 2)
    #         else:
    #             line.price_reduce_taxexcl = line.price_unit

    #         original_price_unit = line.price_unit
    #         original_discount = line.discount

    #         line.price_unit = line.price_reduce_taxexcl
    #         line.discount = 0.0

    #         super(SaleOrderLine, self)._compute_amount()

    #         line.price_unit = original_price_unit
    #         line.discount = original_discount
