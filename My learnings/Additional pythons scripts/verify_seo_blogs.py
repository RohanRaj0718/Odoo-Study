"""
Verify every claim in the SEO blogs against live Odoo 19.
Checks: pricelists, price rules, discount settings, loyalty programs, etc.
"""
import xmlrpc.client
import json

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
print(f"Authenticated: uid={uid}")
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def search_read(model, domain=[], fields=[], limit=0):
    kwargs = {'fields': fields}
    if limit:
        kwargs['limit'] = limit
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], kwargs)

def fields_get(model, attrs=['string','type','selection','help']):
    return models.execute_kw(DB, uid, PASSWORD, model, 'fields_get', [], {'attributes': attrs})

# ═══════════════════════════════════════════
# 1. Check Odoo version
# ═══════════════════════════════════════════
ver = common.version()
print(f"\n=== ODOO VERSION ===")
print(f"Server version: {ver.get('server_version')}")

# ═══════════════════════════════════════════
# 2. Check Settings: Pricelists & Discounts
# ═══════════════════════════════════════════
print(f"\n=== SALES SETTINGS ===")
try:
    # Check if pricelist/discount settings exist
    settings = search_read('res.config.settings', [], [
        'group_product_pricelist', 'group_discount_per_so_line',
        'group_loyalty_card', 'module_loyalty'
    ], limit=1)
    if settings:
        s = settings[0]
        print(f"  Pricelists enabled (group_product_pricelist): {s.get('group_product_pricelist')}")
        print(f"  Discounts enabled (group_discount_per_so_line): {s.get('group_discount_per_so_line')}")
        print(f"  Loyalty enabled: {s.get('group_loyalty_card', 'N/A')}")
        print(f"  Loyalty module: {s.get('module_loyalty', 'N/A')}")
except Exception as e:
    print(f"  Settings check error: {e}")

# Check via ir.config_parameter or res.groups
try:
    groups = search_read('res.groups', [('full_name', 'ilike', 'pricelist')], ['full_name','name'])
    print(f"\n  Pricelist-related groups:")
    for g in groups:
        print(f"    - {g['full_name']}")
except:
    pass

try:
    groups = search_read('res.groups', [('full_name', 'ilike', 'discount')], ['full_name','name'])
    print(f"\n  Discount-related groups:")
    for g in groups:
        print(f"    - {g['full_name']}")
except:
    pass

# ═══════════════════════════════════════════
# 3. Check Pricelist model fields
# ═══════════════════════════════════════════
print(f"\n=== PRICELIST MODEL FIELDS ===")
pl_fields = fields_get('product.pricelist')
key_fields = ['name', 'currency_id', 'company_id', 'country_group_ids', 'item_ids',
              'discount_policy', 'active']
for f in key_fields:
    if f in pl_fields:
        info = pl_fields[f]
        sel = info.get('selection', '')
        print(f"  {f}: type={info['type']}, label='{info['string']}'{', selection='+str(sel) if sel else ''}")
    else:
        print(f"  {f}: NOT FOUND in model")

# Check for any other interesting fields
print(f"\n  All pricelist fields: {sorted(pl_fields.keys())}")

# ═══════════════════════════════════════════
# 4. Check Pricelist Item (price rule) fields
# ═══════════════════════════════════════════
print(f"\n=== PRICELIST ITEM (PRICE RULE) FIELDS ===")
pi_fields = fields_get('product.pricelist.item')
key_fields = ['applied_on', 'compute_price', 'percent_price', 'fixed_price',
              'price_discount', 'price_round', 'price_surcharge', 'min_quantity',
              'date_start', 'date_end', 'product_tmpl_id', 'product_id', 'categ_id',
              'base', 'base_pricelist_id']
for f in key_fields:
    if f in pi_fields:
        info = pi_fields[f]
        sel = info.get('selection', '')
        print(f"  {f}: type={info['type']}, label='{info['string']}'{', selection='+str(sel) if sel else ''}")
    else:
        print(f"  {f}: NOT FOUND in model")

print(f"\n  All pricelist item fields: {sorted(pi_fields.keys())}")

# ═══════════════════════════════════════════
# 5. Check actual pricelists
# ═══════════════════════════════════════════
print(f"\n=== EXISTING PRICELISTS ===")
pricelists = search_read('product.pricelist', [], ['name', 'currency_id', 'company_id', 'active', 'country_group_ids'])
for pl in pricelists:
    print(f"  ID={pl['id']}: '{pl['name']}' | currency={pl['currency_id']} | company={pl['company_id']} | active={pl['active']}")

