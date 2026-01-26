# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

log = logging.getLogger(__name__)


class RmaMain(models.Model):
    _name = "rma.main"
    _description = "RMA"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]
    _order = "date desc, id desc"

    name = fields.Char("Name", default=lambda self: _("New"), store=True)
    is_validate = fields.Boolean("Validated", copy=False)
    sale_order = fields.Many2one(
        "sale.order", "Sale Order", domain="[('state','in',['sale','done'])]"
    )
    subject = fields.Char("Subject")
    date = fields.Datetime("Date", default=datetime.now(), required=True)
    deadline = fields.Datetime("Deadline", default=datetime.now(), required=True)
    rma_note = fields.Text("RMA Note")
    priority = fields.Selection(
        [("0", "No Priority"), ("1", "Low"), ("2", "Normal"), ("3", "High")], "Priority"
    )
    responsible = fields.Many2one("res.users", "Responsible", store=True)
    sales_channel = fields.Many2one("crm.team", "Sales Channel", store=True)
    delivery_order = fields.Many2one(
        "stock.picking",
        "Delivery Order",
        store=True,
        domain="[('picking_type_code','=','outgoing'), ('sale_id','=',sale_order)], ('state', 'in', ['assigned', 'done'])]"
    )
    del_email = fields.Char("Delivery Email", store=True)
    partner_id = fields.Many2one(
        "res.partner", "Customer", related="sale_order.partner_id", store=True
    )
    del_partner = fields.Many2one("res.partner", "Delivery Partner", store=True)
    del_phone = fields.Char("Delivery Phone", store=True)
    del_street = fields.Char("Street")
    del_street2 = fields.Char("Street2")
    del_city = fields.Char("City")
    del_zip = fields.Char("Zip")
    del_state_id = fields.Many2one(
        "res.country.state",
        string="Del State",
        domain="[('country_id', '=?', country_id)]",
    )
    del_country_id = fields.Many2one("res.country", string="Del Country")
    inv_partner = fields.Many2one("res.partner", "Invoice Partner", store=True)
    inv_email = fields.Char("Invoice Email", store=True)
    inv_phone = fields.Char("Invoice Phone", store=True)
    inv_street = fields.Char("Inv Street")
    inv_street2 = fields.Char("Inv Street2")
    inv_city = fields.Char("Inv City")
    inv_zip = fields.Char("Inv Zip")
    inv_state_id = fields.Many2one(
        "res.country.state", string="State", domain="[('country_id', '=?', country_id)]"
    )
    inv_country_id = fields.Many2one("res.country", string="Inv Country")
    del_phone = fields.Char("Phone", store=True)
    del_email = fields.Char("Email", store=True)
    rma_line_ids = fields.One2many("rma.lines", "rma_id", "RMA Lines", store=True)
    return_reason = fields.Char("Return Reason")

    in_delivery_count = fields.Integer(
        string="Incoming Orders", compute="_compute_incoming_picking_ids"
    )
    out_delivery_count = fields.Integer(
        string="Outgoing Orders", compute="_compute_outgoing_picking_ids"
    )
    refund_inv_count = fields.Integer(
        string="Credit Note", compute="_compute_refund_inv_ids"
    )
    sale_order_count = fields.Integer(
        string="Sale Order Count", compute="_compute_sale_order_ids"
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submit", "Submitted"),
            ("approved", "Approved"),
            ("processing", "Processing"),
            ("close", "Closed"),
            ("reject", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    replace_prd_ids = fields.One2many(
        "rma.replace.order", "rma_id", string="Replace Product"
    )
    total_return = fields.Float(
        "Total Return", compute="_update_return_total", default=0.0, store=True
    )
    total_replace = fields.Float(
        "Total Replace", compute="_update_replace_total", default=0.0, store=True
    )
    total_difference = fields.Float(
        "Total Difference", compute="_update_difference_total", store=True
    )
    difference_amount = fields.Float(
        "Difference Amount", compute="_update_difference_total", store=True
    )
    remarks = fields.Text("Remarks")
    validated = fields.Boolean("Validate", compute="_compute_validated")

    is_without_do_rma = fields.Boolean("IS without do rma")
    rma_resolution_id = fields.Many2one("rma.resolution", "RMA Resolution")

    rma_type = fields.Selection([("rma_with_do", "With DO")])
    is_editable = fields.Boolean(compute="_compute_is_editable", default=True)

    def action_cancel(self):
        #TODO: cancel related records: stock pickings, sale orders, credit notes
        #   prevent cancellation if:
        #       1. related stock pickings are done
        #       2. related sale orders are delivered
        #       3. related credit notes are posted


        stock_picking_ids = self.env["stock.picking"].search([("rma_id", "=", self.id)])
        sale_order_ids = self.env["sale.order"].search([("rma_id", "=", self.id)])
        account_move_ids = self.env["account.move"].search([("rma_id", "=", self.id)])

        if stock_picking_ids.filtered(lambda t: t.state == "done"):
            raise ValidationError(
                "Sorry! You can't cancel this RMA as related stock pickings are done."
            )
        else:
            stock_picking_ids.action_cancel()

        new_do = self.env["stock.picking"].search([('sale_id', '=', sale_order_ids.id), ('picking_type_code', '=', 'outgoing')])
        if new_do.filtered(lambda t: t.state == "done"):
            raise ValidationError(
                "Sorry! You can't cancel this RMA as related Sale Orders are delivered."
            )
        else:
            sale_order_ids.action_cancel()

        credit_notes = account_move_ids.filtered(lambda t: t.move_type == 'out_refund' and t.state == 'posted')
        if credit_notes:
            raise ValidationError(
                "Sorry! You can't cancel this RMA as related Credit Notes are posted."
            )
        elif account_move_ids.filtered(lambda t: t.move_type == 'out_refund' and t.state == 'cancel'):
            pass
        else:
            account_move_ids.button_cancel()


        self.write({"state": "cancelled"})

    def button_reject(self):
        self.write({"state": "reject"})

    def _compute_is_editable(self):
        for rma in self:
            rma.is_editable = True

    @api.depends(
        "rma_line_ids.price_unit",
        "rma_line_ids.return_qty",
    )
    def _update_return_total(self):
        for case in self:
            total = 0
            for line in case.rma_line_ids:
                total += line.total_price
            case.total_return = total

    @api.depends("replace_prd_ids.total_price")
    def _update_replace_total(self):
        for case in self:
            total = 0
            for line in case.replace_prd_ids:
                total += line.total_price
            case.total_replace = total

    @api.depends("total_return", "total_replace")
    def _update_difference_total(self):
        self.total_difference = 0.00
        self.difference_amount = 0.00
        for rma in self:
            rma.total_difference = rma.total_replace - rma.total_return
            rma.difference_amount = abs(rma.total_difference)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "rma_type" in vals and vals.get("rma_type", False):
                if vals.get("rma_type") == "rma_with_do":
                    vals.update(
                        {
                            "name": self.env["ir.sequence"].next_by_code("rma.order"),
                        }
                    )
        return super().create(vals_list)

    @api.onchange("sale_order")
    def onchange_sale_order_id(self):
        domain = [("picking_type_code", "=", "outgoing")]
        if self.sale_order:
            if self.rma_type == "rma_with_do":
                picking_id = self.sale_order.picking_ids.filtered(
                    lambda t: t.state == "done"
                ).ids
                domain.append(("id", "in", picking_id))
                self.delivery_order = False

                sale_order_obj = self.env["sale.order"].search(
                    [("id", "=", self.sale_order.id)]
                )

                for delivery_ord in sale_order_obj.picking_ids:
                    if delivery_ord.state == "done":
                        self.delivery_order = delivery_ord.id

                order_line_dict = {}
                order_line_list = []

                for line in self.rma_line_ids:
                    self.rma_line_ids = [(2, line.id, 0)]

                for i in sale_order_obj.order_line:
                    if i.product_id.service_tracking in ["consu", "product"]:
                        order_line_dict = {
                            "product_id": i.product_id.id,
                            "delivery_qty": i.product_uom_qty,
                            "price_unit": i.product_id.standard_price,
                        }
                        order_line_list.append((0, 0, order_line_dict))

                self.rma_line_ids = order_line_list
        return {"domain": {"delivery_order": domain}}

    def action_submit(self):
        if not sum(
            self.rma_line_ids.filtered(
                lambda t: t.product_id.service_tracking != "service"
            ).mapped("return_qty")
        ):
            raise ValidationError(
                "Sorry! You have to enter at-lease one return item to proceed"
            )

        if self.replace_prd_ids:
            if not sum(self.replace_prd_ids.mapped("qty")):
                raise ValidationError(
                    "Sorry! You have to enter at-lease one qty for replace product to proceed"
                )

        service_line = self.rma_line_ids.filtered(
            lambda t: t.product_id.service_tracking == "service"
        )
        rma_lines = self.rma_line_ids.filtered(
            lambda t: t.product_id.service_tracking != "service"
            and t.rma_resolution_action
        )
        rma_resolution_actions = set(rma_lines.mapped("rma_resolution_action"))
        if (
            service_line
            and len(rma_resolution_actions) == 1
            and service_line[0].rma_resolution_id
            and service_line[0].rma_resolution_id.id
            != rma_lines[0].rma_resolution_id.id
        ):
            raise ValidationError(
                "Please select correct Resolution for shipping item and then proceed"
            )

        self.write({"state": "submit"})

    def _compute_incoming_picking_ids(self):
        for order in self:
            stock_picking_ids = self.env["stock.picking"].search(
                [("rma_id", "=", order.id)]
            )
            order.in_delivery_count = len(stock_picking_ids)

    def _compute_sale_order_ids(self):
        for order in self:
            sale_order_ids = self.env["sale.order"].search([("rma_id", "=", order.id)])
            order.sale_order_count = len(sale_order_ids)

    def _compute_outgoing_picking_ids(self):
        for order in self:
            stock_picking_ids = self.env["stock.picking"].search(
                [("rma_id", "=", order.id), ("picking_type_code", "=", "outgoing")]
            )
            order.out_delivery_count = len(stock_picking_ids)

    def _compute_refund_inv_ids(self):
        for inv in self:
            refund_inv_ids = self.env["account.move"].search([("rma_id", "=", inv.id)])
            inv.refund_inv_count = len(refund_inv_ids)

    def _compute_validated(self):
        for rma in self:
            stock_picking_ids = self.env["stock.picking"].search(
                [("rma_id", "=", rma.id)]
            )
            if rma.state in ("processing"):
                if stock_picking_ids.filtered(
                    lambda t: t.state not in ("done", "cancel")
                ):
                    rma.validated = False
                else:
                    rma.validated = True
            else:
                rma.validated = False

    def action_return_replace(self):
        ctx = {
            "default_rma_id": self.id,
            "default_rma_type": self.rma_type,
            "default_rma_line": self.rma_line_ids.ids,
            "default_replace_prd_ids": self.replace_prd_ids.ids,
        }
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "name": "RMA Resolution",
            "view_mode": "form",
            "res_model": "return.order",
            "target": "new",
            "context": ctx,
        }

    @api.onchange("sale_order")
    def set_sale_details(self):
        sale_order_obj = self.env["sale.order"].search(
            [("id", "=", self.sale_order.id)]
        )
        self.sales_channel = sale_order_obj.team_id
        self.inv_partner = sale_order_obj.partner_invoice_id.id
        self.responsible = sale_order_obj.user_id.id
        self.inv_phone = sale_order_obj.partner_invoice_id.phone
        self.inv_email = sale_order_obj.partner_invoice_id.email
        self.inv_street = sale_order_obj.partner_invoice_id.street
        self.inv_street2 = sale_order_obj.partner_invoice_id.street2
        self.inv_city = sale_order_obj.partner_invoice_id.city
        self.inv_zip = sale_order_obj.partner_invoice_id.zip
        self.inv_state_id = sale_order_obj.partner_invoice_id.state_id.id
        self.inv_country_id = sale_order_obj.partner_invoice_id.country_id.id

    @api.onchange("delivery_order")
    def update_delivery_details(self):
        order_line_list = []
        for rma in self:
            if rma.delivery_order and rma.delivery_order.partner_id:
                partner_id = rma.delivery_order.partner_id
                rma.del_partner = partner_id.id
                rma.del_phone = partner_id.phone
                rma.del_email = partner_id.email
                rma.del_street = partner_id.street
                rma.del_street2 = partner_id.street2
                rma.del_city = partner_id.city
                rma.del_zip = partner_id.zip
                rma.del_state_id = partner_id.state_id.id
                rma.del_country_id = partner_id.country_id.id
            else:
                rma.del_street = ""
                rma.del_street2 = ""
                rma.del_city = ""
                rma.del_zip = ""
                rma.del_state_id = False
                rma.del_country_id = False
            for line in rma.rma_line_ids:
                rma.rma_line_ids = [(2, line.id, 0)]
            if rma.rma_type in ("rma_with_do"):
                # field changed
                for i in self.delivery_order.move_line_ids:
                    move_line_id = (
                        self.env["account.move.line"]
                        .sudo()
                        .search([("stock_move_id", "=", i.move_id.id)], limit=1)
                    )
                    if move_line_id:
                        price_unit = move_line_id.price_unit
                    else:
                        price_unit = i.move_id.sale_line_id.price_unit
                    return_qty = i.quantity - i.return_qty
                    order_line_dict = {
                        "product_id": i.product_id.id,
                        "delivery_qty": return_qty,
                        "sale_line_id": i.move_id.sale_line_id.id,
                        "move_line_id": i.id,
                        "price_unit": price_unit,
                    }

                    if i.lot_id:
                        order_line_dict.update({"lot_ids": ([(6, 0, [i.lot_id.id])])})
                    order_line_list.append((0, 0, order_line_dict))
        self.rma_line_ids = order_line_list

    def rma_line_btn(self):
        self.ensure_one()
        return {
            "name": "Product",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "product.product",
            "domain": [("rma_id", "=", self.id)],
        }

    @api.onchange("deadline", "date")
    def _onchange_deadline(self):
        if self.deadline and self.date:
            if self.date > self.deadline:
                raise UserError(_("Please select a proper date."))

    def action_send_rma(self):
        self.ensure_one()

        ir_model_data = self.env["ir.model.data"]
        try:
            template_id = ir_model_data._xmlid_lookup("bi_rma.email_template_edi_rma")[
                1
            ]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup(
                "mail.email_compose_message_wizard_form"
            )[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            "default_model": "rma.main",
            "default_res_ids": self.ids,
            "default_use_template": bool(template_id),
            "default_template_id": template_id,
            "default_composition_mode": "comment",
            "force_email": True,
        }
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
        }

    def process_rma(self):
        refund_items = self.rma_line_ids.filtered(
            lambda t: t.rma_resolution_action == "refund"
        )
        replacement_items = self.rma_line_ids.filtered(
            lambda t: t.rma_resolution_action == "replacement"
        )
        refund_with_return_items = self.rma_line_ids.filtered(
            lambda t: t.rma_resolution_action == "refund_with_returned_item"
        )
        replacement_with_return_items = self.rma_line_ids.filtered(
            lambda t: t.rma_resolution_action == "replacement_with_returned_item"
        )

        # ======================= PROCESS REFUND ITEMS =========================
        if refund_items:
            self.process_credit_note(refund_items)

        # ======================= PROCESS REFUND WITH RETURNED ITEMS =========================
        if refund_with_return_items:
            self.process_credit_note(refund_with_return_items)
            self.process_returned_items(refund_with_return_items)

        # ======================= PROCESS REPLACEMENT ITEMS WITH NO RETURNED ITEMS =========================
        if replacement_items:
            self.process_replacement_items(self.replace_prd_ids)

        # ======================= PROCESS REPLACEMENT ITEMS WITH RETURNED ITEMS =========================
        if replacement_with_return_items:
            if not replacement_items:
                # Create the replacement items only once
                self.process_replacement_items(self.replace_prd_ids)
            self.process_returned_items(replacement_with_return_items)
        return True

    def process_credit_note(self, refund_items):
        """This function creates a credit note for the refund

        Args:
            refund_items (_type_): RMA lines to be refunded
        """
        account_move_lines = []

        # ==================== ACCOUNT MOVE LINES FOR REFUND =========================
        for line in refund_items:
            account_move_line = (
                0,
                0,
                {
                    "product_id": line.product_id.id,
                    "quantity": line.return_qty,
                    "price_unit": line.price_unit,
                    "discount": line.sale_line_id.discount,
                    "tax_ids": line.sale_line_id.tax_ids,
                    "rma_line_id": line.id,
                },
            )
            account_move_lines.append(account_move_line)

        # ==================== UPDATE CREDIT NOTE IF ALREADY EXISTS =========================
        credit_note = self.env["account.move"].search(
            [("rma_id", "=", self.id), ("move_type", "=", "out_refund")]
        )
        if credit_note:
            credit_note.write({"invoice_line_ids": account_move_lines})
        else:
            # ==================== CREATE ACCOUNT MOVE FOR REFUND IF CREDIT NOTE DOES NOT EXIST =========================
            sale_id = self.sale_order
            fiscal_position_id = (
                self.env["account.fiscal.position"]
                .with_context(force_company=sale_id.company_id.id)
                ._get_fiscal_position(sale_id.partner_id)
            )

            account_move = {
                "move_type": "out_refund",
                "partner_id": self.partner_id.id,
                "sale_id": sale_id.id,
                "rma_id": self.id,
                "ref": sale_id.client_order_ref,
                "invoice_origin": sale_id.name,
                "fiscal_position_id": fiscal_position_id.id
                if fiscal_position_id
                else False,
                "team_id": sale_id.team_id.id,
                "invoice_date": self.deadline or False,
                "invoice_user_id": self.env.uid,
                "narration": self.name,
                "currency_id": sale_id.company_id.currency_id.id,
                "invoice_line_ids": account_move_lines,
            }

            self.env["account.move"].create(account_move)

    def process_returned_items(self, return_items):
        """This function creates stock picking for returned items

        Args:
            return_items (_type_): RMA lines to be returned
        """

        picking_type_id = (
            self.sale_order.warehouse_id.out_type_id.return_picking_type_id
        )

        # ======================== CREATE STOCK PICKING FOR RETURNED ITEMS =========================
        stock_picking = {
            "rma_id": self.id,
            "partner_id": self.del_partner.id,
            "origin": self.sale_order.name,
            "scheduled_date": self.date,
            "picking_type_id": picking_type_id[0].id,
        }
        stock_picking_id = self.env["stock.picking"].create(stock_picking)

        # ======================== CREATE STOCK MOVE FOR RETURNED ITEMS =========================
        for line in return_items.filtered(
            lambda t: t.product_id.service_tracking != "service"
        ):
            stock_move = {
                "company_id": self.sale_order.company_id.id,
                "location_id": picking_type_id.default_location_src_id.id,
                "location_dest_id": picking_type_id.default_location_dest_id.id,
                "picking_id": stock_picking_id.id,
                "picking_type_id": picking_type_id.id,
                "date": self.date,
                "product_id": line.product_id.id,
                "product_uom_qty": float(line.return_qty),
                "product_uom": line.product_id.uom_id.id,
                "sale_line_id": line.sale_line_id.id,
                "rma_line_id": line.id,
            }
            stock_move_id = self.env["stock.move"].create(stock_move)

            move_line_vals = stock_move_id._prepare_move_line_vals()
            if line.lot_ids:
                move_line_vals.update(
                    {
                        "lot_id": line.lot_ids[0].id,
                        "quantity": float(line.return_qty),
                    }
                )
            else:
                move_line_vals.update(
                    {
                        "lot_id": False,
                        "quantity": float(line.return_qty),
                    }
                )
            self.env["stock.move.line"].create(move_line_vals)

        stock_picking_id.action_confirm()
        stock_picking_id.action_assign()
        picking_move_line = stock_picking_id.mapped("move_line_ids").filtered(
            lambda t: t.quantity == 0
        )
        picking_move_line.sudo().unlink()

        return True

    def process_replacement_items(self, replacement_items):
        """This function creates and validates Sale Order for replacement items

        Args:
            replacement_items (_type_): RMA lines to be replaced
        """
        fiscal_position_id = (
            self.env["account.fiscal.position"]
            .with_context(force_company=self.sale_order.company_id.id)
            ._get_fiscal_position(self.sale_order.partner_id)
        )

        # ======================== CREATE SALE ORDER LINES FOR REPLACEMENT ITEMS =========================
        sale_order_lines = []
        for line in replacement_items.filtered(
            lambda t: t.product_id.service_tracking != "service"):
            sale_order_line = (
                0,
                0,
                {
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.qty,
                    "price_unit": line.product_price,
                },
            )
            sale_order_lines.append(sale_order_line)

        # ======================== CHECK IF A SALE ORDER EXISTS =========================
        sale_order = self.env["sale.order"].search([("rma_id", "=", self.id), ('state', '=', 'draft')])
        if sale_order:
            sale_order.write({"order_line": sale_order_lines})
        else:
            # ======================== CREATE SALE ORDER FOR REPLACEMENT ITEMS =========================
            sale_order = {
                "partner_id": self.partner_id.id,
                "name": self.env["ir.sequence"].next_by_code("sale.order"),
                "rma_id": self.id,
                "origin": self.sale_order.name,
                "pricelist_id": self.sale_order.pricelist_id.id,
                "team_id": self.sale_order.team_id.id,
                "fiscal_position_id": fiscal_position_id.id
                if fiscal_position_id
                else False,
                "warehouse_id": self.sale_order.warehouse_id.id,
                "date_order": self.date,
                "partner_shipping_id": self.sale_order.partner_shipping_id.id,
                "partner_invoice_id": self.sale_order.partner_invoice_id.id,
                "order_line": sale_order_lines,
            }

            order = self.env["sale.order"].create(sale_order)
            order.order_line._compute_tax_ids()

        self.update({"sale_order_count": 1 + self.sale_order_count})

    def action_approve(self):
        if self.rma_type == "rma_with_do":
            if self.state == "approved":
                raise UserError("You cannot approve a RMA more then one time.")

            self.process_rma()
            self.write({"state": "approved"})

    def action_view_receipt(self):
        self.ensure_one()
        return {
            "name": "Picking",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "stock.picking",
            "domain": [("rma_id", "=", self.id)],
        }

    def action_view_refund_invoice(self):
        self.ensure_one()
        return {
            "name": "Credit Note",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "account.move",
            "domain": [("rma_id", "=", self.id)],
        }

    def action_view_sale_order(self):
        return {
            "name": "Sale Order",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "sale.order",
            "domain": [("rma_id", "=", self.id)],
        }

    def action_move_to_draft(self):
        stock_picking_ids = self.env["stock.picking"].search([("rma_id", "=", self.id)])
        stock_picking_ids.action_cancel()
        self.write({"state": "draft"})
        return

    def validate_stock_picking(self):
        stock_picking_ids = self.env["stock.picking"].search([("rma_id", "=", self.id)])
        if stock_picking_ids.filtered(lambda t: t.state not in ("done", "cancel")):
            raise ValidationError(
                "Sorry! You can't proceed until all the stock picking is complete"
            )

    def action_close(self):
        self.validate_stock_picking()
        baseDate = fields.Date.today(self)
        self.write({"state": "close"})
        return

    def action_validate(self):
        self.validate_stock_picking()
        # if self.replace_prd_ids:
        #     self.create_replaced_product_sale_order()
        self.write({"is_validate": True})

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            for i in rec.rma_line_ids:
                if (
                    i.product_id.tracking == "serial"
                    and i.return_qty != 0
                    and len(i.lot_ids.ids) > i.return_qty
                ):
                    raise UserError(
                        f"The Product {i.product_id.name} should have count of serial numbers equal/less then the return quantity {i.return_qty}"
                    )
                elif (
                    i.product_id.tracking == "lot"
                    and i.return_qty != 0
                    and len(i.lot_ids.ids) > i.return_qty
                ):
                    raise UserError(
                        f"The Product {i.product_id.name} should have count of lot numbers equal/less then the return quantity {i.return_qty}"
                    )
        return res

    def unlink(self):
        """
        Should allow to delete only if the stage in draft
        """
        for rma in self:
            if rma.state != "draft":
                raise ValidationError(
                    "Sorry! You can't delete the RMA order which is not in draft stage"
                )
        return super().unlink()


