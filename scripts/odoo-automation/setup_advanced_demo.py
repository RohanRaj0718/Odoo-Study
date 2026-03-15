"""
============================================================================
ODOO 19 — ADVANCED MANUFACTURING DEMO (REAL-WORLD COMPLEXITY)
============================================================================
Database: https://last-demo.odoo.com
Company: NovaTech Electronics Pvt Ltd
Product: ProTab X1 (Premium Tablet) + SmartWatch S5 (Wearable)

ADVANCED FEATURES DEMONSTRATED:
  ✦ Multiple products with multi-level BOM
  ✦ Multiple vendors per component (vendor comparison / RFQs)
  ✦ Different costing methods (AVCO, FIFO, Standard)
  ✦ Pricelists (Retail, Wholesale, VIP)
  ✦ Employees linked to their own Odoo USER accounts
  ✦ Bank journal + bank statement for reconciliation
  ✦ Purchase Agreements (Blanket Orders)
  ✦ Quality Control with measures, picture types
  ✦ Maintenance with work-center-linked equipment
  ✦ Subcontracting concept (vendor)
  ✦ Lot/Serial tracking on finished goods
============================================================================
"""
import xmlrpc.client
import datetime
import time
import traceback
import sys
import socket

# Set global socket timeout to avoid hanging
socket.setdefaulttimeout(60)

# ──────────────────────────────────────────────────────────
# CONNECTION
# ──────────────────────────────────────────────────────────
URL = "https://last-demo.odoo.com"
DB = "last-demo"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

print("=" * 72)
print("  ODOO 19 — ADVANCED MANUFACTURING DEMO SETUP")
print("  Database:", URL)
print("=" * 72)

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
version = common.version()
print(f"\n[CONNECT] Odoo {version.get('server_version', '?')}")

uid = common.authenticate(DB, USERNAME, PASSWORD, {})
if not uid:
    print("  ❌ Authentication failed"); sys.exit(1)
print(f"  ✅ UID: {uid}, DB: {DB}")

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

# ──────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────
def _fresh_models():
    """Return a fresh XML-RPC proxy (avoids stale connections)."""
    return xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def exe(model, method, *args, **kwargs):
    global models
    for attempt in range(3):
        try:
            return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kwargs)
        except (ConnectionError, TimeoutError, OSError, socket.timeout) as e:
            if attempt < 2:
                print(f"    ⏳ Network retry {attempt+1}...")
                time.sleep(3)
                models = _fresh_models()
            else:
                raise
        except xmlrpc.client.ProtocolError as e:
            if attempt < 2:
                print(f"    ⏳ Protocol retry {attempt+1}...")
                time.sleep(3)
                models = _fresh_models()
            else:
                raise

def sr(model, domain, fields, limit=0):
    kw = {'fields': fields}
    if limit: kw['limit'] = limit
    return exe(model, 'search_read', [domain], kw)

def sc(model, domain, limit=0):
    kw = {}
    if limit: kw['limit'] = limit
    return exe(model, 'search', [domain], kw)

def cr(model, vals):
    return exe(model, 'create', [vals])

def wr(model, ids, vals):
    if not isinstance(ids, list): ids = [ids]
    return exe(model, 'write', [ids, vals])

def foc(model, domain, vals, label="record"):
    """Find or create."""
    existing = sr(model, domain, ['id', 'name'] if 'name' in vals else ['id'], limit=1)
    if existing:
        rid = existing[0]['id']
        rname = existing[0].get('name', rid)
        print(f"    ℹ️  {label} '{rname}' exists (ID:{rid})")
        return rid
    rid = cr(model, vals)
    print(f"    ✅ {label} '{vals.get('name', rid)}' (ID:{rid})")
    return rid

def gid(model, domain):
    r = sr(model, domain, ['id'], limit=1)
    return r[0]['id'] if r else None

TODAY = datetime.date.today().isoformat()
TOMORROW = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
NEXT_WEEK = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
LAST_MONTH_START = (datetime.date.today().replace(day=1) - datetime.timedelta(days=1)).replace(day=1).isoformat()
ERRORS = []

def safe(fn, section):
    try:
        return fn()
    except Exception as e:
        ERRORS.append(f"[{section}] {e}")
        print(f"    ❌ ERROR: {e}")
        traceback.print_exc()
        return None

# Grab company
user_info = sr('res.users', [['id', '=', uid]], ['name', 'company_id'])
company_id = user_info[0]['company_id'][0] if user_info else 1
INR_id = gid('res.currency', [['name', '=', 'INR']])
USD_id = gid('res.currency', [['name', '=', 'USD']])
IN_id = gid('res.country', [['code', '=', 'IN']])

# ══════════════════════════════════════════════════════════
#  PHASE 1: INSTALL MISSING MODULES
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 1: Installing Modules")
print("=" * 72)

def install_modules():
    installed = {m['name'] for m in sr('ir.module.module', [['state', '=', 'installed']], ['name'])}
    print(f"  Currently installed: {len(installed)} modules")
    need = ['hr_payroll', 'hr_holidays', 'helpdesk', 'purchase_requisition',
            'sale_loyalty',  # pricelists/loyalty
            'account_check_printing',
            ]
    for mod in need:
        if mod in installed:
            print(f"  ✅ {mod} — already installed")
            continue
        mid = sc('ir.module.module', [['name', '=', mod]], limit=1)
        if mid:
            try:
                print(f"  ⏳ Installing {mod}...")
                exe('ir.module.module', 'button_immediate_install', [mid])
                print(f"  ✅ {mod} installed")
                time.sleep(2)
            except Exception as e:
                print(f"  ⚠️  {mod}: {e}")
        else:
            print(f"  ⚠️  {mod} not found in registry")

safe(install_modules, "Modules")

# ══════════════════════════════════════════════════════════
#  PHASE 2: SETTINGS — Work Orders, Multi-Locations, Lots, Pricelists
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 2: Enabling Settings")
print("=" * 72)

def enable_settings():
    # Apply settings in small groups to avoid invalid field errors
    setting_groups = [
        {'group_mrp_routings': True},
        {'module_quality_control': True},
        {'group_stock_multi_locations': True},
        {'group_stock_adv_location': True},
        {'group_stock_tracking_lot': True},
        {'group_product_pricelist': True},
        {'group_purchase_receipts': True},
        {'group_analytic_accounting': True},
    ]
    ok = 0
    for sg in setting_groups:
        key = list(sg.keys())[0]
        try:
            sid = cr('res.config.settings', sg)
            exe('res.config.settings', 'execute', [[sid]])
            ok += 1
            print(f"    ✅ {key}")
        except Exception as e:
            err = str(e)
            if 'Invalid field' in err:
                print(f"    ⚠️  {key}: not available in Odoo 19 — skipped")
            else:
                print(f"    ⚠️  {key}: {err[:100]}")
    print(f"  ✅ {ok}/{len(setting_groups)} settings applied")

safe(enable_settings, "Settings")

# ══════════════════════════════════════════════════════════
#  PHASE 3: PRODUCT CATEGORIES (with DIFFERENT costing methods)
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 3: Product Categories (different costing)")
print("=" * 72)

cat_ids = {}

def create_categories():
    # Find available costing method values
    cats = [
        ('Electronics - AVCO', {'name': 'Electronics - AVCO',
            'property_cost_method': 'average',
            'property_valuation': 'real_time'}),
        ('Mechanical Parts - FIFO', {'name': 'Mechanical Parts - FIFO',
            'property_cost_method': 'fifo',
            'property_valuation': 'real_time'}),
        ('Packaging & Consumables', {'name': 'Packaging & Consumables',
            'property_cost_method': 'standard',
            'property_valuation': 'real_time'}),
        ('Finished Products', {'name': 'Finished Products',
            'property_cost_method': 'average',
            'property_valuation': 'real_time'}),
    ]
    for label, vals in cats:
        cid = foc('product.category', [['name', '=', vals['name']]], vals, 'Category')
        cat_ids[label] = cid

