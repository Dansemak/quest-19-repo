from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
from math import ceil


class PackagePlan(models.Model):
    _name = "package.plan"
    _description = "Package Plan"

    picking_id = fields.Many2one("stock.picking", "Reference")
    seq_no = fields.Integer("#")
    product_id = fields.Many2one("product.product", "Product")
    tagging = fields.Char("Tagging")
    max_qty_pack = fields.Integer("Max Qty/Package")
    mtr_template_ids = fields.Many2many(
        comodel_name="mtr.template",
        relation="mtr_template_package_plan_rel",
        column1="id",
        column2="name",
        string="MTR",
    )
    pick_qty = fields.Float("Picked Qty")
    in_box = fields.Char(compute="get_package_planner", string="In Box")
    box_qty = fields.Integer(compute="get_package_planner", string="Boxes")
    skid_qty = fields.Char(compute="get_package_planner", string="Skids")
    packed_qty = fields.Integer(compute="get_package_planner", string="Packed Qty")
    description = fields.Text(string="Description")
    last_box_used = fields.Integer("Last Used Box #")
    package_type = fields.Selection(
        [("box", "Box"), ("sleeve", "Sleeve")],
        "Package Type",
        default="box",
    )
    is_skid = fields.Boolean("Skid")
    skid_number = fields.Integer("Num of Skids")
    package_plan_line_ids = fields.One2many(
        "package.plan.line", "package_plan_id", "Package Details"
    )
    stock_move_id = fields.Many2one("stock.move", "Stock Move Reference")

    def get_package_planner(self):
        for pack in self:
            pack.packed_qty = 0
            pack.skid_qty = 0
            pack.in_box = 0
            pack.box_qty = 0
            in_box_list = []
            skid_list = []
            for val in pack.package_plan_line_ids:
                pack.packed_qty += val.packed_qty
                if val.in_box not in in_box_list:
                    in_box_list.append(val.in_box)
                if val.skid_number not in skid_list:
                    skid_list.append(val.skid_number)
                if val.is_skid:
                    pack.skid_qty = ", ".join(map(str, skid_list))
            pack.in_box = ", ".join(map(str, in_box_list))
            pack.box_qty = len(set(in_box_list))

    def button_3x4_label_report(self):
        return self.env.ref(
            "thinksoft_package_planner.3x4_label_report"
        ).report_action(self)

    def button_package_label_1_25x4(self):
        return self.env.ref(
            "thinksoft_package_planner.1_25x4_label_report"
        ).report_action(self)

    def calculate_packaging(self):
        if self.package_plan_line_ids:
            self.package_plan_line_ids.unlink()
        if self.max_qty_pack <= 0:
            raise UserError(_("Please fill all the packaging details!"))
        if self.pick_qty < self.max_qty_pack:
            raise UserError(_(f"'Max Qty/Package' cannot exceed Pick Quantity of {self.pick_qty}."))
        
        num_boxes = ceil(self.pick_qty / self.max_qty_pack)
        start_box = (self.last_box_used or 0) + 1
        lines = []
        for idx in range(num_boxes):
            if idx == num_boxes - 1:
                packed_qty = int(self.pick_qty - self.max_qty_pack * (num_boxes - 1))
            else:
                packed_qty = self.max_qty_pack

            lines.append(
                {
                    "seq_no": idx + 1,
                    "package_type": self.package_type,
                    "in_box": start_box + idx,
                    "packed_qty": packed_qty,
                    "is_skid": self.is_skid,
                    "skid_number": self.skid_number,
                    "package_plan_id": self.id,
                }
            )

        if lines:
            self.env["package.plan.line"].create(lines)
        return

