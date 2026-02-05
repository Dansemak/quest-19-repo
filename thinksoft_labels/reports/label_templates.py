from odoo import api, models


class FourXFourLabel(models.AbstractModel):
    _name = "report.thinksoft_labels.label_4x4_template"
    _description = "4x4 Label"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.move'].browse(docids)
        cleaned_description = {}

        for move in docs:
            description = move.description_picking or ''
            product_name = move.product_id.name.strip()
            product_ref = f"[{move.product_id.default_code}]"

            name_removed = description.replace(product_name, '') if product_name else description
            name_ref_removed = name_removed.replace(product_ref, '') if product_ref else name_removed
            cleaned_description[move.id] = name_ref_removed.strip()

        return {
            'doc_ids': docids,
            'doc_model': 'stock.move',
            'docs': docs,
            'cleaned_description': cleaned_description,
        }