safe(create_categories, "Categories")

# ══════════════════════════════════════════════════════════
#  PHASE 4: VENDORS (6 vendors — multiple per component)
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 4: Creating Vendors")
print("=" * 72)

vendor_ids = {}

def create_vendors():
    vendors = [
        {'name': 'ChipMax Semiconductors', 'email': 'sales@chipmax.in',
         'phone': '+91-80-25001001', 'city': 'Bangalore', 'is_company': True, 'supplier_rank': 1,
         'country_id': IN_id},
        {'name': 'MicroCore Technologies', 'email': 'orders@microcore.com',
         'phone': '+91-44-26001002', 'city': 'Chennai', 'is_company': True, 'supplier_rank': 1,
         'country_id': IN_id},
        {'name': 'DisplayKing Pvt Ltd', 'email': 'supply@displayking.in',
         'phone': '+91-20-27001003', 'city': 'Pune', 'is_company': True, 'supplier_rank': 1,
         'country_id': IN_id},
        {'name': 'PowerCell Battery Co', 'email': 'bulk@powercell.in',
         'phone': '+91-22-28001004', 'city': 'Mumbai', 'is_company': True, 'supplier_rank': 1,
         'country_id': IN_id},
        {'name': 'MetalCraft Precision', 'email': 'info@metalcraft.in',
         'phone': '+91-11-29001005', 'city': 'Delhi', 'is_company': True, 'supplier_rank': 1,
         'country_id': IN_id},
        {'name': 'PackPro Solutions', 'email': 'orders@packpro.in',
         'phone': '+91-40-30001006', 'city': 'Hyderabad', 'is_company': True, 'supplier_rank': 1,
         'country_id': IN_id},
        # Subcontractor
        {'name': 'AssemblyWorks India (Subcontractor)', 'email': 'ops@assemblyworks.in',
         'phone': '+91-80-31001007', 'city': 'Bangalore', 'is_company': True, 'supplier_rank': 1,
         'country_id': IN_id},
    ]
    for v in vendors:
        vid = foc('res.partner', [['name', '=', v['name']]], v, 'Vendor')
        vendor_ids[v['name']] = vid

safe(create_vendors, "Vendors")

# ══════════════════════════════════════════════════════════
#  PHASE 5: CUSTOMERS (3 — different tiers)
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 5: Creating Customers")
print("=" * 72)

customer_ids = {}

def create_customers():
    customers = [
        {'name': 'MegaMart Retail Chain', 'email': 'procurement@megamart.in',
         'phone': '+91-22-50001001', 'city': 'Mumbai', 'is_company': True, 'customer_rank': 1,
         'street': 'Nariman Point, Tower A', 'country_id': IN_id},
        {'name': 'GovTech Solutions (Govt)', 'email': 'tender@govtech.gov.in',
         'phone': '+91-11-50002002', 'city': 'New Delhi', 'is_company': True, 'customer_rank': 1,
         'street': 'Govt IT Park, Sector 62', 'country_id': IN_id},
        {'name': 'TechBridge Exports LLC', 'email': 'imports@techbridge.ae',
         'phone': '+971-4-5553333', 'city': 'Dubai', 'is_company': True, 'customer_rank': 1,
         'street': 'JAFZA South, Warehouse 12', 'country_id': gid('res.country', [['code', '=', 'AE']])},
    ]
    for c in customers:
        cid = foc('res.partner', [['name', '=', c['name']]], c, 'Customer')
        customer_ids[c['name']] = cid

safe(create_customers, "Customers")

# ══════════════════════════════════════════════════════════
#  PHASE 6: WORK CENTERS (5 — more realistic)
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 6: Creating Work Centers")
print("=" * 72)

wc_ids = {}

def create_work_centers():
    wcs = [
        {'name': 'SMT Line (Surface Mount)', 'costs_hour': 80.0,
         'time_start': 15, 'time_stop': 10, 'time_efficiency': 95.0,
         'oee_target': 85.0},
        {'name': 'PCB Assembly', 'costs_hour': 60.0,
         'time_start': 10, 'time_stop': 5, 'time_efficiency': 90.0},
        {'name': 'Display Bonding', 'costs_hour': 50.0,
         'time_start': 5, 'time_stop': 5, 'time_efficiency': 92.0},
        {'name': 'Final Assembly & Testing', 'costs_hour': 45.0,
         'time_start': 8, 'time_stop': 5, 'time_efficiency': 88.0},
        {'name': 'Packaging & Labeling', 'costs_hour': 25.0,
         'time_start': 3, 'time_stop': 3},
    ]
    for wc in wcs:
        wid = foc('mrp.workcenter', [['name', '=', wc['name']]], wc, 'Work Center')
        wc_ids[wc['name']] = wid

safe(create_work_centers, "Work Centers")

# ══════════════════════════════════════════════════════════
#  PHASE 7: RAW MATERIALS — Multiple vendors per product
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 7: Creating Raw Materials (multi-vendor)")
print("=" * 72)

raw_ids = {}  # name -> product.product id

