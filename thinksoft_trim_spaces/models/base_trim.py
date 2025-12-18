from odoo import models, api


class BaseTrimName(models.AbstractModel):
    _inherit = "base"

    def _trim_name(self, vals):
        """Trim leading and trailing spaces from vals['name'] if it exists and
        is a string.
        """

        for key in vals.keys():
            if isinstance(vals[key], str):
                vals[key] = vals[key].strip()

        # if 'name' in vals and isinstance(vals['name'], str):
        #     vals['name'] = vals['name'].strip()
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        for vals in vals_list:
            self._trim_name(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._trim_name(vals)
        return super().write(vals)
