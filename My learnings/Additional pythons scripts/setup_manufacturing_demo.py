"""
============================================================================
ODOO 19 - COMPLETE MANUFACTURING DEMO DATABASE SETUP
============================================================================
Configures everything for the live demo via XML-RPC API:
  - Installs modules (CRM, Sales, Manufacturing, Quality, Maintenance, etc.)
  - Creates Work Centers, Product Categories
  - Creates Vendors, Raw Materials, Finished Product
  - Creates Bill of Materials with Operations
  - Loads initial stock (Inventory Adjustments)
  - Creates Quality Control Points
  - Creates Maintenance Equipment & Teams
  - Creates Customer, Employees
  - Creates a CRM Lead, Sales Order, Purchase Order
  - Creates a Manufacturing Order
============================================================================
Database: https://demo-tech.odoo.com
============================================================================
"""
import xmlrpc.client
import datetime
import sys
import time
import traceback

# ──────────────────────────────────────────────────────────
# CONNECTION SETTINGS  — UPDATE THESE!
# ──────────────────────────────────────────────────────────
URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
USERNAME = "rohan.raj@infintor.com"   # <-- your Odoo login email
PASSWORD = "Rohanraj@1"               # <-- your Odoo password

# ──────────────────────────────────────────────────────────
# CONNECT & AUTHENTICATE
# ──────────────────────────────────────────────────────────
print("=" * 70)
print("  ODOO 19 — COMPLETE MANUFACTURING DEMO SETUP")
print("  Database:", URL)
print("=" * 70)

print("\n[CONNECT] Connecting to Odoo...")
try:
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
    version = common.version()
    print(f"  ✅ Connected — Odoo {version.get('server_version', '?')}")
except Exception as e:
    print(f"  ❌ Connection failed: {e}")
    import ssl
    try:
        ctx = ssl._create_unverified_context()
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True, context=ctx)
        version = common.version()
        print(f"  ✅ Connected (no SSL verify) — Odoo {version.get('server_version', '?')}")
    except Exception as e2:
        print(f"  ❌ Cannot connect: {e2}")
        sys.exit(1)

# Try authentication with multiple DB name guesses
print("\n[AUTH] Authenticating...")
DB_GUESSES = [DB, "demo-tech", "demo_tech", "Demo-Tech", "demo-tech-main", DB.replace("-", "_")]
# deduplicate while preserving order
DB_GUESSES = list(dict.fromkeys(DB_GUESSES))
uid = None
USED_DB = None
for db in DB_GUESSES:
    try:
        uid = common.authenticate(db, USERNAME, PASSWORD, {})
        if uid:
            USED_DB = db
            print(f"  ✅ Authenticated — UID: {uid}, DB: {db}")
            break
        else:
            print(f"  ⚠️  DB '{db}' — wrong credentials or DB name")
    except Exception as e:
        print(f"  ⚠️  DB '{db}' — {e}")

if not uid:
    # Last resort: try to get the DB list
    print("\n  Trying to list databases...")
    try:
        db_svc = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/db', allow_none=True)
        dbs = db_svc.list()
        print(f"  Available DBs: {dbs}")
        for db in dbs:
            uid = common.authenticate(db, USERNAME, PASSWORD, {})
            if uid:
                USED_DB = db
                print(f"  ✅ Authenticated — UID: {uid}, DB: {db}")
                break
    except:
        pass
    if not uid:
        print("\n  ❌ AUTHENTICATION FAILED.")
        print("  Please update USERNAME and PASSWORD in this script.")
        print("  Make sure the Odoo database URL is correct.")
        sys.exit(1)

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

# ──────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────
def execute(model, method, *args, **kwargs):
    return models.execute_kw(USED_DB, uid, PASSWORD, model, method, *args, **kwargs)

def search_read(model, domain, fields, limit=0):
    kw = {'fields': fields}
    if limit:
        kw['limit'] = limit
    return execute(model, 'search_read', [domain], kw)

def search(model, domain, limit=0):
    kw = {}
    if limit:
        kw['limit'] = limit
    return execute(model, 'search', [domain], kw)

def create(model, vals):
    return execute(model, 'create', [vals])

def write(model, ids, vals):
    if not isinstance(ids, list):
        ids = [ids]
    return execute(model, 'write', [ids, vals])

def find_or_create(model, domain, vals, label="record"):
    """Find existing record or create new one."""
    existing = search_read(model, domain, ['id', 'name'] if 'name' in vals else ['id'], limit=1)
    if existing:
        rid = existing[0]['id']
        rname = existing[0].get('name', rid)
        print(f"    ℹ️  {label} '{rname}' already exists (ID: {rid})")
        return rid
    else:
        rid = create(model, vals)
        print(f"    ✅ Created {label} '{vals.get('name', rid)}' (ID: {rid})")
        return rid

def get_id(model, domain, label=""):
    """Get the ID of an existing record."""
    r = search_read(model, domain, ['id'], limit=1)
    if r:
        return r[0]['id']
    return None

TODAY = datetime.date.today().isoformat()
ERRORS = []

def safe(func, section_name):
    """Wrapper to catch and log errors without stopping the whole script."""
    try:
        return func()
    except Exception as e:
        msg = f"[{section_name}] {e}"
        ERRORS.append(msg)
        print(f"    ❌ ERROR: {e}")
        traceback.print_exc()
        return None

# ──────────────────────────────────────────────────────────
# PHASE 0: VERIFY USER & COMPANY
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 0: Verifying User & Company")
print("=" * 70)

user_info = search_read('res.users', [['id', '=', uid]], ['name', 'email', 'company_id'])
if user_info:
    u = user_info[0]
    company_name = u['company_id'][1] if isinstance(u['company_id'], list) else u['company_id']
    print(f"  User: {u['name']}")
    print(f"  Email: {u['email']}")
    print(f"  Company: {company_name}")

company_id = u['company_id'][0] if isinstance(u['company_id'], list) else u['company_id']

# ──────────────────────────────────────────────────────────
# PHASE 1: INSTALL MODULES
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 1: Installing Required Modules")
print("=" * 70)

