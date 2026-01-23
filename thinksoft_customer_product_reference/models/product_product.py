from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # @api.model
    # def _name_search(
    #     self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    # ):
    #     product_ids = super()._name_search(name, args, operator, limit, name_get_uid)
    #     if self._context.get("partner_id"):
    #         product_customer_part_ids = self.env["product.customer.part"]._search(
    #             [
    #                 ("partner_id", "=", self._context.get("partner_id")),
    #                 ("part_number", operator, name),
    #             ],
    #             access_rights_uid=name_get_uid,
    #         )
    #         if product_customer_part_ids:
    #             product_ids = self._search(
    #                 [
    #                     (
    #                         "product_tmpl_id.customer_part_ids",
    #                         "in",
    #                         product_customer_part_ids,
    #                     )
    #                 ],
    #                 limit=limit,
    #                 access_rights_uid=name_get_uid,
    #             )
    #     return product_ids
