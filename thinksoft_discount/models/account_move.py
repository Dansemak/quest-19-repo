from odoo import models
from contextlib import contextmanager


class AccountMove(models.Model):
    _inherit = 'account.move'

    # 2026-02-20
    # _sync_tax_lines is copied directly from https://github.com/odoo/odoo/blob/19.0/addons/account/models/account_move.py#L3252
    # (The line the link points to may move over time but _sync_tax_lines is in account_move.py)
    # 
    # This is to hijack base_lines_values to temporarily set 'price_unit' to 'price_reduce_taxexcl' and 'discount' to '0.0' so
    # that it can do the calculations with the rounded discounted unit price instead.
    # The only modified part of _sync_tax_lines is the section titled 'Hijack'.

    @contextmanager
    def _sync_tax_lines(self, container):
        AccountTax = self.env['account.tax']
        fake_base_line = AccountTax._prepare_base_line_for_taxes_computation(None)

        def get_base_lines(move):
            return move.line_ids.filtered(lambda line: line.display_type in ('product', 'epd', 'rounding', 'cogs', 'non_deductible_product'))

        def get_tax_lines(move):
            return move.line_ids.filtered('tax_repartition_line_id')

        def get_value(record, field):
            return record._fields[field].convert_to_write(record[field], record)

        def get_tax_line_tracked_fields(line):
            return ('amount_currency', 'balance', 'analytic_distribution')

        def get_base_line_tracked_fields(line):
            grouping_key = AccountTax._prepare_base_line_grouping_key(fake_base_line)
            if line.move_id.is_invoice(include_receipts=True):
                extra_fields = ['price_unit', 'quantity', 'discount']
            else:
                extra_fields = ['amount_currency']
            return list(grouping_key.keys()) + extra_fields

        def field_has_changed(values, record, field):
            return get_value(record, field) != values.get(record, {}).get(field)

        def get_changed_lines(values, records, fields=None):
            return (
                record
                for record in records
                if record not in values
                or any(field_has_changed(values, record, field) for field in values[record] if not fields or field in fields)
            )

        def any_field_has_changed(values, records, fields=None):
            return any(record for record in get_changed_lines(values, records, fields))

        def is_write_needed(line, values):
            return any(
                self.env['account.move.line']._fields[fname].convert_to_write(line[fname], self) != values[fname]
                for fname in values
            )

        moves_values_before = {
            move: {
                field: get_value(move, field)
                for field in ('currency_id', 'partner_id', 'move_type', 'invoice_currency_rate', 'invoice_date')
            }
            for move in container['records']
            if move.state == 'draft'
        }
        base_lines_values_before = {
            move: {
                line: {
                    field: get_value(line, field)
                    for field in get_base_line_tracked_fields(line)
                }
                for line in get_base_lines(move)
            }
            for move in container['records']
        }
        tax_lines_values_before = {
            move: {
                line: {
                    field: get_value(line, field)
                    for field in get_tax_line_tracked_fields(line)
                }
                for line in get_tax_lines(move)
            }
            for move in container['records']
        }
        yield

        to_delete = []
        to_create = []
        for move in container['records']:
            if move.state != 'draft':
                continue

            tax_lines = get_tax_lines(move)
            base_lines = get_base_lines(move)
            move_tax_lines_values_before = tax_lines_values_before.get(move, {})
            move_base_lines_values_before = base_lines_values_before.get(move, {})
            if (
                move.is_invoice(include_receipts=True)
                and (
                    field_has_changed(moves_values_before, move, 'currency_id')
                    or field_has_changed(moves_values_before, move, 'move_type')
                )
            ):
                # Changing the type of an invoice using 'switch to refund' feature or just changing the currency.
                round_from_tax_lines = False
            elif any(line not in base_lines for line, values in move_base_lines_values_before.items() if values['tax_ids']):
                # Removed a base line affecting the taxes.
                round_from_tax_lines = any_field_has_changed(move_tax_lines_values_before, tax_lines)
            elif field_has_changed(moves_values_before, move, 'invoice_currency_rate') and not field_has_changed(moves_values_before, move, 'invoice_date'):
                # Changing the rate should preserve the tax amounts in foreign currency but reapply the currency rate.
                round_from_tax_lines = 'reapply_currency_rate'
            elif changed_lines := list(get_changed_lines(move_base_lines_values_before, base_lines)):
                # A base line has been modified.
                round_from_tax_lines = (
                    # The changed lines don't affect the taxes.
                    all(
                        not line.tax_ids and not move_base_lines_values_before.get(line, {}).get('tax_ids')
                        for line in changed_lines
                    )
                    # Keep the tax lines amounts if an amount has been manually computed.
                    or (
                        list(move_tax_lines_values_before) != list(tax_lines)
                        or any(
                            self.env.is_protected(line._fields[fname], line)
                            for line in tax_lines
                            for fname in move_tax_lines_values_before[line]
                        )
                    )
                )

                # If the move has been created with all lines including the tax ones and the balance/amount_currency are provided on
                # base lines, we don't need to recompute anything.
                if (
                    round_from_tax_lines
                    and any(line[field] for line in changed_lines for field in ('amount_currency', 'balance'))
                ):
                    continue
            else:
                continue

            base_lines_values, tax_lines_values = move._get_rounded_base_and_tax_lines(round_from_tax_lines=round_from_tax_lines)
            ############################## Hijack ##############################
            for base_line in base_lines_values:
                record = base_line.get('record')
                if record and getattr(record, 'price_reduce_taxexcl', False):
                    base_line['price_unit'] = record.price_reduce_taxexcl
                    base_line['discount'] = 0.0
            ####################################################################
            AccountTax._add_accounting_data_in_base_lines_tax_details(base_lines_values, move.company_id, include_caba_tags=move.always_tax_exigible)
            tax_results = AccountTax._prepare_tax_lines(base_lines_values, move.company_id, tax_lines=tax_lines_values)
            non_deductible_tax_line = move.line_ids.filtered(lambda line: line.display_type == 'non_deductible_tax')
            non_deductible_lines_values = [
                line_values
                for line_values in base_lines_values
                if line_values['special_type'] == 'non_deductible'
                and line_values['tax_ids']
            ]

            if not non_deductible_lines_values and non_deductible_tax_line:
                to_delete.append(non_deductible_tax_line.id)

            elif non_deductible_lines_values:
                non_deductible_tax_values = {
                    'tax_amount': 0.0,
                    'tax_amount_currency': 0.0,
                }
                for line_values in non_deductible_lines_values:
                    non_deductible_tax_values['tax_amount'] += -line_values['sign'] * (line_values['tax_details']['total_included'] - line_values['tax_details']['total_excluded'])
                    non_deductible_tax_values['tax_amount_currency'] += -line_values['sign'] * (line_values['tax_details']['total_included_currency'] - line_values['tax_details']['total_excluded_currency'])

                # Update the non-deductible tax lines values
                non_deductable_tax_line_values = {
                    'move_id': move.id,
                    'account_id': (
                        non_deductible_tax_line.account_id
                        or move.journal_id.non_deductible_account_id
                        or move.journal_id.default_account_id
                    ).id,
                    'display_type': 'non_deductible_tax',
                    'name': _('private part (taxes)'),
                    'balance': non_deductible_tax_values['tax_amount'],
                    'amount_currency': non_deductible_tax_values['tax_amount_currency'],
                    'sequence': max(move.line_ids.mapped('sequence')) + 1,
                }
                if non_deductible_tax_line:
                    tax_results['tax_lines_to_update'].append((
                        {'record': non_deductible_tax_line},
                        'unused_grouping_key',
                        {
                            'amount_currency': non_deductable_tax_line_values['amount_currency'],
                            'balance': non_deductable_tax_line_values['balance'],
                        }
                    ))
                else:
                    to_create.append(non_deductable_tax_line_values)

            for base_line, to_update in tax_results['base_lines_to_update']:
                line = base_line['record']
                if is_write_needed(line, to_update):
                    line.write(to_update)

            for tax_line_vals in tax_results['tax_lines_to_delete']:
                to_delete.append(tax_line_vals['record'].id)

            for tax_line_vals in tax_results['tax_lines_to_add']:
                to_create.append({
                    **tax_line_vals,
                    'display_type': 'tax',
                    'move_id': move.id,
                })

            for tax_line_vals, _grouping_key, to_update in tax_results['tax_lines_to_update']:
                line = tax_line_vals['record']
                if is_write_needed(line, to_update):
                    line.write(to_update)

        if to_delete:
            self.env['account.move.line'].browse(to_delete).with_context(dynamic_unlink=True).unlink()
        if to_create:
            self.env['account.move.line'].create(to_create)

    # 2026-02-20
    # _get_rounded_base_and_tax_lines is copied directly from 
    # https://github.com/odoo/odoo/blob/19.0/addons/account/models/account_move.py#L1757
    # (The line the link points to may move over time but _get_rounded_base_and_tax_lines is in account_move.py)
    # 
    # This is to hijack base_lines to temporarily set 'price_unit' to 'price_reduce_taxexcl' and 'discount' to '0.0'
    # so that it can do the calculations with the rounded discounted unit price instead.
    # The only modified parts of _get_rounded_base_and_tax_lines is the section titled 'Hijack'.

    def _get_rounded_base_and_tax_lines(self, round_from_tax_lines=True):
        """ Small helper to extract the base and tax lines for the taxes computation from the current move.
        The move could be stored or not and could have some features generating extra journal items acting as
        base lines for the taxes computation (e.g. epd, rounding lines).

        :param round_from_tax_lines:    Indicate if the manual tax amounts of tax journal items should be kept or not.
                                        It only works when the move is stored.
        :return:                        A tuple <base_lines, tax_lines> for the taxes computation.
        """
        self.ensure_one()
        AccountTax = self.env['account.tax']
        is_invoice = self.is_invoice(include_receipts=True)

        if self.id or not is_invoice:
            base_amls = self.line_ids.filtered(lambda line: line.display_type == 'product')
        else:
            base_amls = self.invoice_line_ids.filtered(lambda line: line.display_type == 'product')
        base_lines = [self._prepare_product_base_line_for_taxes_computation(line) for line in base_amls]

        tax_lines = []
        if self.id:
            # The move is stored so we can add the early payment discount lines directly to reduce the
            # tax amount without touching the untaxed amount.
            epd_amls = self.line_ids.filtered(lambda line: line.display_type == 'epd')
            base_lines += [self._prepare_epd_base_line_for_taxes_computation(line) for line in epd_amls]
            cash_rounding_amls = self.line_ids \
                .filtered(lambda line: line.display_type == 'rounding' and not line.tax_repartition_line_id)
            base_lines += [self._prepare_cash_rounding_base_line_for_taxes_computation(line) for line in cash_rounding_amls]
            non_deductible_base_lines = self.line_ids.filtered(lambda line: line.display_type in ('non_deductible_product', 'non_deductible_product_total'))
            base_lines += [self._prepare_non_deductible_base_line_for_taxes_computation(line) for line in non_deductible_base_lines]
            ############################## Hijack ##############################
            for base_line in base_lines:
                record = base_line.get('record')
                if record and getattr(record, 'price_reduce_taxexcl', False):
                    base_line['price_unit'] = record.price_reduce_taxexcl
                    base_line['discount'] = 0.0
            ####################################################################
            AccountTax._add_tax_details_in_base_lines(base_lines, self.company_id)
            tax_amls = self.line_ids.filtered('tax_repartition_line_id')
            tax_lines = [self._prepare_tax_line_for_taxes_computation(tax_line) for tax_line in tax_amls]
            if round_from_tax_lines == 'reapply_currency_rate':
                for tax_line in tax_lines:
                    rate = tax_line['record'].currency_rate
                    if rate:
                        tax_line['balance'] = self.company_currency_id.round(tax_line['amount_currency'] / rate)
            AccountTax._round_base_lines_tax_details(base_lines, self.company_id, tax_lines=tax_lines if round_from_tax_lines else [])
        else:
            # The move is not stored yet so the only thing we have is the invoice lines.
            base_lines += self._prepare_epd_base_lines_for_taxes_computation_from_base_lines(base_amls)
            base_lines += self._prepare_non_deductible_base_lines_for_taxes_computation_from_base_lines(base_amls)
            ############################## Hijack ##############################
            for base_line in base_lines:
                record = base_line.get('record')
                if record and getattr(record, 'price_reduce_taxexcl', False):
                    base_line['price_unit'] = record.price_reduce_taxexcl
                    base_line['discount'] = 0.0
            ####################################################################
            AccountTax._add_tax_details_in_base_lines(base_lines, self.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, self.company_id)
        return base_lines, tax_lines
