import logging

from odoo import fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class PruchaseReviewReport(models.Model):
    _name = "purchase.review.report"
    _auto = False
    _rec_name = "product_tmpl_id"
    _order = "product_tmpl_id asc"
    _table = "purchase_review_report_view"
    _description = "Purchase Review Report"

    """
        The id field is set to be the stock_warehouse_orderpoint id (swo_id) for a given product.
        It is set this way to facilitate generating POs from the report.
    """

    # Fields generated for the view
    # report_id = fields.Integer("", readonly=True)
    product_tmpl_id = fields.Many2one("product.template", string="Name", readonly=True)

    description = fields.Html(
        related="product_tmpl_id.description", string="Description", readonly=True
    )

    category_id = fields.Many2one("product.category", readonly=True)

    product_id = fields.Many2one("product.product", readonly=True)

    warehouse_id = fields.Many2one("stock.warehouse", readonly=True)

    swo_id = fields.Many2one(
        "stock.warehouse.orderpoint", string="Order Point", readonly=True
    )

    daily_average = fields.Float(string="Daily Consumed/Sold")

    min_qty = fields.Float(
        related="swo_id.product_min_qty",
        string="Current Min",
        readonly=True,
        digits=(100, 2),
    )

    max_qty = fields.Float(
        related="swo_id.product_max_qty",
        string="Current Max",
        readonly=True,
        digits=(100, 2),
    )

    qty_to_order = fields.Float(
        related="swo_id.qty_to_order",
        string="To Order",
        readonly=True,
        digits=(100, 2),
    )

    delay = fields.Integer("Delay", readonly=True)

    quarter_1 = fields.Float(
        string="Q1",
        readonly=True,
        digits=(100, 2),
    )
    quarter_2 = fields.Float(
        string="Q2",
        readonly=True,
        digits=(100, 2),
    )
    quarter_3 = fields.Float(
        string="Q3",
        readonly=True,
        digits=(100, 2),
    )
    quarter_4 = fields.Float(
        string="Q4",
        readonly=True,
        digits=(100, 2),
    )
    total = fields.Float(
        string="Total Consumed/Sold",
        readonly=True,
        digits=(100, 2),
    )
    quantity_available = fields.Float(
        string="Quantity Available",
        help="Quantity on hand = Quantity on Hand - Reserved Quantity",
    )
    quantity_on_hand = fields.Float(
        string="Quantity On Hand",
        help="Quantity on hand = Quantity available + Reserved Quantity",
        digits=(100, 2),
    )
    reserved_quantity = fields.Float(
        string="Reserved quantity",
        help="Reserved Quantity",
        digits=(100, 2),
    )

    # Fields navigated from stock.warehouse.orderpoint to product.product
    qty_incoming = fields.Float(
        related="product_id.incoming_qty",
        string="Incoming",
        help="Incoming Quantity",
        digits=(100, 2),
    )

    qty_outgoing = fields.Float(
        related="product_id.outgoing_qty",
        string="Outgoing",
        help="Outgoing Quantity",
        digits=(100, 2),
    )

    forecast = fields.Float(
        related="product_id.virtual_available",
        string="Forecast",
        help="Forecast = (current inventory – outgoing) + incoming",
        digits=(100, 2),
    )

    branch_min = fields.Float(
        string="Branch  Min", help="daily_average * (delay + 30)", readonly=True
    )

    branch_max = fields.Float(
        string="Branch max", help="daily_average * delay + (total / 4)", readonly=True
    )

    suggested_min = fields.Float(
        string="Suggested Min",
        help="daily_average * (delay + 30)",
        readonly=True,
    )

    suggested_max = fields.Float(
        string="Suggested Max",
        help="daily_average  * (delay + 90)",
        readonly=True,
    )

    # Computed fields
    suggested_buy = fields.Float(
        compute="_compute_qty",
        string="Suggested Buy",
        help="max - forecast + min( branch_total_sales * delay, forecast)",
        readonly=True,
    )

    _depends = {
        "product.template": ["name", "description", "active", "categ_id"],
        "product.product": [
            "product_tmpl_id",
            "active",
        ],
        "stock.move": [
            "product_id",
            "warehouse_id",
            "raw_material_production_id",
            "product_uom_qty",
            "reference",
            "date",
            "bom_line_id",
        ],
        "sale.report": ["product_uom_qty", "date", "product_id", "warehouse_id"],
        "product.supplierinfo": ["product_tmpl_id", "delay"],
        "stock.warehouse": [
            "name",
        ],
        "stock.warehouse.orderpoint": ["warehouse_id"],
    }

    def init(self):
        # self.refresh_materialized_view()
        self.materialized_purchase_review_report_view()

    def refresh_reload_view(self):
        self.refresh_materialized_view()
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }

    def refresh_materialized_view(self):
        try:
            self.env.cr.execute("REFRESH MATERIALIZED VIEW purchase_review_report_view")
            self.env.cr.commit()
            return True
        except Exception as e:
            raise UserError(f"Error refreshing materialized view: {str(e)}")

    def _compute_qty(self):
        for product in self:
            product.suggested_buy = (
                product.max_qty
                - product.forecast
                + min(product.daily_average * product.delay, product.forecast)
            )

    def materialized_purchase_review_report_view(self):
        """
        Create or update the materialized view for purchase review report.
        """

        self.env.cr.execute(
            """SELECT to_regclass('public.purchase_review_report_view')"""
        )
        result = self.env.cr.fetchone()

        if result and result[0]:
            self.refresh_materialized_view()
        else:
            self.env.cr.execute("""
                CREATE MATERIALIZED VIEW IF NOT EXISTS purchase_review_report_view AS
                WITH s_report_data AS (
                        SELECT
                            sol.id AS id,
                            sol.product_id AS product_id,
                            sm.warehouse_id AS warehouse_id,
                            sol.product_uom_qty AS product_uom_qty,
                            so.date_order AS date
                        FROM sale_order_line sol
                        JOIN sale_order so
                            ON so.id = sol.order_id
                        JOIN stock_move sm
                            ON sm.sale_line_id = sol.id
                            AND sm.state = 'done'
                        WHERE
                            so.state IN ('sale', 'done')
                            AND so.date_order >= CURRENT_DATE - INTERVAL '365 days'
                            AND sm.warehouse_id IN (1, 2)
                            AND sol.display_type IS NULL
                    ),
                    stock_move_data AS (
                        SELECT
                            sm.product_id,
                            sm.warehouse_id,
                            sm.product_uom_qty,
                            sm.date,
                            sm.raw_material_production_id,
                            sm.bom_line_id,
                            sm.reference
                        FROM stock_move sm
                        WHERE sm.date >= CURRENT_DATE - INTERVAL '365 days'
                        AND sm.state = 'done'
                        AND sm.warehouse_id IN (1, 2)
                    ),
                    sales_quarters AS (
                                    SELECT
                                        product_id,
                                        warehouse_id,
                                        SUM(CASE WHEN sr.date >= CURRENT_DATE - INTERVAL '365 days'
                                                    AND sr.date < CURRENT_DATE - INTERVAL '274 days' THEN product_uom_qty ELSE 0 END) AS q1,
                                        SUM(CASE WHEN sr.date >= CURRENT_DATE - INTERVAL '274 days'
                                                    AND sr.date < CURRENT_DATE - INTERVAL '183 days' THEN product_uom_qty ELSE 0 END) AS q2,
                                        SUM(CASE WHEN sr.date >= CURRENT_DATE - INTERVAL '183 days'
                                                    AND sr.date < CURRENT_DATE - INTERVAL '92 days' THEN product_uom_qty ELSE 0 END) AS q3,
                                        SUM(CASE WHEN sr.date >= CURRENT_DATE - INTERVAL '92 days'
                                                    AND sr.date < CURRENT_DATE + INTERVAL '1 days' THEN product_uom_qty ELSE 0 END) AS q4,
                                        SUM(COALESCE(product_uom_qty, 0) ) AS qty,
                                        SUM(product_uom_qty) / 365 AS daily_average
                                    FROM s_report_data sr
                                    GROUP BY product_id, warehouse_id
                    ),
                    stock_quarters AS (
                                    SELECT
                                        sm.product_id,
                                        sm.warehouse_id,
                                        sum(q1) q1, sum(q2) q2, sum(q3) q3, sum(q4) q4, sum(qty) qty, sum(qty)/365 daily_average
                                    FROM (
                                        SELECT product_id, warehouse_id, product_uom_qty q1, 0 q2, 0 q3, 0 q4, product_uom_qty qty
                                        FROM stock_move_data smd
                                        WHERE smd.raw_material_production_id IS NOT NULL AND smd.date >= CURRENT_DATE - INTERVAL '365 days' and smd.date < CURRENT_DATE - INTERVAL '274 days'
                                        UNION ALL
                                        SELECT product_id, warehouse_id, 0 q1, product_uom_qty q2, 0 q3, 0 q4, product_uom_qty qty
                                        FROM stock_move_data smd
                                        WHERE smd.raw_material_production_id IS NOT NULL AND smd.date >= CURRENT_DATE - INTERVAL '274 days' and smd.date < CURRENT_DATE - INTERVAL '183 days'
                                        UNION ALL
                                        SELECT product_id, warehouse_id, 0 q1, 0 q2, product_uom_qty q3, 0 q4, product_uom_qty qty
                                        FROM stock_move_data smd
                                        WHERE smd.raw_material_production_id IS NOT NULL AND smd.date >= CURRENT_DATE - INTERVAL '183 days' and smd.date < CURRENT_DATE - INTERVAL '92 days'
                                        UNION ALL
                                        SELECT product_id, warehouse_id, 0 q1, 0 q2, 0 q3, product_uom_qty q4, product_uom_qty qty
                                        FROM stock_move_data smd
                                        WHERE smd.raw_material_production_id IS NOT NULL AND smd.date >= CURRENT_DATE - INTERVAL '92 days' and smd.date < CURRENT_DATE + INTERVAL '1 days'
                                        UNION ALL
                                        SELECT product_id, warehouse_id, product_uom_qty q1, 0 q2, 0 q3, 0 q4, product_uom_qty qty
                                        FROM stock_move_data smd
                                        WHERE smd.raw_material_production_id IS NULL AND smd.date >= CURRENT_DATE - INTERVAL '365 days' and smd.date < CURRENT_DATE - INTERVAL '274 days' AND bom_line_id IS NOT NULL AND reference LIKE '%%OUT%%'
                                        UNION ALL
                                        SELECT product_id, warehouse_id, 0 q1, product_uom_qty q2, 0 q3, 0 q4, product_uom_qty qty
                                        FROM stock_move_data smd
                                        WHERE smd.raw_material_production_id IS NULL AND smd.date >= CURRENT_DATE - INTERVAL '274 days' and smd.date < CURRENT_DATE - INTERVAL '183 days' AND bom_line_id IS NOT NULL AND reference LIKE '%%OUT%%'
                                        UNION ALL
                                        SELECT product_id, warehouse_id, 0 q1, 0 q2, product_uom_qty q3, 0 q4, product_uom_qty qty
                                        FROM stock_move_data smd
                                        WHERE smd.raw_material_production_id IS NULL AND smd.date >= CURRENT_DATE - INTERVAL '183 days' and smd.date < CURRENT_DATE - INTERVAL '92 days' AND bom_line_id IS NOT NULL AND reference LIKE '%%OUT%%'
                                        UNION ALL
                                        SELECT product_id, warehouse_id, 0 q1, 0 q2, 0 q3, product_uom_qty q4, product_uom_qty qty
                                        FROM stock_move_data smd
                                        WHERE smd.raw_material_production_id IS NULL AND smd.date >= CURRENT_DATE - INTERVAL '92 days' and smd.date < CURRENT_DATE + INTERVAL '1 days' AND bom_line_id IS NOT NULL AND reference LIKE '%%OUT%%'
                                    ) AS sm
                                    GROUP BY sm.product_id, sm.warehouse_id
                                )
                    SELECT
                            cd.product_id,
                            cd.warehouse_id,
                            COALESCE(sq.quantity_available,0) AS quantity_available,
                            COALESCE(sq.quantity,0) AS quantity_on_hand,
                            COALESCE(sq.reserved_quantity,0) AS reserved_quantity,
                            pp.product_tmpl_id,
                            pp.category_id,
                            sd.delay AS delay,
                            pp.swo_id,
                            pp.swo_id AS id,
                            SUM(q1) AS quarter_1,
                            SUM(q2) AS quarter_2,
                            SUM(q3) AS quarter_3,
                            SUM(q4) AS quarter_4,
                            SUM(qty) AS total,
                            SUM(qty)/365 AS daily_average,
                            SUM(qty)/365 * (sd.delay + 30) AS suggested_min,
                            SUM(qty)/365 * (sd.delay + 90) AS suggested_max,
                            SUM(qty)/365 * (sd.delay + 30) AS branch_min,
                            SUM(qty) / 4 + SUM(qty)/365 * sd.delay AS branch_max
                        FROM (
                                SELECT * FROM sales_quarters
                                UNION ALL
                                SELECT * FROM stock_quarters) cd
                        LEFT OUTER JOIN (
                                SELECT ps1.delay,
                                        ps1.product_tmpl_id
                                FROM product_supplierinfo ps1
                                WHERE "sequence" = (
                                            SELECT "sequence"
                                            FROM product_supplierinfo ps2
                                            WHERE ps2.product_tmpl_id = ps1.product_tmpl_id
                                        ORDER BY "sequence" ASC
                                            LIMIT 1)
                            ) AS sd ON sd.product_tmpl_id = cd.product_id
                        INNER JOIN
                                    (
                                        SELECT
                                                pp.id,
                                                pp.product_tmpl_id,
                                                pt.categ_id as category_id,
                                                swo.id as swo_id,
                                                swo.warehouse_id AS swo_warehouse_id
                                            FROM product_product pp
                                            JOIN stock_warehouse_orderpoint swo ON swo.product_id = pp.id
                                            JOIN product_template pt ON pt.id = pp.product_tmpl_id
                                            WHERE pp.active = TRUE
                                    ) pp ON pp.id = cd.product_id AND pp.swo_warehouse_id = cd.warehouse_id
                        LEFT JOIN (
                                        SELECT sq.product_id,
                                                pp.name,
                                                sl.parent_root,
                                                sl.warehouse_id,
                                                SUM(sq.quantity)-SUM(sq.reserved_quantity) AS quantity_available,
                                                SUM(sq.quantity) AS quantity,
                                                SUM(sq.reserved_quantity) AS reserved_quantity
                                            FROM stock_quant sq
                                            JOIN (
                                                SELECT  sl.id,
                                                        sl.complete_name,
                                                        'EWH/Stock' parent_root,
                                                        1  AS warehouse_id
                                                    FROM stock_location sl
                                                    WHERE complete_name like 'EWH/Stock%'
                                                UNION ALL
                                                SELECT  sl.id,
                                                        sl.complete_name,'
                                                        CWH/Stock.C' parent_root,
                                                        2 AS warehouse_id
                                                    FROM stock_location sl
                                                    WHERE complete_name like 'CWH/Stock.C%'
                                                ) sl on sq.location_id = sl.id
                                            JOIN (
                                                    SELECT  pp.id,
                                                            pt.name
                                                        FROM product_product pp
                                                        JOIN product_template pt on pp.product_tmpl_id = pt.id) pp ON sq.product_id = pp.id
                                                        WHERE (sl.complete_name like 'EWH/Stock%' OR sl.complete_name LIKE 'CWH/Stock.C%')
                                                    GROUP BY sq.product_id,pp.name,sl.parent_root, sl.warehouse_id
                                                    ORDER BY pp.name,sl.parent_root
                                            ) sq ON sq.product_id = cd.product_id AND sq.warehouse_id = cd.warehouse_id
                        GROUP BY cd.product_id, cd.warehouse_id, pp.product_tmpl_id, pp.swo_id, sd.delay, pp.category_id, sq.quantity_available, sq.quantity, sq.reserved_quantity
            """)