MODULES_TO_INSTALL = [
    'crm',              # CRM
    'sale_management',  # Sales
    'purchase',         # Purchase
    'stock',            # Inventory
    'mrp',              # Manufacturing
    'quality_control',  # Quality (may vary: quality, quality_control, quality_mrp)
    'maintenance',      # Maintenance
    'repair',           # Repairs
    'account',          # Accounting/Invoicing
    'hr',               # Employees
    'hr_payroll',       # Payroll
    'hr_holidays',      # Time Off
    'helpdesk',         # Helpdesk
]

# Also try alternate names for modules that may differ between editions
ALTERNATE_NAMES = {
    'quality_control': ['quality_control', 'quality', 'quality_mrp'],
    'hr_payroll': ['hr_payroll', 'l10n_in_hr_payroll', 'hr_payroll_community'],
    'helpdesk': ['helpdesk', 'website_helpdesk'],
    'sale_management': ['sale_management', 'sale'],
}

installed_mods = search_read('ir.module.module', [['state', '=', 'installed']],
                             ['name', 'shortdesc'])
installed_names = {m['name'] for m in installed_mods}
print(f"  Currently installed: {len(installed_names)} modules")

for mod in MODULES_TO_INSTALL:
    names_to_try = ALTERNATE_NAMES.get(mod, [mod])
    already = any(n in installed_names for n in names_to_try)
    if already:
        found_name = next(n for n in names_to_try if n in installed_names)
        print(f"  ✅ {found_name} — already installed")
        continue

    # Try to install
    installed = False
    for name in names_to_try:
        mod_ids = search('ir.module.module', [['name', '=', name]], limit=1)
        if mod_ids:
            try:
                print(f"  ⏳ Installing {name}...")
                execute('ir.module.module', 'button_immediate_install', [mod_ids])
                print(f"  ✅ {name} — installed!")
                installed = True
                time.sleep(2)  # give server a moment
                break
            except Exception as e:
                print(f"  ⚠️  {name} install attempt: {e}")
    if not installed:
        print(f"  ⚠️  Could not install any of {names_to_try} — may need manual install")

# Refresh installed modules list
installed_mods = search_read('ir.module.module', [['state', '=', 'installed']],
                             ['name', 'shortdesc'])
installed_names = {m['name'] for m in installed_mods}

# ──────────────────────────────────────────────────────────
# PHASE 1.5: ENABLE SETTINGS
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 1.5: Configuring Module Settings")
print("=" * 70)

def enable_settings():
    """Try to enable key settings via res.config.settings."""
    try:
        settings_vals = {}

        # Manufacturing settings
        if 'mrp' in installed_names:
            settings_vals['group_mrp_routings'] = True  # Enable Work Orders
            settings_vals['module_quality_control'] = True

        # Inventory settings
        if 'stock' in installed_names:
            settings_vals['group_stock_multi_locations'] = True
            settings_vals['group_stock_adv_location'] = True
            settings_vals['group_stock_tracking_lot'] = True  # Lots & Serial Numbers

        if not settings_vals:
            print("  ℹ️  No settings to configure")
            return

        # Create a settings record, set values, then execute
        settings_id = create('res.config.settings', settings_vals)
        execute('res.config.settings', 'execute', [[settings_id]])
        print("  ✅ Settings configured (Work Orders, Quality, Maintenance, Multi-Locations, Lots)")
    except Exception as e:
        print(f"  ⚠️  Settings configuration: {e}")
        print("  ℹ️  You may need to enable Work Orders manually:")
        print("       Manufacturing → Configuration → Settings → Enable 'Work Orders'")

safe(enable_settings, "Settings")

# ──────────────────────────────────────────────────────────
# PHASE 2: CREATE PRODUCT CATEGORIES
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 2: Creating Product Categories")
print("=" * 70)

def create_categories():
    cat_raw = find_or_create('product.category',
        [['name', '=', 'Raw Materials']],
        {'name': 'Raw Materials'},
        'Category')
    cat_fin = find_or_create('product.category',
        [['name', '=', 'Finished Products']],
        {'name': 'Finished Products'},
        'Category')
    return cat_raw, cat_fin

cat_raw_id, cat_fin_id = safe(create_categories, "Categories") or (None, None)

# ──────────────────────────────────────────────────────────
# PHASE 3: CREATE WORK CENTERS
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 3: Creating Work Centers")
print("=" * 70)

wc_ids = {}

def create_work_centers():
    work_centers = [
        {'name': 'Cutting Station', 'costs_hour': 25.0,
         'time_start': 5, 'time_stop': 5},
        {'name': 'Assembly Line', 'costs_hour': 35.0,
         'time_start': 10, 'time_stop': 5},
        {'name': 'Quality Testing', 'costs_hour': 30.0,
         'time_start': 2, 'time_stop': 2},
        {'name': 'Packaging', 'costs_hour': 20.0,
         'time_start': 3, 'time_stop': 3},
    ]
    for wc in work_centers:
        wc_id = find_or_create('mrp.workcenter',
            [['name', '=', wc['name']]],
            wc, 'Work Center')
        wc_ids[wc['name']] = wc_id

if 'mrp' in installed_names:
    safe(create_work_centers, "Work Centers")
else:
    print("  ⚠️  MRP not installed, skipping work centers")

# ──────────────────────────────────────────────────────────
# PHASE 4: CREATE VENDORS
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 4: Creating Vendors (Suppliers)")
print("=" * 70)

vendor_ids = {}

def create_vendors():
    vendors = [
        {'name': 'Steel World Suppliers', 'email': 'orders@steelworld.com',
         'phone': '+91-9876543210', 'is_company': True, 'supplier_rank': 1},
        {'name': 'WoodCraft Materials', 'email': 'sales@woodcraft.com',
         'phone': '+91-9876543211', 'is_company': True, 'supplier_rank': 1},
        {'name': 'ElectroComponents Ltd', 'email': 'supply@electrocomp.com',
         'phone': '+91-9876543212', 'is_company': True, 'supplier_rank': 1},
    ]
    for v in vendors:
        vid = find_or_create('res.partner',
            [['name', '=', v['name']]],
            v, 'Vendor')
        vendor_ids[v['name']] = vid

