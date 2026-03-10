# Changelog - Auth Impersonate User Module

## Version 19.0.1.0.0 - Migration to Odoo 19

### Changes Made for Odoo 19 Compatibility

#### 1. Version Updates
- Updated module version from `18.0.1.0.0` to `19.0.1.0.0` in `__manifest__.py`
- Updated translation files (.po) version from Odoo 17.0/18.0 to 19.0

#### 2. XML View Updates
**File: `views/res_users.xml`**

**Tree View (Critical Fix):**
- Changed XPath location strategy to target the `login` field using `position="after"`
- Reason: Odoo 19 changed the base user tree view structure significantly
- The `login` field is a core field that will always be present in the user tree view
- This approach is more robust than trying to locate container elements

**Form View:**
- Changed `column_invisible` attribute to `invisible` for fields in form view (line 23-24)
  - Odoo 19 standardizes on using `invisible` attribute for all field visibility controls
  - Tree view uses `column_invisible` which is still valid for list views
- Updated `invisible` domain syntax from comma-separated conditions to `or` operator
  - Old: `invisible="(can_impersonate_user == False),(can_be_impersonated == False)"`
  - New: `invisible="can_impersonate_user == False or can_be_impersonated == False"`
  - This follows Odoo 19's cleaner domain expression syntax

#### 3. Security Updates
**File: `security/security.xml`**
- Removed `category_id` references to `base.module_category_usability`
  - Reason: Odoo 19 removed or renamed this category
  - Groups still function correctly without explicit category assignment
  - They will appear under "Other" in the user groups interface
- Removed direct `users` field assignment from groups
  - Reason: The `users` field on `res.groups` model has been removed/changed in Odoo 19
  - User-to-group assignment is now done via `groups_id` field on the user model
  - Added `implied_ids` to make "Can impersonate user" automatically available to system users
  - Demo data still assigns groups to users correctly via the user model

#### 4. Demo Data Updates
**File: `demo/res_users.xml`**
- Cleaned up XML structure by removing nested `<odoo>` tags
- Added proper XML declaration at the top of the file

#### 5. Files Maintained (No Changes Required)
The following files required no changes and work as-is in Odoo 19:
- `models/res_users.py` - Model and computed fields
- All Python `__init__.py` files
- `README.rst`
- Translation files (updated version numbers only)
- `static/description/index.html`

#### 6. Controller Updates (Critical for Runtime)
**File: `controllers/main.py`**
- Changed session attribute assignment to dictionary-style access
  - Old: `request.session.impersonator_uid = value`
  - New: `request.session["impersonator_uid"] = value`
- Reason: Odoo 19's Session object no longer allows dynamic attribute assignment
- Changed session attribute reading to use `.get()` method for safety
  - Old: `if request.session.impersonator_uid:`
  - New: `if request.session.get("impersonator_uid"):`
- Changed cache clearing method
  - Old: `request.env["res.users"].clear_caches()`
  - New: `request.env.registry.clear_cache()` (note: singular "cache")
- Reason: Model-level `clear_caches()` method removed in Odoo 19, use registry-level `clear_cache()` instead
- These changes prevent AttributeError exceptions during impersonation

### Key Compatibility Notes

1. **Backward Incompatible Changes**:
   - The `column_invisible` to `invisible` change in form views is a breaking change
   - The domain syntax update is required for Odoo 19 compatibility
   - Session handling changed from attribute to dictionary access (critical runtime fix)

2. **API Changes**:
   - Session object no longer allows dynamic attribute assignment
   - Must use dictionary-style access: `session["key"]` instead of `session.key`
   - Model inheritance and computed fields work the same way

3. **Testing**:
   - All test instructions remain valid
   - No changes needed to test procedures

### Installation Instructions

1. Remove the old version 18.0 module
2. Install this version 19.0 module
3. Update module in Odoo
4. Clear browser cache
5. Test impersonation functionality as per `tests/TEST_INSTRUCTIONS.rst`

### Compatibility

- **Odoo Version**: 19.0
- **Python Version**: 3.10+
- **Dependencies**: web (core module)
- **License**: AGPL-3

### Migration Checklist

- [x] Updated version numbers
- [x] Updated XML view syntax (invisible attributes)
- [x] Updated domain expressions
- [x] Cleaned up demo data structure
- [x] Updated translation file versions
- [x] Verified Python code compatibility
- [x] Maintained backward compatibility where possible
- [x] Documented all changes

### Support

For issues or questions regarding this migration:
- Visit: https://www.mint-system.ch
- Documentation: https://www.odoo-wiki.org/
