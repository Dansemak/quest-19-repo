# AGENTS.md — Odoo 19 Module Development

## Project Overview

This project involves **building and analyzing custom Odoo 19 modules**. This `AGENTS.md` lives **inside** the `addons/` folder, which is the project root — each subdirectory here is a custom Odoo module. Odoo base and enterprise source code are available for **reference only** and must never be modified.

---

## Directory Structure

```
addons/                        ← Project root (where this AGENTS.md lives) [dev laptop]
/opt/odoo/addons/              ←   same directory as above, as seen on the server
├── AGENTS.md
├── my_module/                 ← ALL custom module work happens here
│   ├── __manifest__.py
│   ├── __init__.py
│   ├── models/
│   ├── views/
│   ├── controllers/
│   ├── security/
│   ├── data/
│   ├── static/
│   └── tests/
└── another_module/

~/workspace/repos/odoo/19.0/odoo/        ← Odoo Community source (READ-ONLY) [dev laptop]
/opt/odoo/odoo/                ←   same path as above, as seen on the server
~/workspace/repos/odoo/19.0/enterprise/  ← Odoo Enterprise source (READ-ONLY) [dev laptop]
/opt/odoo/enterprise/          ←   same path as above, as seen on the server
```

---

## Critical Constraints

### ⛔ READ-ONLY Paths — NEVER Edit These

These two pairs of paths point to **identical codebases**. The first is how the path appears on your **development laptop**, the second is how the same directory is mounted on the **server**. Use whichever is accessible in your current environment — they are interchangeable.

| Purpose | Dev laptop path | Server path |
|---|---|---|
| Odoo Community core | `~/workspace/repos/odoo/19.0/odoo/` | `/opt/odoo/odoo/` |
| Odoo Enterprise modules | `~/workspace/repos/odoo/19.0/enterprise/` | `/opt/odoo/enterprise/` |

These paths exist **solely for reference**: to understand base models, inherited methods, field definitions, view structures, and existing business logic. If you need to extend something from core, do it via inheritance in a module here in the project root.

### ✅ Work Only Happens In

The project root (this folder) and `/opt/odoo/addons/` on the server are **the same directory**. Create, edit, and delete freely here — changes are reflected on the server.

| Dev laptop path | Server path |
|---|---|
| `./` (this project root) | `/opt/odoo/addons/` |
| `./<module_name>/` | `/opt/odoo/addons/<module_name>/` |

---

## How to Reference Base Code

When analyzing or building a feature, first check the relevant source paths. Use the laptop path or server path interchangeably — they are the same content:

| What you need | Laptop path | Server path |
|---|---|---|
| Base models (res.partner, sale.order, etc.) | `~/workspace/repos/odoo/19.0/odoo/addons/<module>/models/` | `/opt/odoo/odoo/addons/<module>/models/` |
| Base views & templates | `~/workspace/repos/odoo/19.0/odoo/addons/<module>/views/` | `/opt/odoo/odoo/addons/<module>/views/` |
| Enterprise extensions | `~/workspace/repos/odoo/19.0/enterprise/<module>/` | `/opt/odoo/enterprise/<module>/` |
| ORM, fields, api decorators | `~/workspace/repos/odoo/19.0/odoo/odoo/` | `/opt/odoo/odoo/odoo/` |
| Core HTTP / Controllers | `~/workspace/repos/odoo/19.0/odoo/odoo/http.py` | `/opt/odoo/odoo/odoo/http.py` |

**Workflow when extending a base model:**
1. Read the base model in the read-only source to understand fields, methods, and constraints
2. Identify the correct inheritance strategy (`_inherit` vs `_inherits`)
3. Write the extension exclusively in `./<your_module>/models/`

---

## Odoo 19 Module Conventions

### Manifest (`__manifest__.py`)
```python
{
    'name': 'My Module',
    'version': '19.0.1.0.0',       # Always prefix with Odoo version
    'category': 'Customizations/Thinksoft',
    'summary': 'One-line description',
    'author': 'Thinksoft Inc',
    'depends': ['base', 'sale'],    # List minimal required dependencies
    'data': [
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
        'data/my_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/js/my_widget.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
```

### Model File Structure
```python
# my_module/models/my_model.py

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'
    _order = 'name asc'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)

    # Always use _() for translatable strings
    # Always use sudo() deliberately and document why
```

### Inheritance Patterns
```python
# Extend an existing model — most common pattern
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    my_custom_field = fields.Char(string='Custom Field')

    def action_confirm(self):
        # Call super() FIRST (unless intentionally overriding pre-logic)
        res = super().action_confirm()
        # Your logic here
        return res
```

### Security (`security/ir.model.access.csv`)
```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model manager,model_my_model,base.group_system,1,1,1,1
```

### View XML Patterns
```xml
<!-- Always use meaningful external IDs -->
<record id="view_my_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <group>
                    <field name="name"/>
                </group>
            </sheet>
        </form>
    </field>
</record>

<!-- Inherit and extend a base view — prefer xpath over position="replace" -->
<record id="view_sale_order_form_inherit_my_module" model="ir.ui.view">
    <field name="name">sale.order.form.inherit.my_module</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='partner_id']" position="after">
            <field name="my_custom_field"/>
        </xpath>
    </field>
</record>
```

