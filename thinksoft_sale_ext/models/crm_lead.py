from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    # adding relational fields to crm.lead in the thinksoft_sale_ext module
    # to avoid hard dependancies between extension modules

    customer_end_user_id = fields.Many2one('company.user', string="End User")
    customer_job_project_id = fields.Many2one('job.project', string="Job Project")

    def action_sale_quotations_new(self):
        res = super().action_sale_quotations_new()

        res['context']['default_customer_end_user_id'] = self.customer_end_user_id.id
        res['context']['default_customer_job_project_id'] = self.customer_job_project_id.id

        return res