class RmaLines(models.Model):
    _name = "rma.lines"
    _description = "Rma Lines"

    rma_id = fields.Many2one("rma.main", "RMA Id")
    rma_state = fields.Selection(related="rma_id.state", store=True, string="State")
    delivery_order = fields.Many2one(
        related="rma_id.delivery_order", store=True, string="Delivery Order"
    )
    sale_order = fields.Many2one(
        related="rma_id.sale_order", store=True, string="Sale Order"
    )
    total_return = fields.Float(
        related="rma_id.total_return", store=True, string="Total Return"
    )
    total_replace = fields.Float(
        related="rma_id.total_replace", store=True, string="Total Replace"
    )
    total_difference = fields.Float(
        related="rma_id.total_difference", store=True, string="Total Difference"
    )
    rma_resolution_id = fields.Many2one("rma.resolution", "Return/No Return")
    return_reason_id = fields.Many2one("return.reason", "Return Reason")
    rma_resolution_action = fields.Selection(
        related="rma_resolution_id.rma_action", store=True
    )
    date = fields.Datetime(related="rma_id.date", store=True)
    state = fields.Selection(related="rma_id.state")
    product_id = fields.Many2one("product.product", "Product")
    detailed_type = fields.Selection(related="product_id.service_tracking")
    delivery_qty = fields.Float("Delivered Quantity")
    return_qty = fields.Float("Return Quantity")
    received_qty = fields.Float("Received Quantity")
    price_unit = fields.Float("Price")
    total_price = fields.Float("Total Price", compute="_update_total_price")
    replaced_with = fields.Many2many(
        "product.product", "rma_lin_prds_id", string="Replaced with"
    )
    replaced_qty = fields.Float("Replaced Quantity")
    is_invoice = fields.Boolean("Is invoice", default=False)
    lot_ids = fields.Many2many(
        "stock.lot", "rel_rma_product_id", string="Lot/Serial Numbers"
    )
    sale_line_id = fields.Many2one(
        string="Order Line", comodel_name="sale.order.line", ondelete="restrict"
    )
    move_line_id = fields.Many2one(
        string="Move Order Line", comodel_name="stock.move.line", ondelete="set null"
    )
    return_qty = fields.Integer(string="Return Quantity")

    stock_move_id = fields.Many2one(
        string="Stock Move", comodel_name="stock.move", ondelete="restrict"
    )
    pending_qty = fields.Float(string="Pending Qty")
    rma_line_stock_move_ids = fields.One2many(
        "stock.move",
        "rma_line_id",
        string="To get all the stock move for this sale line id stock",
    )
    rma_line_account_move_line_ids = fields.One2many(
        "account.move.line",
        "rma_line_id",
        string="To get all the stock move for this sale line id Account",
    )
    rma_inward_qty = fields.Float(
        compute="compute_rma_inward_credit_note_qty", string="RMA Stock Inward Qty"
    )
    rma_credit_note_qty = fields.Float(
        compute="compute_rma_inward_credit_note_qty", string="RMA Credit Note Qty"
    )

    def compute_rma_inward_credit_note_qty(self):
        for rma_line in self:
            if rma_line.rma_line_stock_move_ids:
                rma_line.rma_inward_qty = sum(
                    rma_line.rma_line_stock_move_ids.filtered(
                        lambda stockmove: stockmove.state == "done"
                    ).mapped("quantity")
                )
            else:
                rma_line.rma_inward_qty = 0.00
            if rma_line.rma_line_account_move_line_ids:
                rma_line.rma_credit_note_qty = sum(
                    rma_line.rma_line_account_move_line_ids.sudo()
                    .filtered(
                        lambda accountmoveline: accountmoveline.parent_state == "posted"
                    )
                    .mapped("quantity")
                )
            else:
                rma_line.rma_credit_note_qty = 0.00

    @api.onchange(
        "return_qty",
        "price_unit",
    )
    @api.depends(
        "return_qty",
        "price_unit",
    )
    def _update_total_price(self):
        for line in self:
            line.total_price = line.return_qty * line.price_unit

    @api.onchange("return_qty")
    def _onchange_return_qty(self):
        if self.return_qty:
            if self.delivery_qty < self.return_qty:
                raise UserError(_("Quantity should be less than delivered."))


