import time

from odoo import api, models


class SkidLabel(models.AbstractModel):
    _name = "report.thinksoft_package_planner.skid_label_template"
    _description = "Skid Label"

    def _get_max_count(self, package_line, count_type):
        if count_type == "skid":
            sk_list = set(line.skid_qty for line in package_line)
            s_list = []
            for skd in sk_list:
                if "," in skd:
                    s_list += [x for x in skd.split(",")]
                else:
                    s_list.append(skd)
            sk_n_list = set(int(x) for x in s_list)
            if sk_n_list:
                max_skid = max(sk_n_list)
            else:
                max_skid = 0
            return max_skid
        else:
            return 0

    def _get_skids(self, package_line):
        skids = []
        sk_list = set(line.skid_qty for line in package_line)
        s_list = []
        for skd in sk_list:
            if "," in skd:
                s_list += [x for x in skd.split(",")]
            else:
                s_list.append(skd)
        sk_n_list = set(int(x) for x in s_list)
        max_skid = 0
        if sk_n_list:
            max_skid = max(sk_n_list)

        for i in range(1, int(max_skid) + 1):
            skids.append({"skid": i})
        return skids

    def _get_box_skids(self, b, package_line):
        packs = []
        product = []
        for box in b:
            for line in package_line:
                qnty = 0
                show = False
                for p in line.package_plan_line_ids:
                    if p.is_skid and p.skid_number == box["skid"]:
                        show = True
                        if line.product_id.id in product:
                            qnty += p.qty_packed
                        else:
                            qnty = p.qty_packed
                            product.append(line.product_id.id)
                if show:
                    packs.append(
                        {
                            str(box["skid"]): [
                                {
                                    "seq_no": line.seq,
                                    "product_id": line.product_id.id,
                                    "name": line.product_id.name,
                                    "description": line.description,
                                    "pick_qty": int(line.pick_qty),
                                    "in_box": line.in_box,
                                    "qty": qnty,
                                    "heat": ", ".join(
                                        mtr.heat_number or ""
                                        for mtr in line.mtr_template_ids
                                    ),
                                    "tagging": line.tagging,
                                    "box": line.box_qty,
                                }
                            ]
                        }
                    )
        return packs

    @api.model
    def _get_report_values(self, docids, data=None):
        picking = self.env["stock.picking"].search([("id", "=", docids[0])])
        get_boxes = self._get_skids(picking.package_plan_ids)
        docs = picking
        movelines = self._get_box_skids(get_boxes, picking.package_plan_ids)
        get_max_count = self._get_max_count(picking.package_plan_ids, "skid")
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