# ═══════════════════════════════════════════
# 6. Check existing price rules (items)
# ═══════════════════════════════════════════
print(f"\n=== EXISTING PRICE RULES ===")
items = search_read('product.pricelist.item', [], [
    'pricelist_id', 'applied_on', 'compute_price', 'percent_price', 'price_discount',
    'fixed_price', 'min_quantity', 'date_start', 'date_end', 'product_tmpl_id',
    'categ_id', 'price_round', 'price_surcharge', 'base'
])
for item in items:
    print(f"  ID={item['id']}: pricelist={item['pricelist_id']}")
    print(f"    applied_on={item['applied_on']}, compute_price={item['compute_price']}")
    print(f"    percent_price={item.get('percent_price')}, price_discount={item.get('price_discount')}")
    print(f"    fixed_price={item.get('fixed_price')}, min_qty={item['min_quantity']}")
    print(f"    dates={item['date_start']} to {item['date_end']}")
    print(f"    product={item.get('product_tmpl_id')}, categ={item.get('categ_id')}")
    print(f"    base={item.get('base')}, round={item.get('price_round')}, surcharge={item.get('price_surcharge')}")

# ═══════════════════════════════════════════
# 7. Check 'applied_on' and 'compute_price' selection values
# ═══════════════════════════════════════════
print(f"\n=== FIELD SELECTION VALUES ===")
for field_name in ['applied_on', 'compute_price']:
    if field_name in pi_fields:
        sel = pi_fields[field_name].get('selection', [])
        print(f"  {field_name} options: {sel}")

# ═══════════════════════════════════════════
# 8. Check Loyalty / Discount Programs
# ═══════════════════════════════════════════
print(f"\n=== LOYALTY PROGRAMS ===")
try:
    lp_fields = fields_get('loyalty.program')
    print(f"  loyalty.program model exists. Fields: {sorted(lp_fields.keys())}")
    
    # Check program_type selection
    if 'program_type' in lp_fields:
        print(f"  program_type selection: {lp_fields['program_type'].get('selection')}")
    
    programs = search_read('loyalty.program', [], ['name', 'program_type', 'active', 
        'date_from', 'date_to', 'limit_usage', 'available_on', 'pricelist_ids'], limit=20)
    for prog in programs:
        print(f"  ID={prog['id']}: '{prog['name']}' | type={prog.get('program_type')} | active={prog['active']}")
except Exception as e:
    print(f"  loyalty.program error: {e}")

# ═══════════════════════════════════════════
# 9. Check Sale Order fields for discount
# ═══════════════════════════════════════════
print(f"\n=== SALE ORDER LINE DISCOUNT FIELDS ===")
sol_fields = fields_get('sale.order.line')
for f in ['discount', 'price_unit', 'price_subtotal', 'pricelist_item_id']:
    if f in sol_fields:
        info = sol_fields[f]
        print(f"  {f}: type={info['type']}, label='{info['string']}'")
    else:
        print(f"  {f}: NOT FOUND")

# Check sale.order pricelist field
so_fields = fields_get('sale.order')
for f in ['pricelist_id']:
    if f in so_fields:
        info = so_fields[f]
        print(f"  sale.order.{f}: type={info['type']}, label='{info['string']}'")

# ═══════════════════════════════════════════
# 10. Check what "Discount button" is in Odoo 19
# ═══════════════════════════════════════════
print(f"\n=== SALE ORDER DISCOUNT BUTTON CHECK ===")
# Look for sale_loyalty or sale_discount modules
try:
    modules = search_read('ir.module.module', [
        ('name', 'in', ['sale_loyalty', 'sale_discount', 'loyalty', 'sale_coupon'])
    ], ['name', 'state', 'shortdesc'])
    for m in modules:
        print(f"  Module: {m['name']} | state={m['state']} | {m['shortdesc']}")
except:
    pass

# ═══════════════════════════════════════════
# 11. Check if Discount button field exists on SO
# ═══════════════════════════════════════════
print(f"\n=== ALL SALE ORDER FIELDS (discount/loyalty related) ===")
for f_name, f_info in so_fields.items():
    if 'discount' in f_name.lower() or 'loyalty' in f_name.lower() or 'coupon' in f_name.lower() or 'reward' in f_name.lower():
        print(f"  {f_name}: type={f_info['type']}, label='{f_info['string']}'")

# ═══════════════════════════════════════════
# 12. Check Customer form - pricelist field
# ═══════════════════════════════════════════
print(f"\n=== CUSTOMER PRICELIST FIELD ===")
partner_fields = fields_get('res.partner')
for f in ['property_product_pricelist']:
    if f in partner_fields:
        info = partner_fields[f]
        print(f"  {f}: type={info['type']}, label='{info['string']}'")
        if info.get('help'):
            print(f"    help: {info['help']}")
    else:
        print(f"  {f}: NOT FOUND")