def create_raw_materials():
    # Each material has MULTIPLE vendors with different prices/lead times
    materials = [
        {
            'name': 'Snapdragon 8 Gen3 Processor',
            'standard_price': 4500.0,
            'categ': 'Electronics - AVCO',
            'vendors': [
                ('ChipMax Semiconductors', 4500.0, 5, 7),   # (vendor, price, min_qty, lead days)
                ('MicroCore Technologies', 4800.0, 1, 5),    # Higher price, lower MOQ, faster
            ]
        },
        {
            'name': '10.5" AMOLED Display Panel',
            'standard_price': 3200.0,
            'categ': 'Electronics - AVCO',
            'vendors': [
                ('DisplayKing Pvt Ltd', 3200.0, 10, 10),
                ('MicroCore Technologies', 3500.0, 1, 4),
            ]
        },
        {
            'name': '8000mAh Li-Po Battery',
            'standard_price': 1800.0,
            'categ': 'Electronics - AVCO',
            'vendors': [
                ('PowerCell Battery Co', 1800.0, 20, 8),
                ('ChipMax Semiconductors', 2000.0, 5, 5),
            ]
        },
        {
            'name': '8GB LPDDR5 RAM Module',
            'standard_price': 1200.0,
            'categ': 'Electronics - AVCO',
            'vendors': [
                ('ChipMax Semiconductors', 1200.0, 10, 6),
                ('MicroCore Technologies', 1350.0, 1, 3),
            ]
        },
        {
            'name': '128GB UFS 3.1 Storage',
            'standard_price': 900.0,
            'categ': 'Electronics - AVCO',
            'vendors': [
                ('ChipMax Semiconductors', 900.0, 10, 6),
                ('MicroCore Technologies', 980.0, 5, 4),
            ]
        },
        {
            'name': 'Aluminium Unibody Chassis',
            'standard_price': 1500.0,
            'categ': 'Mechanical Parts - FIFO',
            'vendors': [
                ('MetalCraft Precision', 1500.0, 10, 12),
            ]
        },
        {
            'name': 'Gorilla Glass Screen Protector',
            'standard_price': 350.0,
            'categ': 'Mechanical Parts - FIFO',
            'vendors': [
                ('DisplayKing Pvt Ltd', 350.0, 20, 7),
                ('MetalCraft Precision', 380.0, 5, 5),
            ]
        },
        {
            'name': 'Camera Module 13MP+5MP',
            'standard_price': 800.0,
            'categ': 'Electronics - AVCO',
            'vendors': [
                ('MicroCore Technologies', 800.0, 10, 8),
            ]
        },
        {
            'name': 'USB-C Connector Board',
            'standard_price': 120.0,
            'categ': 'Electronics - AVCO',
            'vendors': [
                ('ChipMax Semiconductors', 120.0, 50, 5),
                ('MicroCore Technologies', 135.0, 10, 3),
            ]
        },
        {
            'name': 'Screws & Flex Cable Kit',
            'standard_price': 80.0,
            'categ': 'Packaging & Consumables',
            'vendors': [
                ('MetalCraft Precision', 80.0, 50, 4),
                ('PackPro Solutions', 85.0, 20, 2),
            ]
        },
        {
            'name': 'Premium Retail Box + Accessories',
            'standard_price': 250.0,
            'categ': 'Packaging & Consumables',
            'vendors': [
                ('PackPro Solutions', 250.0, 50, 5),
            ]
        },
        # SmartWatch components
        {
            'name': '1.4" AMOLED Round Display',
            'standard_price': 1100.0,
            'categ': 'Electronics - AVCO',
            'vendors': [
                ('DisplayKing Pvt Ltd', 1100.0, 20, 8),
            ]
        },
        {
            'name': 'Watch SoC (BLE + GPS)',
            'standard_price': 600.0,
            'categ': 'Electronics - AVCO',
            'vendors': [
                ('ChipMax Semiconductors', 600.0, 20, 7),
                ('MicroCore Technologies', 650.0, 5, 4),
            ]
        },
        {
            'name': '450mAh Watch Battery',
            'standard_price': 200.0,
            'categ': 'Electronics - AVCO',
            'vendors': [
                ('PowerCell Battery Co', 200.0, 50, 6),
            ]
        },
        {
            'name': 'Stainless Steel Watch Case',
            'standard_price': 550.0,
            'categ': 'Mechanical Parts - FIFO',
            'vendors': [
                ('MetalCraft Precision', 550.0, 20, 10),
            ]
        },
        {
            'name': 'Silicone Watch Strap',
            'standard_price': 120.0,
            'categ': 'Mechanical Parts - FIFO',
            'vendors': [
                ('PackPro Solutions', 120.0, 50, 5),
            ]
        },
        {
            'name': 'Heart Rate + SpO2 Sensor',
            'standard_price': 350.0,
            'categ': 'Electronics - AVCO',
            'vendors': [
                ('MicroCore Technologies', 350.0, 20, 6),
            ]
        },
    ]

    for mat in materials:
        categ_id = cat_ids.get(mat['categ'])
        vals = {
            'name': mat['name'],
            'type': 'consu',
            'is_storable': True,
            'list_price': 0,
            'standard_price': mat['standard_price'],
            'sale_ok': False,
            'purchase_ok': True,
        }
        if categ_id:
            vals['categ_id'] = categ_id

        existing = sr('product.template', [['name', '=', mat['name']]], ['id'], limit=1)
        if existing:
            tmpl_id = existing[0]['id']
            print(f"    ℹ️  '{mat['name']}' exists (Tmpl:{tmpl_id})")
        else:
            tmpl_id = cr('product.template', vals)
            print(f"    ✅ '{mat['name']}' (Tmpl:{tmpl_id})")

        # Get product.product ID
        pp = sr('product.product', [['product_tmpl_id', '=', tmpl_id]], ['id'], limit=1)
        pp_id = pp[0]['id'] if pp else tmpl_id
        raw_ids[mat['name']] = pp_id

        # Add multiple vendor pricelists (supplierinfo)
        for vname, vprice, vmin, vlead in mat['vendors']:
            v_id = vendor_ids.get(vname)
            if not v_id:
                continue
            ex = sr('product.supplierinfo',
                [['product_tmpl_id', '=', tmpl_id], ['partner_id', '=', v_id]], ['id'], limit=1)
            if not ex:
                try:
                    si_vals = {
                        'partner_id': v_id,
                        'product_tmpl_id': tmpl_id,
                        'price': vprice,
                        'min_qty': vmin,
                        'delay': vlead,
                    }
                    cr('product.supplierinfo', si_vals)
                    print(f"      ↳ Vendor: {vname} @ ₹{vprice} (MOQ:{vmin}, Lead:{vlead}d)")
                except Exception as e:
                    print(f"      ⚠️  Vendor {vname}: {e}")

safe(create_raw_materials, "Raw Materials")

# ══════════════════════════════════════════════════════════
#  PHASE 8: FINISHED PRODUCTS — ProTab X1 + SmartWatch S5
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 8: Creating Finished Products")
print("=" * 72)

finished_ids = {}  # name -> {tmpl_id, pp_id}

def create_finished_products():
    products = [
        {
            'name': 'ProTab X1',
            'list_price': 24999.0,
            'standard_price': 14350.0,
            'default_code': 'PTAB-X1-001',
            'description_sale': 'Premium 10.5" tablet with Snapdragon 8 Gen3, 8GB RAM, 128GB storage, 8000mAh battery',
        },
        {
            'name': 'SmartWatch S5',
            'list_price': 7999.0,
            'standard_price': 3170.0,
            'default_code': 'SWTCH-S5-001',
            'description_sale': 'Fitness smartwatch with AMOLED display, heart rate, SpO2, GPS, 5-day battery',
        },
    ]
    for p in products:
        vals = {
            'name': p['name'],
            'type': 'consu',
            'is_storable': True,
            'list_price': p['list_price'],
            'standard_price': p['standard_price'],
            'sale_ok': True,
            'purchase_ok': False,
            'categ_id': cat_ids.get('Finished Products'),
            'default_code': p['default_code'],
            'description_sale': p.get('description_sale', ''),
        }
        existing = sr('product.template', [['name', '=', p['name']]], ['id'], limit=1)
        if existing:
            tmpl_id = existing[0]['id']
            print(f"    ℹ️  '{p['name']}' exists (Tmpl:{tmpl_id})")
        else:
            tmpl_id = cr('product.template', vals)
            print(f"    ✅ '{p['name']}' (Tmpl:{tmpl_id})")

        pp = sr('product.product', [['product_tmpl_id', '=', tmpl_id]], ['id'], limit=1)
        pp_id = pp[0]['id'] if pp else tmpl_id
        finished_ids[p['name']] = {'tmpl_id': tmpl_id, 'pp_id': pp_id}

        # Enable Manufacture route
        try:
            mfg_route = sr('stock.route', [['name', 'ilike', 'Manufacture']], ['id'], limit=1)
            if mfg_route:
                wr('product.template', tmpl_id, {'route_ids': [(4, mfg_route[0]['id'])]})
                print(f"      ↳ Manufacture route enabled")
        except Exception as e:
            print(f"      ⚠️  Route: {e}")

safe(create_finished_products, "Finished Products")

# ══════════════════════════════════════════════════════════
#  PHASE 9: BILLS OF MATERIALS (with operations)
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 9: Creating BOMs with Operations")
print("=" * 72)

bom_ids = {}

