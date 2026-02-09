from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    outside_salesperson_id = fields.Many2one(comodel_name='res.users', string="Outside Salesperson", readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()

        res["outside_salesperson_id"] = "s.outside_salesperson_id"

        return res

    def _group_by_sale(self):
        group_by = super()._group_by_sale()

        group_by += ", s.outside_salesperson_id"

        return group_by