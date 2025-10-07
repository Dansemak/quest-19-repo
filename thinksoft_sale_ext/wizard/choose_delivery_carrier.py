from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = "choose.delivery.carrier"

    # modifying shipping methods field to not be required
    carrier_id = fields.Many2one(
        "delivery.carrier",
        string="Shipping Method",
        required=False,
        domain="[('id', 'in', available_carrier_ids)]",
    )

    # new added fields to the wizard
    customer_account_info = fields.Char(
        string="Customer Account Information",
        help="Enter any related customer account info regarding shipping (e.g. account number)",
    )
    freight_charge = fields.Many2one(
        "sale.freight",
        string="Freight Charge",
        help="Where and how the freight is being charged",
    )
    cut_off = fields.Float(
        string="Cut Off",
        help="The time of day when the shipping cutoff occurs, in hours (0-24).",
    )

    # disabling delivery rate logic
    @api.onchange("carrier_id", "total_weight")
    def _onchange_carrier_id(self):
        self.delivery_message = False
        self.delivery_price = 0.0
        self.display_price = 0.0

    def _get_delivery_rate(self):
        self.delivery_message = False
        self.delivery_price = 0.0
        self.display_price = 0.0
        return {}  # no error or warning

    # skipping all calculations
    @api.onchange("order_id")
    def _onchange_order_id(self):
        self.delivery_message = False
        self.delivery_price = 0.0
        self.display_price = 0.0

    # not adding a line item to the sale.order.lines
    def button_confirm(self):
        # Do NOT add shipping line
        self.order_id.write(
            {
                "carrier_id": self.carrier_id.id,
                "freight_charge": self.freight_charge,
                "customer_account_info": self.customer_account_info,
                "cut_off": self.cut_off,
                "recompute_delivery_price": False,
                "delivery_message": self.delivery_message or "",
            }
        )

    # cut_off validation
    @api.constrains("cut_off")
    def _constraint_cut_off(self):
        for record in self:
            if record.cut_off < 0 or record.cut_off > 24:
                raise ValidationError("Cut Off time must be valid")
