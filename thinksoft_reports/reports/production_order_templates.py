from odoo import api, models


class ProductionOrderTemplate(models.AbstractModel):
    _name = "report.thinksoft_reports.production_order"
    _description = "Production Order"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['mrp.production'].browse(docids)
        sale_line_id = None
        product_description = None

        def find_first_parent_sale_line_id(manufacturing_order):
            if not manufacturing_order.production_group_id.parent_ids:
                return manufacturing_order.sale_line_id
            else:
                return find_first_parent_sale_line_id(manufacturing_order.production_group_id.parent_ids.production_ids[0])

        def get_product_description(manufacturing_order):
            if not manufacturing_order.production_group_id.parent_ids:
                return manufacturing_order.sale_line_id.product_id.description
            else:
                return manufacturing_order.product_id.description

        for order in docs:
            sale_line_id = find_first_parent_sale_line_id(order)
            product_description = get_product_description(order)

        return {
            'doc_ids': docids,
            'doc_model': 'mrp.production',
            'docs': docs,
            'proper_sale_line_id': sale_line_id,
            'proper_product_description': product_description,
        }