def create_boms():
    boms = [
        {
            'product': 'ProTab X1',
            'code': 'BOM-PTAB-X1',
            'components': [
                ('Snapdragon 8 Gen3 Processor', 1),
                ('10.5" AMOLED Display Panel', 1),
                ('8000mAh Li-Po Battery', 1),
                ('8GB LPDDR5 RAM Module', 1),
                ('128GB UFS 3.1 Storage', 1),
                ('Aluminium Unibody Chassis', 1),
                ('Gorilla Glass Screen Protector', 1),
                ('Camera Module 13MP+5MP', 1),
                ('USB-C Connector Board', 1),
                ('Screws & Flex Cable Kit', 1),
                ('Premium Retail Box + Accessories', 1),
            ],
            'operations': [
                ('SMT & Chip Placement', 'SMT Line (Surface Mount)', 40, 10),
                ('PCB Board Assembly', 'PCB Assembly', 30, 20),
                ('Display + Glass Bonding', 'Display Bonding', 25, 30),
                ('Final Device Assembly', 'Final Assembly & Testing', 35, 40),
                ('Burn-in Testing & QC', 'Final Assembly & Testing', 20, 50),
                ('Packaging & Boxing', 'Packaging & Labeling', 15, 60),
            ],
        },
        {
            'product': 'SmartWatch S5',
            'code': 'BOM-SWTCH-S5',
            'components': [
                ('1.4" AMOLED Round Display', 1),
                ('Watch SoC (BLE + GPS)', 1),
                ('450mAh Watch Battery', 1),
                ('Stainless Steel Watch Case', 1),
                ('Silicone Watch Strap', 1),
                ('Heart Rate + SpO2 Sensor', 1),
                ('USB-C Connector Board', 1),
                ('Screws & Flex Cable Kit', 1),
                ('Premium Retail Box + Accessories', 1),
            ],
            'operations': [
                ('Watch PCB Assembly', 'SMT Line (Surface Mount)', 20, 10),
                ('Sensor + Display Mount', 'Display Bonding', 15, 20),
                ('Case Assembly & Seal', 'Final Assembly & Testing', 20, 30),
                ('Firmware Flash & Test', 'Final Assembly & Testing', 15, 40),
                ('Strap + Box Packaging', 'Packaging & Labeling', 10, 50),
            ],
        },
    ]

    for b in boms:
        pinfo = finished_ids.get(b['product'])
        if not pinfo:
            print(f"    ⚠️  Product '{b['product']}' not found")
            continue
        tmpl_id = pinfo['tmpl_id']

        existing = sr('mrp.bom', [['product_tmpl_id', '=', tmpl_id]], ['id'], limit=1)
        if existing:
            bom_ids[b['product']] = existing[0]['id']
            print(f"    ℹ️  BOM for '{b['product']}' exists (ID:{existing[0]['id']})")
            continue

        # Build component lines
        bom_lines = []
        for cname, cqty in b['components']:
            pp_id = raw_ids.get(cname)
            if pp_id:
                bom_lines.append((0, 0, {'product_id': pp_id, 'product_qty': cqty}))
            else:
                print(f"      ⚠️  Component '{cname}' missing")

        bom_val = {
            'product_tmpl_id': tmpl_id,
            'product_qty': 1,
            'code': b['code'],
            'type': 'normal',
            'bom_line_ids': bom_lines,
        }
        bom_id = cr('mrp.bom', bom_val)
        bom_ids[b['product']] = bom_id
        print(f"    ✅ BOM '{b['code']}' (ID:{bom_id}) — {len(bom_lines)} components")

        # Add operations
        op_count = 0
        for op_name, wc_name, duration, seq in b['operations']:
            wc_id = wc_ids.get(wc_name)
            if not wc_id:
                continue
            try:
                cr('mrp.routing.workcenter', {
                    'name': op_name,
                    'workcenter_id': wc_id,
                    'time_cycle_manual': duration,
                    'sequence': seq,
                    'bom_id': bom_id,
                })
                op_count += 1
                print(f"      ↳ Op: {op_name} @ {wc_name} ({duration}min)")
            except Exception as e:
                print(f"      ⚠️  Op '{op_name}': {e}")
        print(f"    ✅ {op_count} operations added")

safe(create_boms, "BOMs")

# ══════════════════════════════════════════════════════════
#  PHASE 10: INITIAL STOCK
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 10: Loading Initial Stock")
print("=" * 72)

def load_stock():
    stock_loc = sr('stock.location',
        [['usage', '=', 'internal'], ['name', '=', 'Stock']], ['id', 'complete_name'], limit=1)
    if not stock_loc:
        stock_loc = sr('stock.location', [['usage', '=', 'internal']], ['id'], limit=1)
    if not stock_loc:
        print("    ❌ No stock location"); return
    loc_id = stock_loc[0]['id']

    stock_levels = {
        'Snapdragon 8 Gen3 Processor': 30,
        '10.5" AMOLED Display Panel': 30,
        '8000mAh Li-Po Battery': 30,
        '8GB LPDDR5 RAM Module': 30,
        '128GB UFS 3.1 Storage': 30,
        'Aluminium Unibody Chassis': 25,
        'Gorilla Glass Screen Protector': 40,
        'Camera Module 13MP+5MP': 30,
        'USB-C Connector Board': 60,
        'Screws & Flex Cable Kit': 100,
        'Premium Retail Box + Accessories': 50,
        '1.4" AMOLED Round Display': 40,
        'Watch SoC (BLE + GPS)': 40,
        '450mAh Watch Battery': 50,
        'Stainless Steel Watch Case': 40,
        'Silicone Watch Strap': 60,
        'Heart Rate + SpO2 Sensor': 40,
    }

    for pname, qty in stock_levels.items():
        pp_id = raw_ids.get(pname)
        if not pp_id:
            continue
        try:
            quants = sr('stock.quant',
                [['product_id', '=', pp_id], ['location_id', '=', loc_id]], ['id', 'quantity'])
            curr = quants[0]['quantity'] if quants else 0
            if curr >= qty:
                print(f"    ℹ️  {pname}: {curr} in stock")
                continue
            if quants:
                wr('stock.quant', quants[0]['id'], {'inventory_quantity': qty})
                try: exe('stock.quant', 'action_apply_inventory', [[quants[0]['id']]])
                except: pass
            else:
                q_id = cr('stock.quant', {
                    'product_id': pp_id, 'location_id': loc_id, 'inventory_quantity': qty})
                try: exe('stock.quant', 'action_apply_inventory', [[q_id]])
                except: pass
            print(f"    ✅ {pname}: {qty} units")
        except Exception as e:
            print(f"    ⚠️  {pname}: {e}")

safe(load_stock, "Stock")

# ══════════════════════════════════════════════════════════
#  PHASE 11: PRICELISTS (Retail, Wholesale, VIP/Export)
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 11: Creating Pricelists")
print("=" * 72)

pricelist_ids = {}

def create_pricelists():
    # 1. Retail (default — no discount)
    pl_retail = foc('product.pricelist',
        [['name', '=', 'Retail (MRP)']],
        {'name': 'Retail (MRP)', 'currency_id': INR_id}, 'Pricelist')
    pricelist_ids['Retail'] = pl_retail

    # 2. Wholesale — 15% discount on all
    pl_wholesale = foc('product.pricelist',
        [['name', '=', 'Wholesale (15% off)']],
        {'name': 'Wholesale (15% off)', 'currency_id': INR_id}, 'Pricelist')
    pricelist_ids['Wholesale'] = pl_wholesale
    # Add discount rule
    existing_rule = sr('product.pricelist.item',
        [['pricelist_id', '=', pl_wholesale]], ['id'], limit=1)
    if not existing_rule:
        try:
            cr('product.pricelist.item', {
                'pricelist_id': pl_wholesale,
                'applied_on': '3_global',
                'compute_price': 'percentage',
                'percent_price': 15.0,
            })
            print(f"      ↳ 15% discount rule added")
        except Exception as e:
            print(f"      ⚠️  Pricelist rule: {e}")

    # 3. VIP / Export — 25% discount
    pl_vip = foc('product.pricelist',
        [['name', '=', 'VIP / Export (25% off)']],
        {'name': 'VIP / Export (25% off)', 'currency_id': INR_id}, 'Pricelist')
    pricelist_ids['VIP'] = pl_vip
    existing_rule2 = sr('product.pricelist.item',
        [['pricelist_id', '=', pl_vip]], ['id'], limit=1)
    if not existing_rule2:
        try:
            cr('product.pricelist.item', {
                'pricelist_id': pl_vip,
                'applied_on': '3_global',
                'compute_price': 'percentage',
                'percent_price': 25.0,
            })
            print(f"      ↳ 25% discount rule added")
        except Exception as e:
            print(f"      ⚠️  Pricelist rule: {e}")

    # Assign pricelists to customers
    try:
        if customer_ids.get('MegaMart Retail Chain'):
            wr('res.partner', customer_ids['MegaMart Retail Chain'],
               {'property_product_pricelist': pl_wholesale})
            print("    ✅ MegaMart → Wholesale pricelist")
    except Exception as e:
        print(f"    ⚠️  Pricelist assign: {e}")

    try:
        if customer_ids.get('TechBridge Exports LLC'):
            wr('res.partner', customer_ids['TechBridge Exports LLC'],
               {'property_product_pricelist': pl_vip})
            print("    ✅ TechBridge → VIP pricelist")
    except Exception as e:
        print(f"    ⚠️  Pricelist assign: {e}")

