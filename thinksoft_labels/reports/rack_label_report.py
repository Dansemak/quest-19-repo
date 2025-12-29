from odoo import api, models
import re

class RackLabel12x4Report(models.AbstractModel):
    # _inherit = 'product.template'
    _name = 'report.thinksoft_labels.product_label_12x4'
    _description = "12x4 Product Label for Rack"

    # def remove_html_tags(self, text):
    #     if not text:
    #         return ''
    #     return re.sub(r'<[^>]*>', ' ', text).strip()

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     docs = self.env['product.template'].browse(docids)
    #     tagless_description = {
    #         product.id: self.remove_html_tags(product.description or '')
    #         for product in docs
    #     }

    #     return {
    #         'doc_ids': docids,
    #         'doc_model': 'product.template',
    #         'docs': docs,
    #         'tagless_description': tagless_description,
    #     }

    def remove_html_tags(self, text):
        """Remove HTML tags from a string."""
        tagless_string = re.sub('<[^<]+?>', ' ', text)
        return tagless_string

    def _get_report_values(self, docids, data=None):
        docs = self.env['product.template'].browse(docids)

        tagless_description = {}
        for product in docs:
            if product.description:
                tagless_description[product.id] = self.remove_html_tags(product.description)

        return {
            'doc_ids': docids,
            'doc_model': 'product.template',
            'docs': docs,
            'tagless_description': tagless_description,
        }