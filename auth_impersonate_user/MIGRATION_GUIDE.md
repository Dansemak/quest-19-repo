# Migration Guide: Auth Impersonate User from Odoo 18.0 to 19.0

## Overview
This guide explains how to migrate the Auth Impersonate User module from Odoo 18.0 to 19.0.

## Key Changes Summary

### 1. XML View Syntax Updates

#### Tree View XPath Location (Critical)
**Odoo 18.0:**
```xml
<xpath expr="//field[@name='company_id']" position="after">
    <field name="can_impersonate_user" column_invisible="1" />
    <field name="can_be_impersonated" column_invisible="1" />
    <button ... />
</xpath>
```

**Odoo 19.0:**
```xml
<field name="login" position="after">
    <field name="can_impersonate_user" column_invisible="1" />
    <field name="can_be_impersonated" column_invisible="1" />
    <button ... />
</field>
```

**Reason:** Odoo 19 restructured the base user tree view completely. The `company_id` field xpath no longer works, and even `//tree` xpath doesn't work due to the view structure. Using the `login` field as an anchor point is reliable because it's a core field that will always be present in the user tree view.

#### Form View Field Visibility
**Odoo 18.0:**
```xml
<field name="can_impersonate_user" column_invisible="1" />
<field name="can_be_impersonated" column_invisible="1" />
```

**Odoo 19.0:**
```xml
<field name="can_impersonate_user" invisible="1" />
<field name="can_be_impersonated" invisible="1" />
```

**Reason:** Odoo 19 standardizes visibility control using `invisible` attribute for form views, while `column_invisible` remains for tree/list views.

#### Button Visibility Domains
**Odoo 18.0:**
```xml
<button
    name="impersonate_user"
    invisible="(can_impersonate_user == False),(can_be_impersonated == False)"
    string="Impersonate"
    type="object"
/>
```

**Odoo 19.0:**
```xml
<button
    name="impersonate_user"
    invisible="can_impersonate_user == False or can_be_impersonated == False"
    string="Impersonate"
    type="object"
/>
```

**Reason:** Odoo 19 uses cleaner boolean logic operators (`or`, `and`) instead of comma-separated conditions.

### 2. Demo Data Structure

## Step-by-Step Migration Process

### Step 1: Backup
1. Backup your Odoo database
2. Backup the current module files
3. Note any customizations you've made

### Step 2: Prepare Environment
1. Ensure you're running Odoo 19.0
2. Update Python to 3.10 or higher if needed
3. Install/update all dependencies

### Step 3: Install Updated Module
1. Remove or rename the old module directory
2. Copy the new `auth_impersonate_user-19.0.1.0.0` directory to your addons path
3. Restart Odoo server
4. Update the module:
   ```bash
   odoo-bin -u auth_impersonate_user -d your_database
   ```

### Step 4: Verify Installation
1. Log in as admin user
2. **Assign impersonation permissions**:
   - Go to Settings → Users & Companies → Users
   - Edit your admin user
   - In Access Rights tab, ensure "Can impersonate user" group is checked
   - For demo/test users, ensure "Can be impersonated" group is checked
3. Verify the "Impersonate" button appears for eligible users
4. Test impersonation functionality
5. Test logout and de-impersonation

### Step 5: Update Custom Code (if applicable)
If you've customized this module:

1. **Custom Views**: Update any inherited views to use new syntax:
   - Change `column_invisible` to `invisible` in form views
   - Update domain expressions to use `or`/`and` operators
   - Update XPath expressions if you're targeting specific fields

2. **Custom Security**: If you've added custom groups:
   - Remove references to `base.module_category_usability`
   - Groups will work without explicit category assignment

3. **Custom Controllers**: Session and cache handling has changed:
   - Replace `request.session.custom_attr = value` with `request.session["custom_attr"] = value`
   - Replace `if request.session.custom_attr:` with `if request.session.get("custom_attr"):`
   - Replace `request.env["model"].clear_caches()` with `request.env.registry.clear_cache()` (note: singular)
   - These are critical for Odoo 19 compatibility

4. **Custom Models**: No changes needed to model definitions or computed fields

## Testing Checklist

- [ ] Admin can see "Impersonate" button on eligible users
- [ ] Users with impersonation rights can impersonate other users
- [ ] Impersonation correctly updates session
- [ ] User interface shows correct user after impersonation
- [ ] Logout returns to original user (not full logout)
- [ ] Security groups work correctly
- [ ] Demo users have proper permissions
- [ ] Translation files work correctly
- [ ] No errors in server logs
- [ ] No console errors in browser

## Troubleshooting

### Issue: Module Won't Install
**Solution:** 
- Check Odoo version is 19.0
- Verify all files are in correct structure
- Check file permissions
- Review server logs for specific errors

### Issue: Buttons Not Visible
**Solution:**
- Clear browser cache
- Restart Odoo server
- Update module with `-u` flag
- Verify security groups are assigned
- Check user permissions

### Issue: Impersonation Not Working
**Solution:**
- Verify user has `impersonate_admin_group` permission
- Verify target user has `impersonate_user_group` permission
- Check server logs for errors
- Verify session handling in browser

### Issue: Cannot Return to Original User
**Solution:**
- Check session data is properly stored
- Verify logout controller override is working
- Clear browser cookies and retry
- Check server logs for session errors

## Technical Details

### Files Modified
1. `__manifest__.py` - Version number
2. `views/res_users.xml` - XML syntax updates
3. `demo/res_users.xml` - Structure cleanup
4. `i18n/de.po` - Version number
5. `i18n/de_CH.po` - Version number

### Files Unchanged
1. `controllers/main.py`
2. `models/res_users.py`
3. `security/security.xml`
4. All `__init__.py` files
5. `README.rst`
6. `static/description/index.html`
7. `tests/TEST_INSTRUCTIONS.rst`

## Rollback Procedure
If you need to rollback:

1. Stop Odoo server
2. Restore database from backup
3. Replace module files with v18.0 version
4. Restart Odoo server
5. Update module if needed

## Support
For additional help:
- GitHub Issues: Create an issue in the module repository
- Documentation: https://www.odoo-wiki.org/
- Commercial Support: https://www.mint-system.ch

## License
This module is licensed under AGPL-3.