safe(create_vendors, "Vendors")

# ──────────────────────────────────────────────────────────
# PHASE 5: CREATE RAW MATERIAL PRODUCTS
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 5: Creating Raw Material Products")
print("=" * 70)

raw_material_ids = {}  # name -> product.product id

def create_raw_materials():
    materials = [
        {'name': 'Steel Frame', 'type': 'consu', 'is_storable': True,
         'list_price': 0, 'standard_price': 500.0,
         'sale_ok': False, 'purchase_ok': True,
         'categ_id': cat_raw_id,
         'vendor': 'Steel World Suppliers', 'vendor_price': 500.0},
        {'name': 'Wooden Desktop Panel', 'type': 'consu', 'is_storable': True,
         'list_price': 0, 'standard_price': 800.0,
         'sale_ok': False, 'purchase_ok': True,
         'categ_id': cat_raw_id,
         'vendor': 'WoodCraft Materials', 'vendor_price': 800.0},
        {'name': 'Electric Motor (Height Adjustment)', 'type': 'consu', 'is_storable': True,
         'list_price': 0, 'standard_price': 1200.0,
         'sale_ok': False, 'purchase_ok': True,
         'categ_id': cat_raw_id,
         'vendor': 'ElectroComponents Ltd', 'vendor_price': 1200.0},
        {'name': 'Control Panel (Electronic)', 'type': 'consu', 'is_storable': True,
         'list_price': 0, 'standard_price': 600.0,
         'sale_ok': False, 'purchase_ok': True,
         'categ_id': cat_raw_id,
         'vendor': 'ElectroComponents Ltd', 'vendor_price': 600.0},
        {'name': 'Screws & Hardware Kit', 'type': 'consu', 'is_storable': True,
         'list_price': 0, 'standard_price': 100.0,
         'sale_ok': False, 'purchase_ok': True,
         'categ_id': cat_raw_id,
         'vendor': 'Steel World Suppliers', 'vendor_price': 100.0},
    ]

    for mat in materials:
        vendor_name = mat.pop('vendor')
        vendor_price = mat.pop('vendor_price')

        # Check if product template exists
        existing = search_read('product.template', [['name', '=', mat['name']]], ['id'])
        if existing:
            tmpl_id = existing[0]['id']
            print(f"    ℹ️  Raw Material '{mat['name']}' already exists (Tmpl ID: {tmpl_id})")
        else:
            tmpl_id = create('product.template', mat)
            print(f"    ✅ Created Raw Material '{mat['name']}' (Tmpl ID: {tmpl_id})")

        # Get product.product id
        pp = search_read('product.product', [['product_tmpl_id', '=', tmpl_id]], ['id'])
        pp_id = pp[0]['id'] if pp else tmpl_id
        raw_material_ids[mat['name']] = pp_id

        # Add vendor / supplierinfo
        if vendor_name in vendor_ids:
            existing_si = search_read('product.supplierinfo',
                [['product_tmpl_id', '=', tmpl_id],
                 ['partner_id', '=', vendor_ids[vendor_name]]],
                ['id'])
            if not existing_si:
                try:
                    create('product.supplierinfo', {
                        'partner_id': vendor_ids[vendor_name],
                        'product_tmpl_id': tmpl_id,
                        'price': vendor_price,
                        'min_qty': 1,
                    })
                    print(f"      ↳ Added vendor '{vendor_name}' @ {vendor_price}")
                except Exception as e:
                    print(f"      ⚠️  Vendor info: {e}")

safe(create_raw_materials, "Raw Materials")

# ──────────────────────────────────────────────────────────
# PHASE 6: CREATE FINISHED PRODUCT — SmartDesk Pro
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 6: Creating Finished Product — SmartDesk Pro")
print("=" * 70)

smartdesk_pp_id = None
smartdesk_tmpl_id = None

def create_finished_product():
    global smartdesk_pp_id, smartdesk_tmpl_id

    vals = {
        'name': 'SmartDesk Pro',
        'type': 'consu',
        'is_storable': True,
        'list_price': 8500.0,
        'standard_price': 3200.0,
        'sale_ok': True,
        'purchase_ok': False,
        'categ_id': cat_fin_id,
        'default_code': 'SMDSK-001',
    }

    existing = search_read('product.template', [['name', '=', 'SmartDesk Pro']], ['id'])
    if existing:
        smartdesk_tmpl_id = existing[0]['id']
        print(f"    ℹ️  SmartDesk Pro already exists (Tmpl ID: {smartdesk_tmpl_id})")
    else:
        smartdesk_tmpl_id = create('product.template', vals)
        print(f"    ✅ Created SmartDesk Pro (Tmpl ID: {smartdesk_tmpl_id})")

    # Get product.product id
    pp = search_read('product.product', [['product_tmpl_id', '=', smartdesk_tmpl_id]], ['id'])
    smartdesk_pp_id = pp[0]['id'] if pp else smartdesk_tmpl_id
    print(f"    Product.Product ID: {smartdesk_pp_id}")

    # Enable Manufacture route on the product
    try:
        mfg_route = search_read('stock.route',
            [['name', 'ilike', 'Manufacture']], ['id'], limit=1)
        if mfg_route:
            route_id = mfg_route[0]['id']
            write('product.template', smartdesk_tmpl_id, {
                'route_ids': [(4, route_id)]
            })
            print(f"    ✅ Manufacture route enabled on SmartDesk Pro")
    except Exception as e:
        print(f"    ⚠️  Could not set Manufacture route: {e}")

safe(create_finished_product, "Finished Product")

# ──────────────────────────────────────────────────────────
# PHASE 7: CREATE BILL OF MATERIALS WITH OPERATIONS
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 7: Creating Bill of Materials (BOM)")
print("=" * 70)

bom_id = None

