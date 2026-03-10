from odoo import api, models


class ReportQuotation(models.AbstractModel):
    _name = "report.thinksoft_reports.report_thinksoft_quotation_template"
    _description = "Sale Quote/Order"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        sale_order_lines_map = {}

        for order in docs:
            cleaned = []
            # Sort lines by sequence and ID to maintain proper order
            sorted_lines = order.order_line.sorted(key=lambda l: (l.sequence, l.id))
            
            for line in sorted_lines:
                # Check if this is a note line (used as section header)
                if line.display_type == 'line_note':
                    cleaned.append({
                        'line': line,
                        'is_section': True,
                        'cleaned_description': ''
                    })
                elif not line.display_type:  # Regular product line
                    description = line.name or ''
                    product_name = (line.product_id.name or '').strip()
                    product_ref = (f"[{line.product_id.default_code}]" or '')
                    name_removed = description.replace(product_name, '') if product_name else description
                    name_ref_removed = name_removed.replace(product_ref, '') if product_ref else name_removed
                    cleaned_description = (name_ref_removed or '').strip()
                    cleaned.append({
                        'line': line,
                        'is_section': False,
                        'cleaned_description': cleaned_description
                    })
                # Skip section lines and other display types
            sale_order_lines_map[order.id] = cleaned

        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docs,
            'sale_order_lines_map': sale_order_lines_map,
        }