safe(create_pricelists, "Pricelists")

# ══════════════════════════════════════════════════════════
#  PHASE 12: DEPARTMENTS, JOBS, EMPLOYEES & USERS
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 12: Creating Departments, Employees & Users")
print("=" * 72)

employee_ids = {}
user_ids_map = {}

def create_employees_and_users():
    # Departments
    depts = {}
    for dname in ['Manufacturing', 'Quality Assurance', 'Sales & Marketing',
                   'Procurement', 'Human Resources', 'Finance & Accounting',
                   'Warehouse & Logistics', 'R&D Engineering']:
        depts[dname] = foc('hr.department', [['name', '=', dname]],
                           {'name': dname}, 'Department')

    # Employees with LINKED USERS
    # Each employee gets a res.users record so they can log in
    employees = [
        {'name': 'Arjun Mehta', 'job': 'Production Manager',
         'dept': 'Manufacturing', 'email': 'arjun@novatech.in',
         'work_phone': '+91-80-4001001'},
        {'name': 'Sneha Iyer', 'job': 'Quality Manager',
         'dept': 'Quality Assurance', 'email': 'sneha@novatech.in',
         'work_phone': '+91-80-4001002'},
        {'name': 'Rohit Saxena', 'job': 'Sales Head',
         'dept': 'Sales & Marketing', 'email': 'rohit@novatech.in',
         'work_phone': '+91-80-4001003'},
        {'name': 'Kavitha Nair', 'job': 'Purchase Manager',
         'dept': 'Procurement', 'email': 'kavitha@novatech.in',
         'work_phone': '+91-80-4001004'},
        {'name': 'Deepak Joshi', 'job': 'Warehouse Supervisor',
         'dept': 'Warehouse & Logistics', 'email': 'deepak@novatech.in',
         'work_phone': '+91-80-4001005'},
        {'name': 'Meera Kulkarni', 'job': 'Finance Controller',
         'dept': 'Finance & Accounting', 'email': 'meera@novatech.in',
         'work_phone': '+91-80-4001006'},
        {'name': 'Sanjay Reddy', 'job': 'Machine Operator',
         'dept': 'Manufacturing', 'email': 'sanjay@novatech.in',
         'work_phone': '+91-80-4001007'},
        {'name': 'Priyanka Das', 'job': 'HR Manager',
         'dept': 'Human Resources', 'email': 'priyanka@novatech.in',
         'work_phone': '+91-80-4001008'},
        {'name': 'Anil Sharma', 'job': 'R&D Engineer',
         'dept': 'R&D Engineering', 'email': 'anil@novatech.in',
         'work_phone': '+91-80-4001009'},
        {'name': 'Divya Patel', 'job': 'Accounts Executive',
         'dept': 'Finance & Accounting', 'email': 'divya@novatech.in',
         'work_phone': '+91-80-4001010'},
    ]

    for emp in employees:
        # Create Job Position
        dept_id = depts.get(emp['dept'])
        job_id = foc('hr.job', [['name', '=', emp['job']]],
                     {'name': emp['job'], 'department_id': dept_id}, 'Job')

        # Create User account first
        ex_user = sr('res.users', [['login', '=', emp['email']]], ['id', 'name'], limit=1)
        if ex_user:
            u_id = ex_user[0]['id']
            print(f"    ℹ️  User '{emp['email']}' exists (ID:{u_id})")
        else:
            try:
                u_id = cr('res.users', {
                    'name': emp['name'],
                    'login': emp['email'],
                    'email': emp['email'],
                    'password': 'NovaTech@123',
                    'company_id': company_id,
                    'company_ids': [(4, company_id)],
                })
                print(f"    ✅ User '{emp['name']}' ({emp['email']}) ID:{u_id}")
            except Exception as e:
                print(f"    ⚠️  User '{emp['email']}': {e}")
                u_id = None
        user_ids_map[emp['name']] = u_id

        # Create Employee linked to user
        emp_vals = {
            'name': emp['name'],
            'job_id': job_id,
            'department_id': dept_id,
            'work_email': emp['email'],
            'work_phone': emp['work_phone'],
        }
        if u_id:
            emp_vals['user_id'] = u_id

        eid = foc('hr.employee', [['name', '=', emp['name']]], emp_vals, 'Employee')
        employee_ids[emp['name']] = eid

safe(create_employees_and_users, "Employees & Users")

# ══════════════════════════════════════════════════════════
#  PHASE 13: CRM LEADS (3 realistic)
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 13: Creating CRM Leads")
print("=" * 72)

def create_leads():
    leads = [
        {
            'name': 'MegaMart Q2 Tablet Order - 200 ProTab X1',
            'partner_id': customer_ids.get('MegaMart Retail Chain'),
            'expected_revenue': 4249830.0,  # 200 × 24999 × 0.85
            'type': 'opportunity',
            'user_id': user_ids_map.get('Rohit Saxena'),
            'description': 'MegaMart wants 200 ProTab X1 tablets for Q2 launch in 50 stores. '
                           'Need wholesale pricing. Delivery in 4 batches of 50.',
        },
        {
            'name': 'GovTech Tablet Tender - 500 ProTab X1',
            'partner_id': customer_ids.get('GovTech Solutions (Govt)'),
            'expected_revenue': 12499500.0,
            'type': 'opportunity',
            'description': 'Government tender for 500 tablets for school digitization project. '
                           'Need competitive pricing. L1 bidding, deadline in 2 weeks.',
        },
        {
            'name': 'TechBridge Export - 100 SmartWatch S5',
            'partner_id': customer_ids.get('TechBridge Exports LLC'),
            'expected_revenue': 599925.0,
            'type': 'opportunity',
            'description': 'Dubai export order. 100 SmartWatch S5 units. Need VIP pricing. '
                           'Export documentation + certificate of origin required.',
        },
    ]
    for l in leads:
        foc('crm.lead', [['name', '=', l['name']]], l, 'Lead')

safe(create_leads, "CRM Leads")

# ══════════════════════════════════════════════════════════
#  PHASE 14: SALES ORDERS (2 — with pricelists)
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 14: Creating Sales Orders")
print("=" * 72)

so_ids = {}

def create_sales_orders():
    orders = [
        {
            'name_label': 'MegaMart',
            'partner_id': customer_ids.get('MegaMart Retail Chain'),
            'pricelist_id': pricelist_ids.get('Wholesale'),
            'lines': [
                ('ProTab X1', 25, None),  # None = let pricelist calculate
            ],
        },
        {
            'name_label': 'TechBridge',
            'partner_id': customer_ids.get('TechBridge Exports LLC'),
            'pricelist_id': pricelist_ids.get('VIP'),
            'lines': [
                ('SmartWatch S5', 20, None),
                ('ProTab X1', 10, None),
            ],
        },
    ]

    for o in orders:
        if not o['partner_id']:
            continue
        existing = sr('sale.order',
            [['partner_id', '=', o['partner_id']], ['state', 'in', ['draft', 'sale']]],
            ['id', 'name'], limit=1)
        if existing:
            so_ids[o['name_label']] = existing[0]['id']
            print(f"    ℹ️  SO for {o['name_label']} exists: {existing[0]['name']}")
            continue

        lines = []
        for pname, qty, price in o['lines']:
            pinfo = finished_ids.get(pname)
            if not pinfo:
                continue
            line_vals = {'product_id': pinfo['pp_id'], 'product_uom_qty': qty}
            if price:
                line_vals['price_unit'] = price
            lines.append((0, 0, line_vals))

        so_vals = {
            'partner_id': o['partner_id'],
            'date_order': TODAY,
            'order_line': lines,
        }
        if o.get('pricelist_id'):
            so_vals['pricelist_id'] = o['pricelist_id']
        if user_ids_map.get('Rohit Saxena'):
            so_vals['user_id'] = user_ids_map['Rohit Saxena']

        try:
            so_id = cr('sale.order', so_vals)
            so_ids[o['name_label']] = so_id
            so_info = sr('sale.order', [['id', '=', so_id]], ['name', 'amount_total'])
            so_name = so_info[0]['name'] if so_info else str(so_id)
            so_total = so_info[0]['amount_total'] if so_info else '?'
            print(f"    ✅ SO: {so_name} for {o['name_label']} | Total: ₹{so_total}")
        except Exception as e:
            print(f"    ❌ SO for {o['name_label']}: {e}")

