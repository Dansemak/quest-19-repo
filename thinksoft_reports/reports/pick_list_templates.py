from odoo import api, models


class PickList(models.AbstractModel):
    _name = "report.thinksoft_reports.pick_list_template"
    _description = "Pick List"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        stock_picking_lines_map = {}

        for pick in docs:
            cleaned = []
            for move_id in pick.move_ids:
                description = move_id.description_picking or ''
                product_name = (move_id.product_id.name or '').strip()
                product_ref = (f"[{move_id.product_id.default_code}]" or '')
                name_removed = description.replace(product_name, '') if product_name else description
                name_ref_removed = name_removed.replace(product_ref, '') if product_ref else name_removed
                cleaned_description = (name_ref_removed or '').strip()
                cleaned.append({'line': move_id, 'cleaned_description': cleaned_description})
            stock_picking_lines_map[pick.id] = cleaned

        return {
            'doc_ids': docids,
            'doc_model': 'stock.picking',
            'docs': docs,
            'stock_picking_lines_map': stock_picking_lines_map,
        }