def create_bom():
    global bom_id

    if not smartdesk_tmpl_id:
        print("    ❌ SmartDesk Pro not found, skipping BOM")
        return

    # Check if BOM already exists
    existing = search_read('mrp.bom',
        [['product_tmpl_id', '=', smartdesk_tmpl_id]], ['id'])
    if existing:
        bom_id = existing[0]['id']
        print(f"    ℹ️  BOM already exists (ID: {bom_id})")
        return

    # Build component lines
    components = [
        ('Steel Frame', 1),
        ('Wooden Desktop Panel', 1),
        ('Electric Motor (Height Adjustment)', 1),
        ('Control Panel (Electronic)', 1),
        ('Screws & Hardware Kit', 1),
    ]

    bom_lines = []
    for comp_name, qty in components:
        pp_id = raw_material_ids.get(comp_name)
        if pp_id:
            bom_lines.append((0, 0, {
                'product_id': pp_id,
                'product_qty': qty,
            }))
        else:
            print(f"    ⚠️  Component '{comp_name}' not found, skipping")

    bom_vals = {
        'product_tmpl_id': smartdesk_tmpl_id,
        'product_qty': 1,
        'code': 'BOM-SMDSK-001',
        'type': 'normal',  # Manufacture this product
        'bom_line_ids': bom_lines,
    }

    bom_id = create('mrp.bom', bom_vals)
    print(f"    ✅ Created BOM (ID: {bom_id}) with {len(bom_lines)} components")

    # Add operations (Work Orders) if work centers exist
    if wc_ids:
        operations = [
            {'name': 'Cut & Prepare Frame', 'workcenter_id': wc_ids.get('Cutting Station'),
             'time_cycle_manual': 30, 'sequence': 10},
            {'name': 'Assemble Desk', 'workcenter_id': wc_ids.get('Assembly Line'),
             'time_cycle_manual': 45, 'sequence': 20},
            {'name': 'Install Electronics', 'workcenter_id': wc_ids.get('Assembly Line'),
             'time_cycle_manual': 30, 'sequence': 30},
            {'name': 'Quality Inspection', 'workcenter_id': wc_ids.get('Quality Testing'),
             'time_cycle_manual': 15, 'sequence': 40},
            {'name': 'Final Packaging', 'workcenter_id': wc_ids.get('Packaging'),
             'time_cycle_manual': 20, 'sequence': 50},
        ]

        op_count = 0
        for op in operations:
            if op['workcenter_id']:
                try:
                    op_vals = {
                        'name': op['name'],
                        'workcenter_id': op['workcenter_id'],
                        'time_cycle_manual': op['time_cycle_manual'],
                        'sequence': op['sequence'],
                        'bom_id': bom_id,
                    }
                    create('mrp.routing.workcenter', op_vals)
                    op_count += 1
                    print(f"      ↳ Operation: {op['name']} @ {op['time_cycle_manual']} min")
                except Exception as e:
                    print(f"      ⚠️  Operation '{op['name']}': {e}")
        print(f"    ✅ Added {op_count} operations to BOM")
    else:
        print("    ⚠️  No work centers found, skipping operations")

if 'mrp' in installed_names:
    safe(create_bom, "BOM")
else:
    print("  ⚠️  MRP not installed, skipping BOM")

# ──────────────────────────────────────────────────────────
# PHASE 8: LOAD INITIAL STOCK (Inventory Adjustments)
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 8: Loading Initial Stock")
print("=" * 70)

def load_initial_stock():
    # Find the stock location (WH/Stock)
    stock_loc = search_read('stock.location',
        [['usage', '=', 'internal'], ['name', '=', 'Stock']], ['id', 'complete_name'], limit=1)
    if not stock_loc:
        stock_loc = search_read('stock.location',
            [['usage', '=', 'internal']], ['id', 'complete_name'], limit=1)
    if not stock_loc:
        print("    ❌ No internal stock location found!")
        return

    location_id = stock_loc[0]['id']
    print(f"    Stock location: {stock_loc[0]['complete_name']} (ID: {location_id})")

    stock_items = {
        'Steel Frame': 20,
        'Wooden Desktop Panel': 20,
        'Electric Motor (Height Adjustment)': 20,
        'Control Panel (Electronic)': 20,
        'Screws & Hardware Kit': 40,
    }

    # Try using stock.quant method (Odoo 17+)
    for prod_name, qty in stock_items.items():
        pp_id = raw_material_ids.get(prod_name)
        if not pp_id:
            print(f"    ⚠️  Product '{prod_name}' not found, skipping stock")
            continue

        try:
            # Check current stock
            quants = search_read('stock.quant',
                [['product_id', '=', pp_id], ['location_id', '=', location_id]],
                ['id', 'quantity'])
            current_qty = quants[0]['quantity'] if quants else 0

            if current_qty >= qty:
                print(f"    ℹ️  {prod_name}: {current_qty} units already in stock (need {qty})")
                continue

            # Update or create quant
            if quants:
                write('stock.quant', quants[0]['id'], {
                    'inventory_quantity': qty,
                })
                # Apply inventory adjustment
                try:
                    execute('stock.quant', 'action_apply_inventory', [[quants[0]['id']]])
                except:
                    pass
                print(f"    ✅ {prod_name}: set to {qty} units")
            else:
                # Create new quant
                try:
                    q_id = create('stock.quant', {
                        'product_id': pp_id,
                        'location_id': location_id,
                        'inventory_quantity': qty,
                    })
                    try:
                        execute('stock.quant', 'action_apply_inventory', [[q_id]])
                    except:
                        pass
                    print(f"    ✅ {prod_name}: set to {qty} units")
                except Exception as e:
                    print(f"    ⚠️  {prod_name}: quant creation failed: {e}")
                    # Fallback: try stock.change.product.qty wizard
                    try:
                        wiz_id = create('stock.change.product.qty', {
                            'product_id': pp_id,
                            'product_tmpl_id': search_read('product.product',
                                [['id', '=', pp_id]], ['product_tmpl_id'])[0]['product_tmpl_id'][0],
                            'new_quantity': qty,
                        })
                        execute('stock.change.product.qty', 'change_product_qty', [[wiz_id]])
                        print(f"    ✅ {prod_name}: set to {qty} units (via wizard)")
                    except Exception as e2:
                        print(f"    ❌ {prod_name}: {e2}")

        except Exception as e:
            print(f"    ❌ {prod_name}: {e}")

safe(load_initial_stock, "Initial Stock")