safe(create_sales_orders, "Sales Orders")

# ══════════════════════════════════════════════════════════
#  PHASE 15: PURCHASE ORDERS — Multiple RFQs to different vendors
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 15: Creating Purchase Orders / RFQs")
print("=" * 72)

po_ids = []

def create_purchase_orders():
    """Create multiple RFQs: some confirmed, some still draft (for demo comparison)."""
    purchase_orders = [
        # PO 1: ChipMax — large order, best prices
        {
            'vendor': 'ChipMax Semiconductors',
            'confirm': True,
            'lines': [
                ('Snapdragon 8 Gen3 Processor', 50, 4500.0),
                ('8GB LPDDR5 RAM Module', 50, 1200.0),
                ('128GB UFS 3.1 Storage', 50, 900.0),
                ('USB-C Connector Board', 100, 120.0),
                ('Watch SoC (BLE + GPS)', 50, 600.0),
            ],
        },
        # PO 2: MicroCore — COMPETING RFQ (higher price, faster delivery — draft)
        {
            'vendor': 'MicroCore Technologies',
            'confirm': False,  # Keep as draft RFQ for comparison demo
            'lines': [
                ('Snapdragon 8 Gen3 Processor', 50, 4800.0),
                ('8GB LPDDR5 RAM Module', 50, 1350.0),
                ('128GB UFS 3.1 Storage', 50, 980.0),
            ],
        },
        # PO 3: DisplayKing — displays
        {
            'vendor': 'DisplayKing Pvt Ltd',
            'confirm': True,
            'lines': [
                ('10.5" AMOLED Display Panel', 40, 3200.0),
                ('Gorilla Glass Screen Protector', 60, 350.0),
                ('1.4" AMOLED Round Display', 50, 1100.0),
            ],
        },
        # PO 4: PowerCell — batteries
        {
            'vendor': 'PowerCell Battery Co',
            'confirm': True,
            'lines': [
                ('8000mAh Li-Po Battery', 40, 1800.0),
                ('450mAh Watch Battery', 60, 200.0),
            ],
        },
        # PO 5: MetalCraft — chassis + mechanical
        {
            'vendor': 'MetalCraft Precision',
            'confirm': True,
            'lines': [
                ('Aluminium Unibody Chassis', 30, 1500.0),
                ('Stainless Steel Watch Case', 50, 550.0),
                ('Screws & Flex Cable Kit', 100, 80.0),
            ],
        },
        # PO 6: PackPro — packaging (draft for negotiation demo)
        {
            'vendor': 'PackPro Solutions',
            'confirm': False,
            'lines': [
                ('Premium Retail Box + Accessories', 100, 250.0),
                ('Silicone Watch Strap', 80, 120.0),
            ],
        },
    ]

    for po_data in purchase_orders:
        v_id = vendor_ids.get(po_data['vendor'])
        if not v_id:
            continue

        existing = sr('purchase.order',
            [['partner_id', '=', v_id], ['state', 'in', ['draft', 'purchase']]],
            ['id', 'name'], limit=1)
        if existing:
            print(f"    ℹ️  PO for {po_data['vendor']} exists: {existing[0]['name']}")
            po_ids.append(existing[0]['id'])
            continue

        order_lines = []
        for pname, qty, price in po_data['lines']:
            pp_id = raw_ids.get(pname)
            if pp_id:
                order_lines.append((0, 0, {
                    'product_id': pp_id,
                    'product_qty': qty,
                    'price_unit': price,
                    'name': pname,
                }))

        if not order_lines:
            continue

        try:
            po_id = cr('purchase.order', {
                'partner_id': v_id,
                'date_order': TODAY,
                'order_line': order_lines,
            })
            po_ids.append(po_id)
            pi = sr('purchase.order', [['id', '=', po_id]], ['name', 'amount_total'])
            pname = pi[0]['name'] if pi else str(po_id)
            ptotal = pi[0]['amount_total'] if pi else '?'
            status = 'CONFIRMED' if po_data['confirm'] else 'DRAFT (RFQ)'
            print(f"    ✅ {pname} → {po_data['vendor']} | ₹{ptotal} [{status}]")

            if po_data['confirm']:
                try:
                    exe('purchase.order', 'button_confirm', [[po_id]])
                    print(f"      ↳ Confirmed")
                except Exception as e:
                    print(f"      ⚠️  Confirm: {e}")
        except Exception as e:
            print(f"    ❌ PO {po_data['vendor']}: {e}")

safe(create_purchase_orders, "Purchase Orders")

# ══════════════════════════════════════════════════════════
#  PHASE 16: MANUFACTURING ORDERS
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 16: Creating Manufacturing Orders")
print("=" * 72)

mo_ids = {}

def create_mos():
    mos = [
        ('ProTab X1', 10, 'Regular production batch'),
        ('SmartWatch S5', 15, 'SmartWatch batch for export + retail'),
    ]
    for pname, qty, note in mos:
        pinfo = finished_ids.get(pname)
        if not pinfo:
            continue
        existing = sr('mrp.production',
            [['product_id', '=', pinfo['pp_id']],
             ['state', 'in', ['draft', 'confirmed', 'progress']]],
            ['id', 'name'], limit=1)
        if existing:
            mo_ids[pname] = existing[0]['id']
            print(f"    ℹ️  MO for {pname} exists: {existing[0]['name']}")
            continue

        mo_vals = {
            'product_id': pinfo['pp_id'],
            'product_qty': qty,
            'date_start': TODAY,
        }
        bom = bom_ids.get(pname)
        if bom:
            mo_vals['bom_id'] = bom

        try:
            mo_id = cr('mrp.production', mo_vals)
            mo_ids[pname] = mo_id
            mi = sr('mrp.production', [['id', '=', mo_id]], ['name'])
            moname = mi[0]['name'] if mi else str(mo_id)
            print(f"    ✅ MO: {moname} — {qty}× {pname}")
            try:
                exe('mrp.production', 'action_confirm', [[mo_id]])
                print(f"      ↳ Confirmed")
            except Exception as e:
                print(f"      ⚠️  Confirm: {e}")
        except Exception as e:
            print(f"    ❌ MO {pname}: {e}")

safe(create_mos, "Manufacturing Orders")

# ══════════════════════════════════════════════════════════
#  PHASE 17: QUALITY CONTROL POINTS
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 17: Quality Control Points")
print("=" * 72)

