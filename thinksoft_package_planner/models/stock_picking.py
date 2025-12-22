from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    package_plan_ids = fields.One2many("package.plan", "picking_id", "Package Details")

    def button_create_packages(self):
        package_plan = self.env["package.plan"]
        message = "Package has been updated"
        for move in self.move_ids:
            res = {
                "product_id": move.product_id.id,
                "seq_no": move.seq_no,
                "description": move.description_picking,
                "picking_id": self.id,
                "pick_qty": move.quantity if move.picked else 0,
                "stock_move_id": move.id,
                "tagging": move.tagging,
                "mtr_template_ids": move.mtr_template_ids
            }

            packages = package_plan.search([("stock_move_id", "=", move.id)])
            
            if not packages:
                move.package_plan_id = package_plan.create(res)
                message = "Package has been created"
            else:
                packages.write(res)
                move.package_plan_id = packages[0].id
        
        self.message_post(body=message)

        return

    def button_skid_label(self):
        return self.env.ref(
            "thinksoft_package_planner.skid_label_report"
        ).report_action(self)

    def button_box_label(self):
        return self.env.ref(
            "thinksoft_package_planner.box_label_report"
        ).report_action(self)