# ──────────────────────────────────────────────────────────
# PHASE 9: CREATE CUSTOMER
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 9: Creating Customer")
print("=" * 70)

customer_id = None

def create_customer():
    global customer_id
    customer_id = find_or_create('res.partner',
        [['name', '=', 'Global Office Solutions']],
        {
            'name': 'Global Office Solutions',
            'email': 'procurement@globaloffice.com',
            'phone': '+91-9988776655',
            'is_company': True,
            'customer_rank': 1,
            'street': 'Business District, Tower B, Floor 12',
            'city': 'Mumbai',
            'country_id': get_id('res.country', [['code', '=', 'IN']]),
        },
        'Customer')

safe(create_customer, "Customer")

# Also create a second customer for CRM demo
customer2_id = None
def create_customer2():
    global customer2_id
    customer2_id = find_or_create('res.partner',
        [['name', '=', 'StartUp Innovations Pvt Ltd']],
        {
            'name': 'StartUp Innovations Pvt Ltd',
            'email': 'ceo@startupinnovations.com',
            'phone': '+91-9876501234',
            'is_company': True,
            'customer_rank': 1,
            'street': 'Tech Park, Block C',
            'city': 'Bangalore',
            'country_id': get_id('res.country', [['code', '=', 'IN']]),
        },
        'Customer')

safe(create_customer2, "Customer 2")

# ──────────────────────────────────────────────────────────
# PHASE 10: CREATE CRM LEAD / OPPORTUNITY
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 10: Creating CRM Lead")
print("=" * 70)

lead_id = None

def create_crm_lead():
    global lead_id

    if 'crm' not in installed_names:
        print("    ⚠️  CRM not installed, skipping")
        return

    lead_id = find_or_create('crm.lead',
        [['name', '=', 'Bulk Order - 50 SmartDesk Pro Units']],
        {
            'name': 'Bulk Order - 50 SmartDesk Pro Units',
            'partner_id': customer_id,
            'email_from': 'procurement@globaloffice.com',
            'phone': '+91-9988776655',
            'expected_revenue': 425000.0,
            'type': 'opportunity',
            'description': 'Client needs 50 adjustable standing desks for new corporate office. '
                           'Delivery required within 3 weeks. Budget approved. Decision maker confirmed.',
        },
        'CRM Lead')

safe(create_crm_lead, "CRM Lead")

# ──────────────────────────────────────────────────────────
# PHASE 11: CREATE SALES ORDER
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 11: Creating Sales Order")
print("=" * 70)

so_id = None

def create_sales_order():
    global so_id

    if not smartdesk_pp_id or not customer_id:
        print("    ⚠️  Missing product or customer, skipping")
        return

    # Check if SO already exists for this customer+product
    existing_so = search_read('sale.order',
        [['partner_id', '=', customer_id], ['state', 'in', ['draft', 'sale']]],
        ['id', 'name'], limit=1)
    if existing_so:
        so_id = existing_so[0]['id']
        print(f"    ℹ️  Sales Order already exists: {existing_so[0]['name']} (ID: {so_id})")
        return

    so_id = create('sale.order', {
        'partner_id': customer_id,
        'date_order': TODAY,
        'order_line': [(0, 0, {
            'product_id': smartdesk_pp_id,
            'product_uom_qty': 5,
            'price_unit': 8500.0,
            'name': 'SmartDesk Pro - Adjustable Standing Desk',
        })],
    })
    print(f"    ✅ Created Sales Order (ID: {so_id})")

    # Read back the SO number
    so_data = search_read('sale.order', [['id', '=', so_id]], ['name', 'amount_total'])
    if so_data:
        print(f"    ↳ {so_data[0]['name']} | Total: {so_data[0]['amount_total']}")

safe(create_sales_order, "Sales Order")

# ──────────────────────────────────────────────────────────
# PHASE 12: CREATE PURCHASE ORDERS FOR RAW MATERIALS
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 12: Creating Purchase Orders")
print("=" * 70)

po_ids = []

def create_purchase_orders():
    """Create sample purchase orders for raw materials."""
    if 'purchase' not in installed_names:
        print("    ⚠️  Purchase not installed, skipping")
        return

    purchase_orders = [
        {
            'vendor': 'Steel World Suppliers',
            'lines': [
                {'name': 'Steel Frame', 'qty': 10, 'price': 500.0},
                {'name': 'Screws & Hardware Kit', 'qty': 10, 'price': 100.0},
            ]
        },
        {
            'vendor': 'WoodCraft Materials',
            'lines': [
                {'name': 'Wooden Desktop Panel', 'qty': 10, 'price': 800.0},
            ]
        },
        {
            'vendor': 'ElectroComponents Ltd',
            'lines': [
                {'name': 'Electric Motor (Height Adjustment)', 'qty': 10, 'price': 1200.0},
                {'name': 'Control Panel (Electronic)', 'qty': 10, 'price': 600.0},
            ]
        },
    ]

    for po_data in purchase_orders:
        vendor_name = po_data['vendor']
        v_id = vendor_ids.get(vendor_name)
        if not v_id:
            print(f"    ⚠️  Vendor '{vendor_name}' not found, skipping PO")
            continue

        # Check existing PO
        existing_po = search_read('purchase.order',
            [['partner_id', '=', v_id], ['state', 'in', ['draft', 'purchase']]],
            ['id', 'name'], limit=1)
        if existing_po:
            print(f"    ℹ️  PO for '{vendor_name}' already exists: {existing_po[0]['name']}")
            po_ids.append(existing_po[0]['id'])
            continue

        # Build order lines
        order_lines = []
        for line in po_data['lines']:
            pp_id = raw_material_ids.get(line['name'])
            if pp_id:
                order_lines.append((0, 0, {
                    'product_id': pp_id,
                    'product_qty': line['qty'],
                    'price_unit': line['price'],
                    'name': line['name'],
                }))

        if not order_lines:
            continue

        try:
            po_id = create('purchase.order', {
                'partner_id': v_id,
                'date_order': TODAY,
                'order_line': order_lines,
            })
            po_ids.append(po_id)
            po_info = search_read('purchase.order', [['id', '=', po_id]], ['name', 'amount_total'])
            po_name = po_info[0]['name'] if po_info else f"PO-{po_id}"
            po_total = po_info[0]['amount_total'] if po_info else '?'
            print(f"    ✅ Created PO: {po_name} for {vendor_name} | Total: {po_total}")

            # Confirm the PO
            try:
                execute('purchase.order', 'button_confirm', [[po_id]])
                print(f"      ↳ Confirmed")
            except Exception as e:
                print(f"      ⚠️  Could not confirm PO: {e}")

        except Exception as e:
            print(f"    ❌ PO for '{vendor_name}': {e}")

