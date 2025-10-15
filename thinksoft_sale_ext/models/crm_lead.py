from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    # adding relational fields to crm.lead in the thinksoft_sale_ext module
    # to avoid hard dependancies between extension modules

    sale_end_user_id = fields.Many2one('sale.end.user', string="End User")
    sale_project_id = fields.Many2one('sale.project', string="Project")

    def action_sale_quotations_new(self):
        res = super().action_sale_quotations_new()

        res['context']['default_sale_end_user_id'] = self.sale_end_user_id.id
        res['context']['default_sale_project_id'] = self.sale_project_id.id

        return res