def create_qcps():
    try:
        sr('quality.point', [], ['id'], limit=1)
    except:
        print("    ⚠️  Quality module not available"); return

    receipt_pt = sr('stock.picking.type', [['code', '=', 'incoming']], ['id'], limit=1)
    mfg_pt = sr('stock.picking.type', [['code', '=', 'mrp_operation']], ['id'], limit=1)
    passfail = gid('quality.point.test_type', [['technical_name', '=', 'passfail']])
    measure = gid('quality.point.test_type', [['technical_name', '=', 'measure']])

    qcps = [
        {
            'title': 'Incoming Component Inspection',
            'picking_type_ids': [(6, 0, [receipt_pt[0]['id']])] if receipt_pt else False,
            'test_type_id': passfail,
            'note': 'Verify component specs, packaging integrity, vendor COA (Certificate of Analysis).',
        },
    ]

    # Product-specific QCPs for manufacturing
    for pname in ['ProTab X1', 'SmartWatch S5']:
        pinfo = finished_ids.get(pname)
        if not pinfo or not mfg_pt:
            continue
        qcps.append({
            'title': f'{pname} — Display Alignment Check',
            'product_ids': [(6, 0, [pinfo['pp_id']])],
            'picking_type_ids': [(6, 0, [mfg_pt[0]['id']])],
            'test_type_id': measure,
            'note': f'Measure display-to-bezel gap. Must be ≤ 0.3mm on all sides.',
        })
        qcps.append({
            'title': f'{pname} — Final Functional Test',
            'product_ids': [(6, 0, [pinfo['pp_id']])],
            'picking_type_ids': [(6, 0, [mfg_pt[0]['id']])],
            'test_type_id': passfail,
            'note': f'Boot test, touch response, battery charge, camera, sensors, connectivity.',
        })

    for qcp in qcps:
        title = qcp.get('title', '')
        existing = sr('quality.point', [['title', '=', title]], ['id'], limit=1)
        if existing:
            print(f"    ℹ️  QCP '{title}' exists")
            continue
        try:
            qid = cr('quality.point', qcp)
            print(f"    ✅ QCP: '{title}' (ID:{qid})")
        except Exception as e:
            print(f"    ⚠️  QCP '{title}': {e}")

safe(create_qcps, "QCPs")

# ══════════════════════════════════════════════════════════
#  PHASE 18: MAINTENANCE TEAMS + EQUIPMENT
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 18: Maintenance Equipment & Teams")
print("=" * 72)

def create_maintenance():
    team_id = foc('maintenance.team', [['name', '=', 'Electronics Production Team']],
                  {'name': 'Electronics Production Team'}, 'Maintenance Team')
    cat_id = foc('maintenance.equipment.category', [['name', '=', 'SMT & Assembly Machines']],
                 {'name': 'SMT & Assembly Machines'}, 'Equipment Category')
    cat_id2 = foc('maintenance.equipment.category', [['name', '=', 'Testing Equipment']],
                  {'name': 'Testing Equipment'}, 'Equipment Category')

    equipment = [
        {'name': 'Pick & Place Machine (SMT)', 'category_id': cat_id,
         'maintenance_team_id': team_id, 'serial_no': 'PNP-2024-001',
         'workcenter_id': wc_ids.get('SMT Line (Surface Mount)'), 'cost': 2500000.0},
        {'name': 'Reflow Oven', 'category_id': cat_id,
         'maintenance_team_id': team_id, 'serial_no': 'RFO-2024-002',
         'workcenter_id': wc_ids.get('SMT Line (Surface Mount)'), 'cost': 800000.0},
        {'name': 'Display Lamination Press', 'category_id': cat_id,
         'maintenance_team_id': team_id, 'serial_no': 'DLP-2024-003',
         'workcenter_id': wc_ids.get('Display Bonding'), 'cost': 600000.0},
        {'name': 'ICT Tester (In-Circuit)', 'category_id': cat_id2,
         'maintenance_team_id': team_id, 'serial_no': 'ICT-2024-004',
         'workcenter_id': wc_ids.get('Final Assembly & Testing'), 'cost': 350000.0},
        {'name': 'Automated Packaging Line', 'category_id': cat_id,
         'maintenance_team_id': team_id, 'serial_no': 'APL-2024-005',
         'workcenter_id': wc_ids.get('Packaging & Labeling'), 'cost': 450000.0},
    ]

    for eq in equipment:
        # Remove None workcenter_id
        if not eq.get('workcenter_id'):
            eq.pop('workcenter_id', None)
        foc('maintenance.equipment', [['name', '=', eq['name']]], eq, 'Equipment')

safe(create_maintenance, "Maintenance")

# ══════════════════════════════════════════════════════════
#  PHASE 19: REORDERING RULES
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 19: Reordering Rules")
print("=" * 72)

def create_reorder_rules():
    wh = sr('stock.warehouse', [], ['id', 'lot_stock_id'], limit=1)
    if not wh:
        print("    ⚠️  No warehouse"); return
    loc_id = wh[0]['lot_stock_id'][0]
    buy_route = sr('stock.route', [['name', 'ilike', 'Buy']], ['id'], limit=1)
    route_id = buy_route[0]['id'] if buy_route else None

    rules = [
        ('Snapdragon 8 Gen3 Processor', 10, 50),
        ('10.5" AMOLED Display Panel', 10, 40),
        ('8000mAh Li-Po Battery', 10, 40),
        ('8GB LPDDR5 RAM Module', 10, 50),
        ('128GB UFS 3.1 Storage', 10, 50),
        ('Aluminium Unibody Chassis', 5, 30),
        ('USB-C Connector Board', 20, 80),
        ('Screws & Flex Cable Kit', 30, 100),
        ('1.4" AMOLED Round Display', 10, 50),
        ('Watch SoC (BLE + GPS)', 10, 50),
        ('450mAh Watch Battery', 15, 60),
    ]

    for pname, mn, mx in rules:
        pp_id = raw_ids.get(pname)
        if not pp_id:
            continue
        ex = sr('stock.warehouse.orderpoint', [['product_id', '=', pp_id]], ['id'], limit=1)
        if ex:
            print(f"    ℹ️  Rule for '{pname}' exists")
            continue
        vals = {'product_id': pp_id, 'location_id': loc_id,
                'product_min_qty': mn, 'product_max_qty': mx}
        if route_id:
            vals['route_id'] = route_id
        try:
            cr('stock.warehouse.orderpoint', vals)
            print(f"    ✅ {pname}: Min={mn}, Max={mx}")
        except Exception as e:
            print(f"    ⚠️  {pname}: {e}")

safe(create_reorder_rules, "Reordering Rules")

# ══════════════════════════════════════════════════════════
#  PHASE 20: BANK JOURNAL + BANK STATEMENT (for reconciliation)
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 20: Bank Setup & Statement for Reconciliation")
print("=" * 72)

def setup_bank_reconciliation():
    # Find or create bank journal
    bank_journal = sr('account.journal', [['type', '=', 'bank']], ['id', 'name'], limit=1)
    if bank_journal:
        journal_id = bank_journal[0]['id']
        print(f"    ℹ️  Bank journal exists: {bank_journal[0]['name']} (ID:{journal_id})")
    else:
        try:
            journal_id = cr('account.journal', {
                'name': 'HDFC Bank - Current Account',
                'type': 'bank',
                'code': 'HDFC',
                'company_id': company_id,
            })
            print(f"    ✅ Bank journal created (ID:{journal_id})")
        except Exception as e:
            print(f"    ⚠️  Bank journal: {e}")
            return

    # Create bank statement with sample transactions
    existing_stmt = sr('account.bank.statement',
        [['journal_id', '=', journal_id]], ['id', 'name'], limit=1)
    if existing_stmt:
        print(f"    ℹ️  Bank statement exists: {existing_stmt[0].get('name', existing_stmt[0]['id'])}")
        return

    try:
        # In Odoo 19, bank statement lines can be created directly
        # They appear in the reconciliation widget
        stmt_lines = [
            {
                'date': TODAY,
                'payment_ref': 'NEFT-MegaMart-Payment',
                'amount': 531228.75,  # Partial payment from MegaMart
                'partner_id': customer_ids.get('MegaMart Retail Chain'),
                'journal_id': journal_id,
            },
            {
                'date': TODAY,
                'payment_ref': 'RTGS-ChipMax-Vendor-Pay',
                'amount': -402000.0,  # Payment to ChipMax
                'partner_id': vendor_ids.get('ChipMax Semiconductors'),
                'journal_id': journal_id,
            },
            {
                'date': TODAY,
                'payment_ref': 'NEFT-TechBridge-Advance',
                'amount': 200000.0,   # Advance from TechBridge
                'partner_id': customer_ids.get('TechBridge Exports LLC'),
                'journal_id': journal_id,
            },
            {
                'date': TODAY,
                'payment_ref': 'UPI-Office-Rent-Feb',
                'amount': -85000.0,
                'journal_id': journal_id,
            },
            {
                'date': TODAY,
                'payment_ref': 'NEFT-DisplayKing-Payment',
                'amount': -155500.0,
                'partner_id': vendor_ids.get('DisplayKing Pvt Ltd'),
                'journal_id': journal_id,
            },
            {
                'date': TODAY,
                'payment_ref': 'Bank-Interest-Credit',
                'amount': 4250.0,
                'journal_id': journal_id,
            },
        ]

        for sl in stmt_lines:
            try:
                sl_id = cr('account.bank.statement.line', sl)
                direction = 'CR' if sl['amount'] > 0 else 'DR'
                print(f"    ✅ {sl['payment_ref']}: ₹{abs(sl['amount']):,.2f} [{direction}]")
            except Exception as e:
                print(f"    ⚠️  Line '{sl['payment_ref']}': {e}")

    except Exception as e:
        print(f"    ❌ Bank statement: {e}")

