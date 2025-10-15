from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    # adding relational fields to crm.lead in the thinksoft_sale_ext module
    # to avoid hard dependancies between extension modules

    company_end_user_id = fields.Many2one('company.user', string="End User")
    job_project_id = fields.Many2one('job.project', string="Job Project")

    def action_sale_quotations_new(self):
        res = super().action_sale_quotations_new()

        res['context']['default_company_end_user_id'] = self.company_end_user_id.id
        res['context']['default_job_project_id'] = self.job_project_id.id

        return res