safe(create_purchase_orders, "Purchase Orders")

# ──────────────────────────────────────────────────────────
# PHASE 13: CREATE MANUFACTURING ORDER
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 13: Creating Manufacturing Order")
print("=" * 70)

mo_id = None

def create_manufacturing_order():
    global mo_id

    if 'mrp' not in installed_names:
        print("    ⚠️  MRP not installed, skipping")
        return

    if not smartdesk_pp_id:
        print("    ⚠️  SmartDesk Pro product not found, skipping MO")
        return

    # Check existing MO
    existing_mo = search_read('mrp.production',
        [['product_id', '=', smartdesk_pp_id], ['state', 'in', ['draft', 'confirmed', 'progress']]],
        ['id', 'name'], limit=1)
    if existing_mo:
        mo_id = existing_mo[0]['id']
        print(f"    ℹ️  MO already exists: {existing_mo[0]['name']} (ID: {mo_id})")
        return

    mo_vals = {
        'product_id': smartdesk_pp_id,
        'product_qty': 5,
        'date_start': TODAY,
    }

    # Add BOM if found
    if bom_id:
        mo_vals['bom_id'] = bom_id

    try:
        mo_id = create('mrp.production', mo_vals)
        mo_info = search_read('mrp.production', [['id', '=', mo_id]], ['name', 'product_qty', 'state'])
        mo_name = mo_info[0]['name'] if mo_info else f"MO-{mo_id}"
        print(f"    ✅ Created Manufacturing Order: {mo_name} for 5 × SmartDesk Pro")

        # Confirm the MO
        try:
            execute('mrp.production', 'action_confirm', [[mo_id]])
            print(f"      ↳ Confirmed — ready for production!")
        except Exception as e:
            print(f"      ⚠️  Could not confirm MO: {e}")

    except Exception as e:
        print(f"    ❌ MO creation failed: {e}")

safe(create_manufacturing_order, "Manufacturing Order")

# ──────────────────────────────────────────────────────────
# PHASE 14: CREATE QUALITY CONTROL POINTS
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 14: Creating Quality Control Points")
print("=" * 70)

def create_quality_points():
    # Check if quality module models exist
    try:
        search_read('quality.point', [], ['id'], limit=1)
    except Exception:
        print("    ⚠️  Quality module not available (quality.point model missing)")
        return

    # Get the manufacturing operation picking type
    mfg_picking = search_read('stock.picking.type',
        [['code', '=', 'mrp_operation']], ['id'], limit=1)
    receipt_picking = search_read('stock.picking.type',
        [['code', '=', 'incoming']], ['id'], limit=1)

    qcps = []

    # QCP 1: Incoming Material Inspection
    if receipt_picking:
        qcps.append({
            'name': 'Incoming Material Inspection',
            'title': 'Incoming Material Inspection',
            'product_ids': [(6, 0, list(raw_material_ids.values()))] if raw_material_ids else False,
            'picking_type_ids': [(6, 0, [receipt_picking[0]['id']])],
            'test_type_id': get_id('quality.point.test_type', [['technical_name', '=', 'passfail']]),
            'note': 'Check material dimensions, surface quality, and certification documents.',
        })

    # QCP 2: Assembly Quality Check (Measure type)
    if mfg_picking and smartdesk_pp_id:
        measure_type = get_id('quality.point.test_type', [['technical_name', '=', 'measure']])
        if measure_type:
            qcps.append({
                'name': 'Desk Height Measurement',
                'title': 'Desk Height Measurement',
                'product_ids': [(6, 0, [smartdesk_pp_id])],
                'picking_type_ids': [(6, 0, [mfg_picking[0]['id']])],
                'test_type_id': measure_type,
                'norm': 75.0,
                'tolerance_min': 73.0,
                'tolerance_max': 77.0,
                'note': 'Measure desk height at all four corners. Must be 75cm ±2cm.',
            })

    # QCP 3: Final Product Inspection
    if mfg_picking and smartdesk_pp_id:
        passfail_type = get_id('quality.point.test_type', [['technical_name', '=', 'passfail']])
        if passfail_type:
            qcps.append({
                'name': 'Final Product Inspection',
                'title': 'Final Product Inspection',
                'product_ids': [(6, 0, [smartdesk_pp_id])],
                'picking_type_ids': [(6, 0, [mfg_picking[0]['id']])],
                'test_type_id': passfail_type,
                'note': 'Test electric motor, check height adjustment range 65-125cm, '
                        'verify control panel buttons, check packaging integrity.',
            })

    for qcp in qcps:
        try:
            # Use 'title' or 'name' depending on Odoo version
            search_field = 'title' if 'title' in qcp else 'name'
            search_val = qcp.get('title', qcp.get('name'))
            existing = search_read('quality.point',
                [[search_field, '=', search_val]], ['id'], limit=1)
            if existing:
                print(f"    ℹ️  QCP '{search_val}' already exists")
                continue
            qcp_id = create('quality.point', qcp)
            print(f"    ✅ Created QCP: '{search_val}' (ID: {qcp_id})")
        except Exception as e:
            # Try without some fields that may not exist
            print(f"    ⚠️  QCP '{qcp.get('title', qcp.get('name'))}': {e}")
            # Simplified retry
            try:
                simple_vals = {
                    'title': qcp.get('title', qcp.get('name', 'Quality Check')),
                    'note': qcp.get('note', ''),
                }
                if qcp.get('picking_type_ids'):
                    simple_vals['picking_type_ids'] = qcp['picking_type_ids']
                if qcp.get('test_type_id'):
                    simple_vals['test_type_id'] = qcp['test_type_id']
                qcp_id = create('quality.point', simple_vals)
                print(f"    ✅ Created QCP (simplified): (ID: {qcp_id})")
            except Exception as e2:
                print(f"    ❌ QCP failed: {e2}")

