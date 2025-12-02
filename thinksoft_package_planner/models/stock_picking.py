from odoo import fields, models
from odoo.tools.translate import _


class thinksoft_package(models.Model):
    _inherit = "stock.picking"

    package_line = fields.One2many("package.line", "picking_id", "Package Details")

    def create_product(self):
        package_line_obj = self.env["package.line"]
        create, update = False, False
        for move in self.move_ids:
            res = {
                "product_id": move.product_id.id,
                # 'pick_qty': val.pick_qty, # Get it from stock.move.line
                "seq": move.seq_no,
                # 'name': move.name,
                "picking_id": self.id,
                "move_id": move.id,
                "tagging": move.tagging,
            }
            for move_line in self.move_line_ids:
                if move_line.id == res["move_id"]:
                    res["pick_qty"] = move_line.qty_done
                    res["mtr_template_ids"] = move_line.mtr_template_ids
                    continue

            package_line_ids = package_line_obj.search([("move_id", "=", move.id)])
            if not package_line_ids:
                new_package_line = package_line_obj.create(res)
                move.package_line_id = new_package_line
                create = True
            else:
                package_line_ids.write(res)
                move.package_line_id = package_line_ids[0].id
                update = True
        if create:
            body = _("Package has been created")
            self.message_post(body=body)
        if update:
            body = "Package has been updated"
            self.message_post(body=body)
        return True

    def button_skid_label(self):
        return self.env.ref(
            "thinksoft_package_planner.skid_label_report"
        ).report_action(self)

    def button_box_label(self):
        return self.env.ref(
            "thinksoft_package_planner.box_label_report"
        ).report_action(self)
