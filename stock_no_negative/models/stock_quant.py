# Copyright 2015-2017 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.constrains("product_id", "quantity")
    def check_negative_qty(self):
        p = self.env["decimal.precision"].precision_get("Product Unit of Measure")

        for quant in self:
            if (
                float_compare(quant.quantity, 0, precision_digits=p) == -1
                and quant.product_id.is_storable
                and quant.location_id.usage in ["internal", "transit"]
            ):
                msg_add = ""
                if quant.lot_id:
                    msg_add = _(" lot %(name)s", name=quant.lot_id.display_name)
                raise ValidationError(
                    _(
                        "You cannot validate this stock operation because the "
                        f"stock level of the product '{quant.product_id.display_name}'{msg_add} would "
                        "become negative "
                        f"({quant.quantity}) on the stock location '{quant.location_id.complete_name}' "
                        "and negative stock is not allowed."
                    )
                )