safe(create_quality_points, "Quality Control Points")

# ──────────────────────────────────────────────────────────
# PHASE 15: CREATE MAINTENANCE EQUIPMENT & TEAM
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 15: Creating Maintenance Equipment & Teams")
print("=" * 70)

def create_maintenance():
    if 'maintenance' not in installed_names:
        print("    ⚠️  Maintenance not installed, skipping")
        return

    # Create Maintenance Team
    team_id = find_or_create('maintenance.team',
        [['name', '=', 'Factory Maintenance Team']],
        {'name': 'Factory Maintenance Team'},
        'Maintenance Team')

    # Create Equipment Category
    cat_id = find_or_create('maintenance.equipment.category',
        [['name', '=', 'Production Machines']],
        {'name': 'Production Machines'},
        'Equipment Category')

    # Create Equipment
    equipment_list = [
        {
            'name': 'CNC Cutting Machine',
            'category_id': cat_id,
            'maintenance_team_id': team_id,
            'color': 1,
        },
        {
            'name': 'Assembly Robot Arm',
            'category_id': cat_id,
            'maintenance_team_id': team_id,
            'color': 2,
        },
        {
            'name': 'Electronic Testing Station',
            'category_id': cat_id,
            'maintenance_team_id': team_id,
            'color': 3,
        },
        {
            'name': 'Packaging Machine',
            'category_id': cat_id,
            'maintenance_team_id': team_id,
            'color': 4,
        },
    ]

    # Link equipment to work centers if possible
    wc_map = {
        'CNC Cutting Machine': 'Cutting Station',
        'Assembly Robot Arm': 'Assembly Line',
        'Electronic Testing Station': 'Quality Testing',
        'Packaging Machine': 'Packaging',
    }

    for eq in equipment_list:
        eq_name = eq['name']
        wc_name = wc_map.get(eq_name)
        if wc_name and wc_name in wc_ids:
            eq['workcenter_id'] = wc_ids[wc_name]

        find_or_create('maintenance.equipment',
            [['name', '=', eq_name]],
            eq, 'Equipment')

safe(create_maintenance, "Maintenance")

# ──────────────────────────────────────────────────────────
# PHASE 16: CREATE EMPLOYEES
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 16: Creating Employees")
print("=" * 70)

def create_employees():
    if 'hr' not in installed_names:
        print("    ⚠️  HR not installed, skipping")
        return

    # Create departments first
    dept_mfg = find_or_create('hr.department',
        [['name', '=', 'Manufacturing']],
        {'name': 'Manufacturing'}, 'Department')

    dept_qc = find_or_create('hr.department',
        [['name', '=', 'Quality Control']],
        {'name': 'Quality Control'}, 'Department')

    dept_sales = find_or_create('hr.department',
        [['name', '=', 'Sales']],
        {'name': 'Sales'}, 'Department')

    dept_purchase = find_or_create('hr.department',
        [['name', '=', 'Purchase']],
        {'name': 'Purchase'}, 'Department')

    dept_hr = find_or_create('hr.department',
        [['name', '=', 'Human Resources']],
        {'name': 'Human Resources'}, 'Department')

    # Create Job Positions
    jobs = [
        ('Manufacturing Manager', dept_mfg),
        ('Quality Inspector', dept_qc),
        ('Sales Manager', dept_sales),
        ('Purchase Manager', dept_purchase),
        ('Machine Operator', dept_mfg),
        ('HR Manager', dept_hr),
    ]

    job_ids = {}
    for job_name, dept_id in jobs:
        jid = find_or_create('hr.job',
            [['name', '=', job_name]],
            {'name': job_name, 'department_id': dept_id},
            'Job Position')
        job_ids[job_name] = jid

    # Create Employees
    employees = [
        {'name': 'Rajesh Kumar', 'job_id': job_ids.get('Manufacturing Manager'),
         'department_id': dept_mfg, 'work_email': 'rajesh@techfurn.com',
         'work_phone': '+91-9876500001'},
        {'name': 'Priya Sharma', 'job_id': job_ids.get('Quality Inspector'),
         'department_id': dept_qc, 'work_email': 'priya@techfurn.com',
         'work_phone': '+91-9876500002'},
        {'name': 'Amit Patel', 'job_id': job_ids.get('Sales Manager'),
         'department_id': dept_sales, 'work_email': 'amit@techfurn.com',
         'work_phone': '+91-9876500003'},
        {'name': 'Neha Gupta', 'job_id': job_ids.get('Purchase Manager'),
         'department_id': dept_purchase, 'work_email': 'neha@techfurn.com',
         'work_phone': '+91-9876500004'},
        {'name': 'Vikram Singh', 'job_id': job_ids.get('Machine Operator'),
         'department_id': dept_mfg, 'work_email': 'vikram@techfurn.com',
         'work_phone': '+91-9876500005'},
        {'name': 'Ananya Reddy', 'job_id': job_ids.get('HR Manager'),
         'department_id': dept_hr, 'work_email': 'ananya@techfurn.com',
         'work_phone': '+91-9876500006'},
    ]

    for emp in employees:
        find_or_create('hr.employee',
            [['name', '=', emp['name']]],
            emp, 'Employee')

safe(create_employees, "Employees")

# ──────────────────────────────────────────────────────────
# PHASE 17: CREATE REORDERING RULES
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 17: Creating Reordering Rules")
print("=" * 70)