class RmaReplaceOrder(models.Model):
    _name = "rma.replace.order"
    _description = "Rma Replace Order"

    product_id = fields.Many2one("product.product", string="Product")
    product_detailed_type = fields.Selection(related="product_id.service_tracking")
    qty = fields.Integer("qty", default=0)
    rma_id = fields.Many2one("rma.main", string="RMA Order")
    product_price = fields.Float("Price")
    total_price = fields.Float(
        "Total Price", default=0.0, compute="_update_total_price"
    )

    @api.onchange("qty", "product_price")
    def _update_total_price(self):
        for line in self:
            line.total_price = line.qty * line.product_price


class RejectWizard(models.Model):
    _name = "return.reason"
    _description = "Return Reason"
    _rec_name = "name"

    name = fields.Char("Return Reason")
    is_customer_return_reason = fields.Boolean(
        string="Is Customer Return Reason", default=True
    )
    active = fields.Boolean(default=True)


class RmaClaim(models.Model):
    _name = "rma.claim"
    _description = "Rma Claim"
    _rec_name = "rma_id"

    rma_id = fields.Many2one("rma.main", "RMA Number")
    subject = fields.Char("Subject")
    partner = fields.Many2one("res.partner", "Partner", store=True)
    responsible = fields.Many2one("res.users", "Responsible", store=True)
    date = fields.Datetime("Date")
    nxt_act_dt = fields.Datetime("Next Action Date")
    nxt_act = fields.Char("Next Action")
    stock_picking_id = fields.Many2one("stock.picking")


class RmaResolution(models.Model):
    _name = "rma.resolution"
    _description = "Rma Resolution"
    _rec_name = "rma_resolution"

    rma_resolution = fields.Char("Resolution", required=True)
    rma_action = fields.Selection(
        [
            ("refund", "Refund"),
            ("refund_with_returned_item", "Refund With Returned Items"),
            ("replacement", "Replacement"),
            ("replacement_with_returned_item", "Replacement With Returned Items"),
        ],
        string="Action",
    )
    active = fields.Boolean(default=True)
    rma_main_ids = fields.One2many("rma.main", "rma_resolution_id")
    count_rma = fields.Integer(compute="get_len_rma_main_ids")

    def get_len_rma_main_ids(self):
        for reason in self:
            reason.count_rma = len(reason.rma_main_ids)

    def unlink(self):
        for reason in self:
            if reason.count_rma:
                raise ValidationError(
                    "Sorry! this reason was used in the RMA so you can't delete use archive"
                )
        return super().unlink()
