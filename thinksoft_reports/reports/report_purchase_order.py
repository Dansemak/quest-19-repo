from odoo import api, models


class ReportPurchaseOrder(models.AbstractModel):
    _name = "report.thinksoft_reports.purchase_order_template"
    _description = "RFQ/Purchase Order"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)
        purchase_order_lines_map = {}

        for order in docs:
            cleaned = []
            for line in order.order_line:
                description = line.name or ''
                product_name = (line.product_id.name or '').strip()
                product_ref = (f"[{line.product_id.default_code}]" or '')
                name_removed = description.replace(product_name, '') if product_name else description
                name_ref_removed = name_removed.replace(product_ref, '') if product_ref else name_removed
                cleaned_description = (name_ref_removed or '').strip()
                cleaned.append({'line': line, 'cleaned_description': cleaned_description})
            purchase_order_lines_map[order.id] = cleaned

        return {
            'doc_ids': docids,
            'doc_model': 'purchase.order',
            'docs': docs,
            'purchase_order_lines_map': purchase_order_lines_map,
        }