# Check where this field appears (tab info not available via XML-RPC)
# But we can check what tab label is used

# ═══════════════════════════════════════════
# 13. Verify blog-specific claims
# ═══════════════════════════════════════════
print(f"\n=== BLOG CLAIM VERIFICATION ===")

# Claim: "applied_on" has values: All Products, Product Category, Product, Product Variant
if 'applied_on' in pi_fields:
    sel = pi_fields['applied_on'].get('selection', [])
    print(f"\n  CLAIM: Apply To options are 'All Products, Product Category, Product, Product Variant'")
    print(f"  ACTUAL: {sel}")
    actual_values = [s[1] for s in sel]
    for expected in ['All Products', 'Product Category', 'Product', 'Product Variant']:
        found = any(expected.lower() in v.lower() for v in actual_values)
        print(f"    '{expected}' -> {'FOUND' if found else 'NOT FOUND'}")

# Claim: compute_price has values: Discount, Formula, Fixed Price
if 'compute_price' in pi_fields:
    sel = pi_fields['compute_price'].get('selection', [])
    print(f"\n  CLAIM: Price Type options are 'Discount, Formula, Fixed Price'")
    print(f"  ACTUAL: {sel}")
    actual_values = [s[1] for s in sel]
    for expected in ['Discount', 'Formula', 'Fixed Price']:
        found = any(expected.lower() in v.lower() for v in actual_values)
        print(f"    '{expected}' -> {'FOUND' if found else 'NOT FOUND'}")

# Claim: pricelist has "Recurring Prices" and "Rental Rules" tabs
print(f"\n  CLAIM: Pricelist form has 'Price Rules', 'Recurring Prices', 'Rental Rules' tabs")
for tab_field in ['item_ids', 'recurring_item_ids', 'rental_item_ids']:
    if tab_field in pl_fields:
        print(f"    {tab_field}: FOUND (label='{pl_fields[tab_field]['string']}')")
    else:
        # Search similar
        matches = [k for k in pl_fields.keys() if 'recurring' in k.lower() or 'rental' in k.lower() or 'subscription' in k.lower()]
        print(f"    {tab_field}: NOT FOUND. Similar: {matches}")

# Check discount_policy field on pricelist
print(f"\n  CLAIM: Pricelists have discount_policy field")
if 'discount_policy' in pl_fields:
    print(f"    discount_policy: FOUND, selection={pl_fields['discount_policy'].get('selection')}")
else:
    print(f"    discount_policy: NOT FOUND")

# ═══════════════════════════════════════════
# 14. Check menu paths
# ═══════════════════════════════════════════
print(f"\n=== MENU PATHS ===")
try:
    menus = search_read('ir.ui.menu', [('name', 'ilike', 'pricelists')], ['name', 'complete_name', 'parent_id'])
    print(f"  Menus containing 'pricelists':")
    for m in menus:
        print(f"    {m.get('complete_name', m['name'])}")
except:
    pass

try:
    menus = search_read('ir.ui.menu', [('name', 'ilike', 'discount')], ['name', 'complete_name', 'parent_id'])
    print(f"\n  Menus containing 'discount':")
    for m in menus:
        print(f"    {m.get('complete_name', m['name'])}")
except:
    pass

try:
    menus = search_read('ir.ui.menu', [('name', 'ilike', 'loyalty')], ['name', 'complete_name', 'parent_id'])
    print(f"\n  Menus containing 'loyalty':")
    for m in menus:
        print(f"    {m.get('complete_name', m['name'])}")
except:
    pass

# ═══════════════════════════════════════════
# 15. Formula fields detailed check
# ═══════════════════════════════════════════
print(f"\n=== FORMULA FIELDS DETAIL ===")
formula_fields = ['price_discount', 'price_round', 'price_surcharge', 'price_min_margin', 'price_max_margin']
for f in formula_fields:
    if f in pi_fields:
        info = pi_fields[f]
        print(f"  {f}: type={info['type']}, label='{info['string']}', help='{info.get('help','')}'")
    else:
        print(f"  {f}: NOT FOUND")

# ═══════════════════════════════════════════
# 16. Check Discount Button - sale.order methods
# ═══════════════════════════════════════════
print(f"\n=== LOYALTY REWARD FIELDS ON SALE ORDER ===")
for f_name, f_info in so_fields.items():
    if 'loyalty' in f_name.lower() or 'reward' in f_name.lower() or 'code' in f_name.lower() or 'promo' in f_name.lower():
        print(f"  {f_name}: type={f_info['type']}, label='{f_info['string']}'")

print("\n=== DONE ===")
