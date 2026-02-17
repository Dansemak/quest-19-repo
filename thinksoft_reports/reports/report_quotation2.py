from odoo import api, models




class ReportQuotation(models.AbstractModel):
    _name = "report.thinksoft_reports.report_thinksoft_quotation_template"
    _description = "Sale Quote/Order"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        # sale_order_lines_map = {}

        for order in docs:
            prepared_lines = []

            for line in order.order_line.with_context(include_section_lines=True):

                # SECTION
                if line.display_type == 'line_section':
                    prepared_lines.append({
                        'type': 'section',
                        'name': line.name,
                    })
                    continue

                # NOTE (skip if you want)
                if line.display_type == 'line_note':
                    continue

                # PRODUCT
                description = line.name or ''
                product_name = (line.product_id.name or '').strip()
                product_ref = f"[{line.product_id.default_code}]" if line.product_id.default_code else ''

                cleaned = description.replace(product_name, '').replace(product_ref, '').strip()

                prepared_lines.append({
                    'type': 'product',
                    'line': line,
                    'cleaned_description': cleaned,
                })

            # sale_order_lines_map[order.id] = prepared_lines

        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docs,
            # 'sale_order_lines_map': sale_order_lines_map,
        }