---

## Development Workflow

### When Asked to Analyze a Module
1. Read `./<module>/__manifest__.py` to understand dependencies and file list
2. Read model files in `./<module>/models/`
3. Cross-reference inherited models in `~/workspace/repos/odoo/19.0/odoo/` or `enterprise/`
4. Report: models, fields, methods, view structure, access rights, data files

### When Asked to Build a Feature
1. Clarify: which base models are involved? Check read-only source first
2. Determine: new model or extension of existing?
3. Plan file structure before writing any code
4. Follow the order: model → security → views → data → tests
5. Validate: do `_inherit` references match actual model `_name` in base?

### When Asked to Debug
1. Check model `_name` matches `ir.model.access.csv` model_id entries
2. Check `__init__.py` files import all model files
3. Check `__manifest__.py` lists all XML files in `data`
4. Check `depends` covers all modules whose models are referenced

---

## Odoo 19 Specific Notes

> ⚠️ **Odoo 19 was released around October 2025, just after this file's knowledge cutoff. Always verify these notes against the official [Odoo 19 release notes](https://www.odoo.com/odoo-19-release-notes) and the read-only source at `~/workspace/repos/odoo/19.0/`.**

- **Python 3.12+** required — modern syntax fully supported
- **OWL 2** remains the frontend framework — `Component`, `useState`, `useRef`, `onMounted`, `xml`
- **`@api.model`** — use for class-level methods (no recordset)
- **`@api.depends`** — required for all computed fields; list ALL dependencies including nested fields
- **`@api.constrains`** — for Python-level validation, raises `ValidationError`
- **`@api.onchange`** — for UI-only reactive behavior (not saved unless field changes)
- **`copy=False`** — set on fields that should not copy on record duplication
- **`groups=` on fields/views** — use for field-level access control
- **`sudo()`** — always document why you're bypassing record rules
- **`with_context()`** — pass context explicitly; never mutate `self.env.context` directly
- **`_rec_names_search`** — use this list attribute instead of overriding `name_search()` for multi-field search
- **`precommit` hooks** — use `env.cr.precommit.add()` for deferred pre-commit actions
- **lists** — use `list` for xml lists
- Translations: wrap all user-facing strings in `_('...')`, import `_` from `odoo`
- **⚠️ Verify before using:** Any module that existed in 17/18 may have structural changes — always read the base source before inheriting

---

## Common Pitfalls to Avoid

| Pitfall | Correct Approach |
|---|---|
| Editing base Odoo source | Always use `_inherit` in a module here |
| Forgetting `super()` in overrides | Call `super()` unless deliberately blocking |
| `compute=` without `store=True/False` decision | Decide explicitly; stored fields are searchable |
| Missing `@api.depends` on computed fields | List every field the compute reads |
| Hardcoded IDs or company-specific data | Use `ref()` in XML, `env.ref()` in Python |
| Business logic in views/controllers | Keep logic in model methods |
| Direct SQL without good reason | Use ORM; only bypass for performance-critical reporting |

---

## Module Naming Conventions

| Pattern | Example |
|---|---|
| Module technical name | `sale_custom_pricing` (snake_case) |
| Model `_name` | `sale.custom.pricing` (dot.notation) |
| XML external IDs | `view_sale_custom_pricing_form` |
| Python class name | `SaleCustomPricing` (PascalCase) |
| Field names | `custom_price_unit` (snake_case) |

---

## Quick Reference: Field Types

```python
# Scalar
name        = fields.Char(string='Name', required=True, size=128)
description = fields.Text()
amount      = fields.Float(digits='Product Price')
quantity    = fields.Integer()
is_active   = fields.Boolean(default=True)
date_order  = fields.Date()
datetime_c  = fields.Datetime(default=fields.Datetime.now)
html_notes  = fields.Html()
binary_file = fields.Binary(attachment=True)

# Relational
partner_id  = fields.Many2one('res.partner', string='Partner', ondelete='restrict')
tag_ids     = fields.Many2many('res.partner.category', string='Tags')
line_ids    = fields.One2many('sale.order.line', 'order_id', string='Lines')

# Computed
total       = fields.Float(compute='_compute_total', store=True)

@api.depends('line_ids.price_subtotal')
def _compute_total(self):
    for rec in self:
        rec.total = sum(rec.line_ids.mapped('price_subtotal'))
```

---

## Testing

Place tests in `./<module>/tests/`:
```python
# tests/__init__.py → from . import test_my_model
# tests/test_my_model.py

from odoo.tests.common import TransactionCase

class TestMyModel(TransactionCase):

    def setUp(self):
        super().setUp()
        self.MyModel = self.env['my.model']

    def test_create_record(self):
        record = self.MyModel.create({'name': 'Test'})
        self.assertEqual(record.name, 'Test')
```

Run with:
```bash
python odoo-bin -c odoo.conf --test-enable --stop-after-init -u my_module
```
