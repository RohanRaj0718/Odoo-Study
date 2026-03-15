"""
Check current state and set up Shop Floor demo data via API.
"""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def x(model, method, *args):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *args)

def sr(model, domain, fields):
    return x(model, 'search_read', [domain], {'fields': fields, 'limit': 50})

# ── 1. CHECK COMPANIES ──
print("=== COMPANIES ===")
companies = sr('res.company', [], ['name'])
for c in companies:
    print(f"  [{c['id']}] {c['name']}")

# ── 2. CHECK CURRENT USER ──  
print("\n=== CURRENT USER ===")
user = sr('res.users', [['id', '=', uid]], ['name', 'company_id', 'company_ids'])
print(f"  User: {user[0]['name']}")
print(f"  Current company: {user[0]['company_id']}")
print(f"  Allowed companies: {user[0]['company_ids']}")

# ── 3. CHECK WORK CENTERS (all companies) ──
print("\n=== WORK CENTERS (all companies) ===")
wcs = sr('mrp.workcenter', [], ['name', 'company_id', 'active', 'code'])
if wcs:
    for wc in wcs:
        print(f"  [{wc['id']}] {wc['name']} | company={wc['company_id']} | active={wc['active']}")
else:
    print("  NONE found")

# Also check inactive
wcs_inactive = sr('mrp.workcenter', [['active', '=', False]], ['name', 'company_id'])
if wcs_inactive:
    print("  Inactive work centers:")
    for wc in wcs_inactive:
        print(f"    [{wc['id']}] {wc['name']} | company={wc['company_id']}")

# ── 4. CHECK BOMs ──
print("\n=== BILL OF MATERIALS ===")
boms = sr('mrp.bom', [], ['display_name', 'product_tmpl_id', 'company_id', 'operation_ids', 'bom_line_ids', 'type'])
for bom in boms:
    print(f"  [{bom['id']}] {bom['display_name']}")
    print(f"    Product: {bom['product_tmpl_id']}")
    print(f"    Company: {bom['company_id']}")
    print(f"    Type: {bom['type']}")
    print(f"    Operations: {bom['operation_ids']}")
    print(f"    Lines: {bom['bom_line_ids']}")

# ── 5. CHECK OPERATIONS (mrp.routing.workcenter) ──
print("\n=== ROUTING OPERATIONS ===")
ops = sr('mrp.routing.workcenter', [], ['name', 'bom_id', 'workcenter_id', 'company_id', 'sequence'])
if ops:
    for op in ops:
        print(f"  [{op['id']}] {op['name']} | WC={op['workcenter_id']} | BoM={op['bom_id']}")
else:
    print("  NONE found")

# ── 6. CHECK MOs ──
print("\n=== MANUFACTURING ORDERS ===")
mos = sr('mrp.production', [], ['name', 'state', 'company_id', 'product_id', 'workorder_ids'])
if mos:
    for mo in mos:
        print(f"  [{mo['id']}] {mo['name']} | state={mo['state']} | company={mo['company_id']}")
        print(f"    Product: {mo['product_id']}")
        print(f"    Work Orders: {mo['workorder_ids']}")
else:
    print("  NONE found")

# ── 7. CHECK INSTALLED MODULES ──
print("\n=== KEY MODULES ===")
mods = sr('ir.module.module', [['name', 'in', ['mrp', 'mrp_workorder', 'quality_control', 'mrp_shop_floor']]], 
          ['name', 'state'])
for m in mods:
    print(f"  {m['name']}: {m['state']}")

# ── 8. CHECK SETTINGS ──
print("\n=== MRP SETTINGS ===")
try:
    # Check config settings
    config = sr('res.config.settings', [], ['group_mrp_routings', 'module_mrp_workorder', 'module_quality_control'])
    if config:
        c = config[-1]  # latest
        print(f"  group_mrp_routings: {c.get('group_mrp_routings')}")
        print(f"  module_mrp_workorder: {c.get('module_mrp_workorder')}")
        print(f"  module_quality_control: {c.get('module_quality_control')}")
except Exception as e:
    print(f"  Error reading settings: {e}")

# Check if group_mrp_routings is enabled
try:
    group = sr('ir.model.data', [['module', '=', 'mrp'], ['name', '=', 'group_mrp_routings']], ['res_id'])
    if group:
        gid = group[0]['res_id']
        grp = sr('res.groups', [['id', '=', gid]], ['name', 'users'])
        print(f"\n  group_mrp_routings (id={gid}):")
        print(f"    Users with access: {len(grp[0]['users'])} users")
        # Check if our user has it
        has_access = uid in grp[0]['users']
        print(f"    Current user has access: {has_access}")
except Exception as e:
    print(f"  Error checking group: {e}")

print("\n=== DONE ===")
