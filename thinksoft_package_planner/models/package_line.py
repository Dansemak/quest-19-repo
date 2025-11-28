from odoo import fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class package_line(models.Model):
    _name = "package.line"
    _description = "Package Line"

    picking_id = fields.Many2one("stock.picking", "Reference")
    seq = fields.Integer("#")
    product_id = fields.Many2one("product.product", "Product")
    tagging = fields.Char("Tagging")
    max_qty_pack = fields.Integer("Max Qty/Package")
    # Heat field will need to be removed, since mtr_template_ids will be used instead.
    heat = fields.Char("Archived Heat #", readonly=True)
    mtr_template_ids = fields.Many2many(
        comodel_name="mtr.template",
        relation="mtr_template_package_line_rel",
        column1="id",
        column2="name",
        string="MTR",
    )
    pick_qty = fields.Float("Pick")
    inbox_qty = fields.Char(compute="get_package_planner", string="In Box")
    boxs = fields.Integer(compute="get_package_planner", string="Boxes")
    # crates = fields.Char(compute='get_package_planner', string='Crates')
    skids = fields.Char(compute="get_package_planner", string="Skids")
    qty_packed = fields.Integer(compute="get_package_planner", string="Qty Packed")
    desc = fields.Text(compute="get_package_planner", string="Description")

    ordered = fields.Integer("Ordered")
    last_box_no = fields.Integer("Last Used Box #")
    pack_type = fields.Selection(
        [("box", "Box"), ("bag", "Bag"), ("sleeve", "Sleeve")],
        "Package Type",
        default="box",
    )
    crate_skid = fields.Selection([("skid", "Skid"), ("crate", "Crate")], "Crate/Skid")
    cs_no = fields.Integer("Crate/Skid No")
    name = fields.Char("Description", size=32)
    package_planner_line = fields.One2many(
        "package.planner.line", "pack_id", "Package Details"
    )
    move_id = fields.Many2one("stock.move", "Move Reference")

    def get_package_planner(self):
        for pack in self:
            pack.qty_packed = 0
            pack.skids = 0
            # pack.crates = 0
            pack.inbox_qty = 0
            pack.boxs = 0
            inbox_qty_lst = []
            skid_crate_list = []
            for val in pack.package_planner_line:
                pack.qty_packed += val.qty_packed
                if val.pack_in_no not in inbox_qty_lst:
                    inbox_qty_lst.append(val.pack_in_no)
                if val.no not in skid_crate_list:
                    skid_crate_list.append(val.no)
                if val.crate_skid == "skid":
                    pack.skids = ", ".join(map(str, skid_crate_list))
                # if val.crate_skid == 'crate':
                #     pack.crates = ', '.join(map(str, skid_crate_list))
            pack.inbox_qty = ", ".join(map(str, inbox_qty_lst))
            pack.boxs = len(set(inbox_qty_lst))

            pack.desc = pack.move_id.product_id.description

    def button_package_label_3x4(self):
        return self.env.ref("thinksoft_package_planner.3x4_qweb_report").report_action(
            self
        )
        return True

    def button_package_label_1_25x4(self):
        return self.env.ref(
            "thinksoft_package_planner.1_25x4_qweb_report"
        ).report_action(self)
        return True

    def load_lines(self):
        package_id = self
        package_line_obj = self.env["package.planner.line"]
        line_ids = map(lambda x: x.id, package_id.package_planner_line)
        if package_id.package_planner_line:
            for l in package_id.package_planner_line:
                l.unlink()
        if package_id.max_qty_pack <= 0:
            raise UserError(_("Load Error Please fill all the packaging details!"))
        if package_id.pick_qty < package_id.max_qty_pack:
            raise UserError(
                _(
                    'Error! Max Quantity Package cannot exceed Pick quantity= "%s" and Max Quantity=%d.'
                )
                % (package_id.pick_qty, package_id.max_qty_pack)
            )
        seq_no = 1
        qty = 0
        box_no = package_id.last_box_no + 1
        while qty < package_id.pick_qty:
            max_qty = package_id.max_qty_pack
            check_qty = package_id.pick_qty - qty
            if check_qty != 0 and check_qty < package_id.max_qty_pack:
                max_qty = package_id.pick_qty - qty
            package_line_obj.create(
                {
                    "seq_no": seq_no,
                    "pack_in": package_id.pack_type,
                    "pack_in_no": box_no,
                    "qty_packed": max_qty,
                    # 'crate_skid': package_id.crate_skid,
                    "no": package_id.cs_no,
                    "pack_id": package_id.id,
                }
            )
            seq_no += 1
            qty += package_id.max_qty_pack
            box_no += 1
        return True

    def save_load(self):
        package_id = self
        if package_id.pick_qty < package_id.qty_packed:
            raise UserError(
                _(
                    'Error! Quantity Packed cannot exceed Pick quantity= "%s" (Quantity Packed=%d).'
                )
                % (package_id.pick_qty, package_id.qty_packed)
            )
        return True

    # @api.model
    # def create(self, vals):
    #     for val in vals:
    #         seq = 10
    #         if val.get('package_planner_line'):
    #             for value in val['package_planner_line']:
    #                 if len(value) > 2 and isinstance(value[2], dict):
    #                     value[2].setdefault('seq', seq)
    #                 seq += 10
