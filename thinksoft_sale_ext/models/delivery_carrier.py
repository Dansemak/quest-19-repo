from odoo import api, fields, models
from odoo.exceptions import ValidationError


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    cut_off = fields.Float(
        string="Cut Off",
        help="The time of day when the shipping cutoff occurs, in hours (0-24).",
    )

    # cut_off validation
    @api.constrains("cut_off")
    def _constraint_cut_off(self):
        for record in self:
            if record.cut_off < 0 or record.cut_off > 24:
                raise ValidationError("Cut Off time must be valid")
