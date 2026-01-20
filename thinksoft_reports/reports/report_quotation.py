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
            for line in order.order_line:
                description = line.name or ''
                product_name = (line.product_id.display_name or '').strip()
                cleaned_description = description.replace(product_name, '') if product_name else description
                cleaned_description = (cleaned_description or '').strip()
                cleaned.append({'line': line, 'cleaned_description': cleaned_description})
            sale_order_lines_map[order.id] = cleaned

        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docs,
            'sale_order_lines_map': sale_order_lines_map,
        }
