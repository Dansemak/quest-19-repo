import time

from odoo import api, models


class Box_label(models.AbstractModel):
    _name = "report.thinksoft_package_planner.box_labels_qweb_template"
    _description = "Box Label"

    def _get_boxes(self, package_line):
        inbox = []
        boxes = []
        for line in package_line:
            for l in line.package_planner_line:
                if l.pack_in_no not in inbox:
                    inbox.append(l.pack_in_no)
        inbox.sort()

        for i in inbox:
            boxes.append({"box": i})
        return boxes

    def _get_box_label(self, b, package_line):
        packs = []
        for box in b:
            for line in package_line:
                for p in line.package_planner_line:
                    if p.pack_in_no == box["box"]:
                        packs.append(
                            {
                                str(box["box"]): [
                                    {
                                        "seq_no": line.seq,
                                        "product_id": line.product_id.id,
                                        "name": line.product_id.name,
                                        "pick_qty": int(line.pick_qty),
                                        "qty": p.qty_packed,
                                        "pack_in_no": p.pack_in_no,
                                        "heat": ", ".join(
                                            mtr.heat_number or ""
                                            for mtr in line.mtr_tag_ids
                                        ),
                                        "desc": line.desc,
                                        "tagging": line.tagging,
                                    }
                                ]
                            }
                        )
        return packs

    def _get_max_count(self, package_line, count_type):
        if count_type == "box":
            inbox = []
            for line in package_line:
                for l in line.package_planner_line:
                    if l.pack_in_no not in inbox:
                        inbox.append(l.pack_in_no)
            inbox.sort()
            if inbox:
                return int(max(inbox))
        else:
            return 0

    @api.model
    def _get_report_values(self, docids, data=None):
        picking = self.env["stock.picking"].search([("id", "=", docids[0])])
        get_boxes = self._get_boxes(picking.package_line)
        docs = picking
        movelines = self._get_box_label(get_boxes, picking.package_line)
        get_max_count = self._get_max_count(picking.package_line, "box")
        return {
            "doc_ids": docids,
            "data": {},
            "doc_model": "stock.picking",
            "docs": docs,
            "time": time,
            "get_box_label": movelines,
            "get_boxes": get_boxes,
            "total_boxes": get_max_count,
        }