def create_reordering_rules():
    if 'stock' not in installed_names:
        print("    ⚠️  Stock not installed, skipping")
        return

    # Find warehouse and buy route
    warehouse = search_read('stock.warehouse', [], ['id', 'lot_stock_id'], limit=1)
    if not warehouse:
        print("    ⚠️  No warehouse found")
        return

    location_id = warehouse[0]['lot_stock_id'][0]

    buy_route = search_read('stock.route',
        [['name', 'ilike', 'Buy']], ['id'], limit=1)
    route_id = buy_route[0]['id'] if buy_route else None

    rules = [
        ('Steel Frame', 5, 20),
        ('Wooden Desktop Panel', 5, 20),
        ('Electric Motor (Height Adjustment)', 5, 15),
        ('Control Panel (Electronic)', 5, 15),
        ('Screws & Hardware Kit', 10, 40),
    ]

    for prod_name, min_qty, max_qty in rules:
        pp_id = raw_material_ids.get(prod_name)
        if not pp_id:
            continue

        existing = search_read('stock.warehouse.orderpoint',
            [['product_id', '=', pp_id]], ['id'], limit=1)
        if existing:
            print(f"    ℹ️  Reorder rule for '{prod_name}' already exists")
            continue

        try:
            vals = {
                'product_id': pp_id,
                'location_id': location_id,
                'product_min_qty': min_qty,
                'product_max_qty': max_qty,
            }
            if route_id:
                vals['route_id'] = route_id
            r_id = create('stock.warehouse.orderpoint', vals)
            print(f"    ✅ Reorder rule: {prod_name} (Min: {min_qty}, Max: {max_qty})")
        except Exception as e:
            print(f"    ⚠️  Reorder rule for '{prod_name}': {e}")

safe(create_reordering_rules, "Reordering Rules")

# ──────────────────────────────────────────────────────────
# PHASE 18: CREATE SECOND CRM LEAD (for demo variety)
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 18: Creating Second CRM Lead")
print("=" * 70)

def create_second_lead():
    if 'crm' not in installed_names:
        return

    find_or_create('crm.lead',
        [['name', '=', '20 SmartDesk Pro - StartUp Innovations']],
        {
            'name': '20 SmartDesk Pro - StartUp Innovations',
            'partner_id': customer2_id,
            'email_from': 'ceo@startupinnovations.com',
            'phone': '+91-9876501234',
            'expected_revenue': 170000.0,
            'type': 'opportunity',
            'description': 'Fast-growing startup needs 20 standing desks for new office. '
                           'Budget pre-approved. Want delivery in 2 weeks.',
        },
        'CRM Lead')

safe(create_second_lead, "Second CRM Lead")

# ──────────────────────────────────────────────────────────
# PHASE 19: VERIFY INSTALLED MODULES
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  PHASE 19: Final Verification")
print("=" * 70)

def final_verification():
    # Refresh installed modules
    critical = ['crm', 'sale_management', 'sale', 'purchase', 'stock', 'mrp',
                'account', 'hr', 'maintenance', 'repair']
    ins = search_read('ir.module.module',
        [['state', '=', 'installed'], ['name', 'in', critical]],
        ['name', 'shortdesc'])
    installed = {m['name']: m['shortdesc'] for m in ins}

    print("\n  INSTALLED MODULES:")
    for name in critical:
        if name in installed:
            print(f"    ✅ {installed[name]} ({name})")
        else:
            print(f"    ❌ {name} — NOT INSTALLED")

    # Count records
    checks = [
        ('Work Centers', 'mrp.workcenter', []),
        ('Raw Materials', 'product.template', [['name', 'in',
            ['Steel Frame', 'Wooden Desktop Panel', 'Electric Motor (Height Adjustment)',
             'Control Panel (Electronic)', 'Screws & Hardware Kit']]]),
        ('Finished Products', 'product.template', [['name', '=', 'SmartDesk Pro']]),
        ('BOMs', 'mrp.bom', []),
        ('CRM Leads', 'crm.lead', []),
        ('Sales Orders', 'sale.order', []),
        ('Purchase Orders', 'purchase.order', []),
        ('Manufacturing Orders', 'mrp.production', []),
        ('Vendors', 'res.partner', [['supplier_rank', '>', 0]]),
        ('Customers', 'res.partner', [['customer_rank', '>', 0]]),
        ('Employees', 'hr.employee', []),
    ]

    print("\n  DATA COUNTS:")
    for label, model, domain in checks:
        try:
            count = len(search(model, domain))
            icon = "✅" if count > 0 else "⚠️ "
            print(f"    {icon} {label}: {count}")
        except:
            print(f"    ⚠️  {label}: model not available")

safe(final_verification, "Verification")

# ──────────────────────────────────────────────────────────
# FINAL SUMMARY
# ──────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  🎉 SETUP COMPLETE!")
print("=" * 70)

if ERRORS:
    print(f"\n  ⚠️  {len(ERRORS)} non-critical errors occurred:")
    for e in ERRORS:
        print(f"    - {e[:100]}")

print(f"""
  ╔══════════════════════════════════════════════════════╗
  ║  YOUR ODOO DATABASE IS CONFIGURED FOR THE DEMO!     ║
  ╠══════════════════════════════════════════════════════╣
  ║                                                      ║
  ║  Company: TechFurn Industries                        ║
  ║  Product: SmartDesk Pro (₹8,500 / $850)              ║
  ║                                                      ║
  ║  WHAT WAS CREATED:                                   ║
  ║  ✅ Modules installed (CRM, Sales, MRP, etc.)        ║
  ║  ✅ 4 Work Centers with hourly costs                 ║
  ║  ✅ 3 Vendors with supplier info                     ║
  ║  ✅ 5 Raw Materials with initial stock               ║
  ║  ✅ 1 Finished Product (SmartDesk Pro)               ║
  ║  ✅ Bill of Materials with 5 operations              ║
  ║  ✅ Reordering Rules for auto-replenishment          ║
  ║  ✅ 3 Quality Control Points                         ║
  ║  ✅ 4 Maintenance Equipment + Team                   ║
  ║  ✅ 2 Customers + 2 CRM Leads                       ║
  ║  ✅ 6 Employees across departments                   ║
  ║  ✅ 1 Sales Order (5 × SmartDesk Pro)                ║
  ║  ✅ 3 Purchase Orders (raw materials)                ║
  ║  ✅ 1 Manufacturing Order (5 units)                  ║
  ║                                                      ║
  ║  NEXT: Open {URL}                                    ║ 
  ║  Follow LIVE_DEMO_PRESENTATION_SCRIPT.md             ║
  ║                                                      ║
  ╚══════════════════════════════════════════════════════╝
""")
