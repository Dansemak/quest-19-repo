import time

from odoo import api, models


class Box_label_skid(models.AbstractModel):
    _name = "report.thinksoft_package_planner.box_crate_qweb_template"
    _description = "Box Label Crate"

    def _get_max_count(self, package_line, count_type):
        if count_type == "crate":
            crate_no = []
            crates = []
            for line in package_line:
                if line.crates not in crate_no:
                    crate_no.append(line.crates)
            crate_no = ",".join(crate_no)
            if crate_no:
                max_crate = max(crate_no)
            else:
                max_crate = 0
            return int(max_crate)
        else:
            return 0

    def _get_crates(self, package_line):
        crate_no = []
        crates = []
        for line in package_line:
            if line.crates not in crate_no:
                crate_no.append(line.crates)
        crate_no = ",".join(crate_no)
        max_crate = 0
        if crate_no:
            max_crate = max(crate_no)

        for i in range(1, int(max_crate) + 1):
            crates.append({"crate": i})
        return crates

    def _get_box_crates(self, b, package_line):
        packs = []
        product = []
        for box in b:
            for line in package_line:
                qnty = 0
                show = False
                for p in line.package_planner_line:
                    if p.crate_skid == "crate" and p.no == box["crate"]:
                        show = True
                        if line.product_id.id in product:
                            qnty += p.qty_packed
                        else:
                            qnty = p.qty_packed
                            product.append(line.product_id.id)
                if show:
                    packs.append(
                        {
                            str(box["crate"]): [
                                {
                                    "seq_no": line.seq,
                                    "product_id": line.product_id.id,
                                    "name": line.product_id.name,
                                    "desc": line.desc,
                                    "pick_qty": int(line.pick_qty),
                                    "qty": qnty,
                                    "heat": ", ".join(
                                        mtr.heat_number or ""
                                        for mtr in line.mtr_tag_ids
                                    ),
                                    "tagging": line.tagging,
                                    "box": line.boxs,
                                }
                            ]
                        }
                    )
        return packs

    @api.model
    def _get_report_values(self, docids, data=None):
        picking = self.env["stock.picking"].search([("id", "=", docids[0])])
        get_boxes = self._get_crates(picking.package_line)
        docs = picking
        movelines = self._get_box_crates(get_boxes, picking.package_line)
        get_max_count = self._get_max_count(picking.package_line, "crate")
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