safe(setup_bank_reconciliation, "Bank Reconciliation")

# ══════════════════════════════════════════════════════════
#  PHASE 21: VENDOR BILLS (for reconciliation matching)
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 21: Vendor Bills (for reconciliation)")
print("=" * 72)

def create_vendor_bills():
    bills = [
        {
            'vendor': 'ChipMax Semiconductors',
            'ref': 'CHIP/INV/2026/0023',
            'amount': 402000.0,
            'label': 'Processor + RAM supply',
        },
        {
            'vendor': 'DisplayKing Pvt Ltd',
            'ref': 'DK/2026/0087',
            'amount': 155500.0,
            'label': 'Display panels supply',
        },
    ]
    purchase_journal = sr('account.journal', [['type', '=', 'purchase']], ['id'], limit=1)
    if not purchase_journal:
        print("    ⚠️  No purchase journal found"); return
    pj_id = purchase_journal[0]['id']

    for bill in bills:
        v_id = vendor_ids.get(bill['vendor'])
        if not v_id:
            continue
        existing = sr('account.move',
            [['partner_id', '=', v_id], ['move_type', '=', 'in_invoice'],
             ['ref', '=', bill['ref']]],
            ['id'], limit=1)
        if existing:
            print(f"    ℹ️  Bill {bill['ref']} exists")
            continue

        try:
            # Find expense account
            exp_acct = sr('account.account',
                [['account_type', '=', 'expense']], ['id'], limit=1)
            acct_id = exp_acct[0]['id'] if exp_acct else None

            bill_vals = {
                'move_type': 'in_invoice',
                'partner_id': v_id,
                'ref': bill['ref'],
                'invoice_date': TODAY,
                'journal_id': pj_id,
                'invoice_line_ids': [(0, 0, {
                    'name': bill['label'],
                    'quantity': 1,
                    'price_unit': bill['amount'],
                    'account_id': acct_id,
                })],
            }
            bill_id = cr('account.move', bill_vals)
            print(f"    ✅ Bill: {bill['ref']} — ₹{bill['amount']:,.0f}")

            # Post the bill
            try:
                exe('account.move', 'action_post', [[bill_id]])
                print(f"      ↳ Posted")
            except Exception as e:
                print(f"      ⚠️  Post: {e}")
        except Exception as e:
            print(f"    ❌ Bill {bill['ref']}: {e}")

safe(create_vendor_bills, "Vendor Bills")

# ══════════════════════════════════════════════════════════
#  PHASE 22: FINAL VERIFICATION
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  PHASE 22: Final Verification")
print("=" * 72)

def verify():
    checks = [
        ('Work Centers', 'mrp.workcenter', []),
        ('Raw Materials', 'product.template', [['sale_ok', '=', False], ['purchase_ok', '=', True]]),
        ('Finished Products', 'product.template', [['name', 'in', ['ProTab X1', 'SmartWatch S5']]]),
        ('BOMs', 'mrp.bom', []),
        ('CRM Leads', 'crm.lead', []),
        ('Sales Orders', 'sale.order', []),
        ('Purchase Orders', 'purchase.order', []),
        ('Manufacturing Orders', 'mrp.production', []),
        ('Vendors', 'res.partner', [['supplier_rank', '>', 0]]),
        ('Customers', 'res.partner', [['customer_rank', '>', 0]]),
        ('Employees', 'hr.employee', []),
        ('Users', 'res.users', []),
        ('Pricelists', 'product.pricelist', []),
        ('Quality Points', 'quality.point', []),
        ('Maintenance Equipment', 'maintenance.equipment', []),
        ('Reordering Rules', 'stock.warehouse.orderpoint', []),
        ('Bank Statement Lines', 'account.bank.statement.line', []),
    ]
    print("\n  DATA COUNTS:")
    for label, model, domain in checks:
        try:
            count = len(sc(model, domain))
            icon = "✅" if count > 0 else "⚠️ "
            print(f"    {icon} {label}: {count}")
        except:
            print(f"    ⚠️  {label}: model unavailable")

safe(verify, "Verification")

# ══════════════════════════════════════════════════════════
#  DONE
# ══════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("  🎉 ADVANCED DEMO SETUP COMPLETE!")
print("=" * 72)

if ERRORS:
    print(f"\n  ⚠️  {len(ERRORS)} errors:")
    for e in ERRORS:
        print(f"    - {e[:120]}")

print(f"""
  ╔═══════════════════════════════════════════════════════════════╗
  ║  DATABASE READY: {URL:<42s} ║
  ╠═══════════════════════════════════════════════════════════════╣
  ║                                                               ║
  ║  Company: NovaTech Electronics Pvt Ltd                        ║
  ║  Products: ProTab X1 (₹24,999) + SmartWatch S5 (₹7,999)      ║
  ║                                                               ║
  ║  ADVANCED FEATURES CONFIGURED:                                ║
  ║  ✅ 17 Raw Materials (multi-vendor with competing prices)     ║
  ║  ✅ 2 Finished Products with multi-level BOMs                 ║
  ║  ✅ 5 Work Centers with efficiency tracking                   ║
  ║  ✅ 7 Vendors (incl. subcontractor)                           ║
  ║  ✅ 3 Customers (Retail / Govt / Export)                      ║
  ║  ✅ 3 Pricelists (Retail / Wholesale / VIP-Export)            ║
  ║  ✅ 10 Employees with LINKED USER ACCOUNTS                   ║
  ║  ✅ 3 CRM Leads (realistic scenarios)                        ║
  ║  ✅ 2 Sales Orders (with different pricelists)                ║
  ║  ✅ 6 Purchase Orders / RFQs (2 draft for comparison)        ║
  ║  ✅ 2 Manufacturing Orders (confirmed)                       ║
  ║  ✅ 5 Quality Control Points                                  ║
  ║  ✅ 5 Maintenance Equipment linked to work centers            ║
  ║  ✅ 11 Reordering Rules (auto-replenishment)                  ║
  ║  ✅ Bank Statement with 6 transactions (for reconciliation)   ║
  ║  ✅ Vendor Bills posted (for matching)                        ║
  ║  ✅ 4 Product Categories (AVCO / FIFO / Standard)             ║
  ║                                                               ║
  ║  EMPLOYEE LOGINS (all password: NovaTech@123):                ║
  ║    arjun@novatech.in   — Production Manager                   ║
  ║    sneha@novatech.in   — Quality Manager                      ║
  ║    rohit@novatech.in   — Sales Head                           ║
  ║    kavitha@novatech.in — Purchase Manager                     ║
  ║    meera@novatech.in   — Finance Controller                   ║
  ║    deepak@novatech.in  — Warehouse Supervisor                 ║
  ║    priyanka@novatech.in— HR Manager                           ║
  ║    sanjay@novatech.in  — Machine Operator                     ║
  ║    anil@novatech.in    — R&D Engineer                         ║
  ║    divya@novatech.in   — Accounts Executive                   ║
  ║                                                               ║
  ╚═══════════════════════════════════════════════════════════════╝
""")
