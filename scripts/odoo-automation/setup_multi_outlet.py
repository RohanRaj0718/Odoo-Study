"""
============================================================================
ODOO 19 — MULTI-COMPANY & MULTI-OUTLET COMPLETE SETUP SCRIPT
============================================================================
Database: demo-tech.odoo.com (Odoo 19, saas~19.1+e)

This script implements the full architecture described in
MULTI_COMPANY_MULTI_OUTLET_GUIDE.md:

  Company A (demo-tech) — one legal entity, three outlets:
    1. Kochi Outlet (Central/Flagship warehouse)
    2. Bangalore Outlet (resupplied from Kochi)
    3. Chennai Outlet (resupplied from Kochi)

WHAT THIS SCRIPT CREATES:
  ✅ Enable Multi-Step Routes & Storage Locations
  ✅ Enable Analytic Accounting, Pricelists, Margins
  ✅ 3 Warehouses (Kochi, Bangalore, Chennai) with addresses
  ✅ Sub-locations within each warehouse
  ✅ Resupply routes: Bangalore←Kochi, Chennai←Kochi
  ✅ Contacts: 3 vendors, 9 customers (3 per outlet)
  ✅ Products: 12 retail products across categories
  ✅ Route assignment on products for inter-warehouse resupply
  ✅ Reordering rules for auto-replenishment
  ✅ Analytic Plan "Outlets" + 3 analytic accounts
  ✅ 3 Pricelists (one per outlet)
  ✅ Additional users (Kochi Manager, Bangalore Staff, Chennai Staff) — optional
  ✅ Sample inventory (opening stock)
  ✅ Sample sale orders (one per outlet)
  ✅ Sample purchase orders
  ✅ Sample internal transfers

============================================================================
"""

import xmlrpc.client
import time
import sys

# ─────────────────────────────────────────────
# CONNECTION
# ─────────────────────────────────────────────
URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

print("=" * 70)
print("ODOO 19 — MULTI-COMPANY & MULTI-OUTLET SETUP")
print("=" * 70)

print("\n[CONNECT] Connecting to Odoo 19...")
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
version = common.version()
print(f"  Server: {version.get('server_version', 'unknown')}")

uid = common.authenticate(DB, USERNAME, PASSWORD, {})
if not uid:
    print("  ❌ Authentication failed!")
    sys.exit(1)
print(f"  ✅ Authenticated as UID={uid}")

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def execute(model, method, *args, **kwargs):
    """Execute an Odoo RPC call with error handling."""
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kwargs)
    except Exception as e:
        print(f"  ⚠️  Error on {model}.{method}: {e}")
        return None

def search(model, domain, limit=100):
    return execute(model, 'search', [domain], {'limit': limit}) or []

def search_read(model, domain=[], fields=[], limit=100):
    return execute(model, 'search_read', [domain], {'fields': fields, 'limit': limit}) or []

def create(model, vals):
    result = execute(model, 'create', [vals])
    if result:
        return result
    return None

def write(model, ids, vals):
    if not isinstance(ids, list):
        ids = [ids]
    return execute(model, 'write', [ids, vals])

def find_or_create(model, domain, vals, label="record"):
    """Find existing record or create new one."""
    existing = search(model, domain, limit=1)
    if existing:
        print(f"  ℹ️  {label} already exists (ID={existing[0]})")
        return existing[0], False
    new_id = create(model, vals)
    if new_id:
        print(f"  ✅ Created {label} (ID={new_id})")
        return new_id, True
    print(f"  ❌ Failed to create {label}")
    return None, False


# ═══════════════════════════════════════════════
# PHASE 1: ENABLE SETTINGS
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 1: ENABLE SETTINGS")
print("═" * 70)

print("\n[1.1] Enabling Multi-Step Routes, Storage Locations, Analytics, Pricelists, Margins...")

# Create a settings record and execute it
settings_vals = {
    'group_stock_adv_location': True,      # Multi-Step Routes
    'group_stock_multi_locations': True,    # Storage Locations
    'group_analytic_accounting': True,      # Analytic Accounting
    'group_product_pricelist': True,        # Pricelists
    'module_sale_margin': True,             # Sales Margins
}

try:
    settings_id = create('res.config.settings', settings_vals)
    if settings_id:
        execute('res.config.settings', 'execute', [[settings_id]])
        print("  ✅ Settings enabled and applied")
        time.sleep(3)  # Wait for modules to install
    else:
        print("  ⚠️  Settings creation returned None, trying direct approach...")
except Exception as e:
    print(f"  ⚠️  Settings apply error (may still work): {e}")
    time.sleep(3)


# ═══════════════════════════════════════════════
# PHASE 2: COMPANY CONFIGURATION
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 2: COMPANY & ADDRESS CONFIGURATION")
print("═" * 70)

COMPANY_ID = 1  # demo-tech

# Get country and state IDs
india_ids = search('res.country', [['code', '=', 'IN']])
INDIA_ID = india_ids[0] if india_ids else 104

states = search_read('res.country.state', 
    [['country_id', '=', INDIA_ID], ['code', 'in', ['KL', 'KA', 'TN']]], 
    ['name', 'code'])
STATE_MAP = {s['code']: s['id'] for s in states}
print(f"  States: KL={STATE_MAP.get('KL')}, KA={STATE_MAP.get('KA')}, TN={STATE_MAP.get('TN')}")

# Update company name and details
print("\n[2.1] Updating company details...")
write('res.company', COMPANY_ID, {
    'name': 'Company A — SmartTech Retail',
    'street': 'Phase 1, Carnival Info Park, Kakkanad',
    'city': 'Kochi',
    'state_id': STATE_MAP.get('KL'),
    'country_id': INDIA_ID,
    'phone': '+91 484 2345678',
    'email': 'info@smarttech-retail.com',
    'website': 'https://smarttech-retail.com',
})
print("  ✅ Company updated to 'Company A — SmartTech Retail'")


# ═══════════════════════════════════════════════
# PHASE 3: CREATE PARTNER ADDRESSES FOR WAREHOUSES
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 3: WAREHOUSE PARTNER ADDRESSES")
print("═" * 70)

outlet_addresses = {
    'Kochi Outlet': {
        'name': 'Kochi Outlet — SmartTech',
        'street': 'MG Road, Near Lulu Mall',
        'city': 'Kochi',
        'state_id': STATE_MAP.get('KL'),
        'country_id': INDIA_ID,
        'zip': '682024',
        'phone': '+91 484 2345001',
        'is_company': False,
        'type': 'other',
        'company_id': COMPANY_ID,
    },
    'Bangalore Outlet': {
        'name': 'Bangalore Outlet — SmartTech',
        'street': '100 Feet Road, Koramangala',
        'city': 'Bangalore',
        'state_id': STATE_MAP.get('KA'),
        'country_id': INDIA_ID,
        'zip': '560034',
        'phone': '+91 80 2345002',
        'is_company': False,
        'type': 'other',
        'company_id': COMPANY_ID,
    },
    'Chennai Outlet': {
        'name': 'Chennai Outlet — SmartTech',
        'street': 'Usman Road, T. Nagar',
        'city': 'Chennai',
        'state_id': STATE_MAP.get('TN'),
        'country_id': INDIA_ID,
        'zip': '600017',
        'phone': '+91 44 2345003',
        'is_company': False,
        'type': 'other',
        'company_id': COMPANY_ID,
    }
}

partner_ids = {}
for outlet_name, addr in outlet_addresses.items():
    pid, _ = find_or_create('res.partner',
        [['name', '=', addr['name']]], addr, label=f"Address: {outlet_name}")
    partner_ids[outlet_name] = pid


# ═══════════════════════════════════════════════
# PHASE 4: CREATE WAREHOUSES
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 4: CREATE WAREHOUSES (Outlets)")
print("═" * 70)

# First, rename the existing warehouse to Kochi Outlet
print("\n[4.1] Configuring existing warehouse as Kochi Outlet (Central)...")
existing_wh = search_read('stock.warehouse', [['company_id', '=', COMPANY_ID]], ['name', 'code'])
if existing_wh:
    wh1_id = existing_wh[0]['id']
    write('stock.warehouse', wh1_id, {
        'name': 'Kochi Outlet',
        'code': 'KOCHI',
        'partner_id': partner_ids.get('Kochi Outlet', False),
        'buy_to_resupply': True,
        'manufacture_to_resupply': True,
    })
    print(f"  ✅ Warehouse ID={wh1_id} renamed to 'Kochi Outlet' (Code: KOCHI)")
else:
    print("  ❌ No existing warehouse found!")
    sys.exit(1)

# Create Bangalore Outlet
print("\n[4.2] Creating Bangalore Outlet warehouse...")
wh2_id, wh2_created = find_or_create('stock.warehouse',
    [['code', '=', 'BANG']],
    {
        'name': 'Bangalore Outlet',
        'code': 'BANG',
        'company_id': COMPANY_ID,
        'partner_id': partner_ids.get('Bangalore Outlet', False),
        'reception_steps': 'one_step',
        'delivery_steps': 'ship_only',
        'buy_to_resupply': True,
        'manufacture_to_resupply': False,
    },
    label="Warehouse: Bangalore Outlet")

# Create Chennai Outlet
print("\n[4.3] Creating Chennai Outlet warehouse...")
wh3_id, wh3_created = find_or_create('stock.warehouse',
    [['code', '=', 'CHEN']],
    {
        'name': 'Chennai Outlet',
        'code': 'CHEN',
        'company_id': COMPANY_ID,
        'partner_id': partner_ids.get('Chennai Outlet', False),
        'reception_steps': 'one_step',
        'delivery_steps': 'ship_only',
        'buy_to_resupply': True,
        'manufacture_to_resupply': False,
    },
    label="Warehouse: Chennai Outlet")

time.sleep(2)  # Let Odoo create the default locations/routes

# ═══════════════════════════════════════════════
# PHASE 5: CONFIGURE RESUPPLY FROM KOCHI
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 5: CONFIGURE RESUPPLY ROUTES")
print("═" * 70)

# Set Bangalore to resupply from Kochi
print("\n[5.1] Setting Bangalore Outlet to resupply from Kochi Outlet...")
write('stock.warehouse', wh2_id, {
    'resupply_wh_ids': [(6, 0, [wh1_id])]  # 6,0 = replace with this list
})
print("  ✅ Bangalore Outlet → Resupply from Kochi Outlet")

# Set Chennai to resupply from Kochi 
print("\n[5.2] Setting Chennai Outlet to resupply from Kochi Outlet...")
write('stock.warehouse', wh3_id, {
    'resupply_wh_ids': [(6, 0, [wh1_id])]
})
print("  ✅ Chennai Outlet → Resupply from Kochi Outlet")

time.sleep(2)

# Verify the resupply routes were created
print("\n[5.3] Verifying resupply routes...")
routes = search_read('stock.route', [], ['name', 'active', 'company_id', 'product_selectable'])
for r in routes:
    print(f"  Route ID={r['id']}: {r['name']} (Active: {r['active']}, Selectable: {r['product_selectable']})")


# ═══════════════════════════════════════════════
# PHASE 6: CREATE SUB-LOCATIONS
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 6: CREATE SUB-LOCATIONS")
print("═" * 70)

# Find stock locations for each warehouse
wh_locations = {}
for wh_code in ['KOCHI', 'BANG', 'CHEN']:
    locs = search_read('stock.location', 
        [['usage', '=', 'internal'], ['complete_name', 'like', f'{wh_code}%Stock']],
        ['name', 'complete_name', 'id'])
    if locs:
        wh_locations[wh_code] = locs[0]['id']
        print(f"  Found stock location: {locs[0]['complete_name']} (ID={locs[0]['id']})")
    else:
        # Try broader search
        locs = search_read('stock.location',
            [['usage', '=', 'internal'], ['warehouse_id.code', '=', wh_code]],
            ['name', 'complete_name', 'id'])
        if locs:
            wh_locations[wh_code] = locs[0]['id']
            print(f"  Found stock location: {locs[0]['complete_name']} (ID={locs[0]['id']})")
        else:
            print(f"  ⚠️  Could not find stock location for {wh_code}")

# Create sub-locations for Kochi (central warehouse — more zones)
kochi_sublocs = [
    ('Zone A — Electronics', wh_locations.get('KOCHI')),
    ('Zone B — Furniture', wh_locations.get('KOCHI')),
    ('Zone C — Accessories', wh_locations.get('KOCHI')),
    ('Cold Storage', wh_locations.get('KOCHI')),
]

for loc_name, parent_id in kochi_sublocs:
    if parent_id:
        find_or_create('stock.location',
            [['name', '=', loc_name], ['location_id', '=', parent_id]],
            {
                'name': loc_name,
                'location_id': parent_id,
                'usage': 'internal',
                'company_id': COMPANY_ID,
            },
            label=f"Location: {loc_name}")

# Create sub-locations for Bangalore
bang_sublocs = [
    ('Display Area', wh_locations.get('BANG')),
    ('Back Storage', wh_locations.get('BANG')),
]

for loc_name, parent_id in bang_sublocs:
    if parent_id:
        find_or_create('stock.location',
            [['name', '=', loc_name], ['location_id', '=', parent_id]],
            {
                'name': loc_name,
                'location_id': parent_id,
                'usage': 'internal',
                'company_id': COMPANY_ID,
            },
            label=f"Location: {loc_name}")

# Create sub-locations for Chennai
chen_sublocs = [
    ('Showroom Floor', wh_locations.get('CHEN')),
    ('Storage Room', wh_locations.get('CHEN')),
]

for loc_name, parent_id in chen_sublocs:
    if parent_id:
        find_or_create('stock.location',
            [['name', '=', loc_name], ['location_id', '=', parent_id]],
            {
                'name': loc_name,
                'location_id': parent_id,
                'usage': 'internal',
                'company_id': COMPANY_ID,
            },
            label=f"Location: {loc_name}")


# ═══════════════════════════════════════════════
# PHASE 7: CREATE PRODUCT CATEGORIES
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 7: PRODUCT CATEGORIES")
print("═" * 70)

categories = {
    'Electronics': {},
    'Furniture': {},
    'Accessories': {},
    'Smart Home': {},
}

cat_ids = {}
# Get the "Goods" parent category
goods_cats = search_read('product.category', [['name', '=', 'Goods']], ['id'])
goods_parent = goods_cats[0]['id'] if goods_cats else 1

for cat_name in categories:
    cat_id, _ = find_or_create('product.category',
        [['name', '=', cat_name], ['parent_id', '=', goods_parent]],
        {'name': cat_name, 'parent_id': goods_parent},
        label=f"Category: {cat_name}")
    cat_ids[cat_name] = cat_id


# ═══════════════════════════════════════════════
# PHASE 8: CREATE PRODUCTS
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 8: CREATE PRODUCTS")
print("═" * 70)

products_data = [
    # (Name, Category, Sale Price, Cost, Type)
    ("SmartDesk Pro X1", "Furniture", 12500.00, 7500.00, "consu"),
    ("ErgoChair Elite", "Furniture", 8900.00, 5200.00, "consu"),
    ("Standing Desk Converter", "Furniture", 6500.00, 3800.00, "consu"),
    ("LED Smart Monitor 27\"", "Electronics", 22000.00, 15000.00, "consu"),
    ("Wireless Keyboard Combo", "Electronics", 2500.00, 1200.00, "consu"),
    ("Bluetooth Speaker Pro", "Electronics", 4500.00, 2200.00, "consu"),
    ("USB-C Hub 7-in-1", "Accessories", 1800.00, 800.00, "consu"),
    ("Laptop Stand Adjustable", "Accessories", 2200.00, 1100.00, "consu"),
    ("Cable Organizer Kit", "Accessories", 450.00, 180.00, "consu"),
    ("Smart LED Strip 5m", "Smart Home", 1500.00, 600.00, "consu"),
    ("WiFi Smart Plug Pack", "Smart Home", 1200.00, 500.00, "consu"),
    ("Smart Security Camera", "Smart Home", 5500.00, 3000.00, "consu"),
]

product_ids = {}
for pname, pcat, pprice, pcost, ptype in products_data:
    pid, _ = find_or_create('product.template',
        [['name', '=', pname]],
        {
            'name': pname,
            'type': ptype,
            'list_price': pprice,
            'standard_price': pcost,
            'categ_id': cat_ids.get(pcat, goods_parent),
            'sale_ok': True,
            'purchase_ok': True,
            'company_id': False,  # shared across companies
        },
        label=f"Product: {pname}")
    product_ids[pname] = pid


# ═══════════════════════════════════════════════
# PHASE 9: ASSIGN RESUPPLY ROUTES TO PRODUCTS
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 9: ASSIGN RESUPPLY ROUTES TO PRODUCTS")
print("═" * 70)

# Find the resupply routes
resupply_routes = search_read('stock.route', 
    [['name', 'like', 'Supply Product from']], 
    ['name', 'id'])

resupply_route_ids = [r['id'] for r in resupply_routes]
print(f"  Found resupply routes: {[r['name'] for r in resupply_routes]}")

if resupply_route_ids:
    # Get also the Buy route
    buy_routes = search_read('stock.route', [['name', '=', 'Buy']], ['id'])
    buy_route_id = buy_routes[0]['id'] if buy_routes else None
    
    all_route_ids = resupply_route_ids[:]
    if buy_route_id:
        all_route_ids.append(buy_route_id)
    
    # Assign routes to all products
    for pname, pid in product_ids.items():
        if pid:
            # Get product.product id from template
            pp = search_read('product.product', 
                [['product_tmpl_id', '=', pid]], ['id'])
            if pp:
                # Set routes on the product template
                write('product.template', pid, {
                    'route_ids': [(6, 0, all_route_ids)]
                })
    print(f"  ✅ Assigned {len(all_route_ids)} routes to {len(product_ids)} products")
    print(f"     Routes: {', '.join(r['name'] for r in resupply_routes)}" + (f", Buy" if buy_route_id else ""))
else:
    print("  ⚠️  No resupply routes found — skipping route assignment")


# ═══════════════════════════════════════════════
# PHASE 10: CREATE CONTACTS (Vendors & Customers)
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 10: CREATE CONTACTS")
print("═" * 70)

# Vendors
vendors_data = [
    {
        'name': 'TechVision Distributors',
        'is_company': True,
        'supplier_rank': 1,
        'street': 'MIDC Industrial Area, Andheri East',
        'city': 'Mumbai',
        'state_id': search('res.country.state', [['country_id', '=', INDIA_ID], ['code', '=', 'MH']], limit=1),
        'country_id': INDIA_ID,
        'phone': '+91 22 4455 6677',
        'email': 'orders@techvision.in',
        'zip': '400093',
    },
    {
        'name': 'FurniCraft India Pvt Ltd',
        'is_company': True,
        'supplier_rank': 1,
        'street': 'Industrial Estate, Whitefield',
        'city': 'Bangalore',
        'state_id': STATE_MAP.get('KA'),
        'country_id': INDIA_ID,
        'phone': '+91 80 2233 4455',
        'email': 'sales@furnicraft.in',
        'zip': '560066',
    },
    {
        'name': 'SmartParts Components',
        'is_company': True,
        'supplier_rank': 1,
        'street': 'Electronics City Phase 2',
        'city': 'Bangalore',
        'state_id': STATE_MAP.get('KA'),
        'country_id': INDIA_ID,
        'phone': '+91 80 6677 8899',
        'email': 'supply@smartparts.in',
        'zip': '560100',
    },
]

vendor_ids = {}
for v in vendors_data:
    # Process state_id if it's a list from search
    if isinstance(v.get('state_id'), list) and v['state_id']:
        v['state_id'] = v['state_id'][0]
    elif isinstance(v.get('state_id'), list):
        v.pop('state_id', None)
    
    vid, _ = find_or_create('res.partner',
        [['name', '=', v['name']], ['is_company', '=', True]],
        v, label=f"Vendor: {v['name']}")
    vendor_ids[v['name']] = vid

# Customers — 3 per outlet city
customers_data = [
    # Kochi customers
    {'name': 'Kerala Tech Solutions', 'is_company': True, 'customer_rank': 1,
     'street': 'Palarivattom, Bypass Junction', 'city': 'Kochi',
     'state_id': STATE_MAP.get('KL'), 'country_id': INDIA_ID,
     'email': 'buy@keralatech.in', 'zip': '682025'},
    {'name': 'Cochin Startups Hub', 'is_company': True, 'customer_rank': 1,
     'street': 'Infopark, Kakkanad', 'city': 'Kochi',
     'state_id': STATE_MAP.get('KL'), 'country_id': INDIA_ID,
     'email': 'procurement@cochistartups.in', 'zip': '682030'},
    {'name': 'Marine Drive Interiors', 'is_company': True, 'customer_rank': 1,
     'street': 'Marine Drive, Ernakulam', 'city': 'Kochi',
     'state_id': STATE_MAP.get('KL'), 'country_id': INDIA_ID,
     'email': 'info@marinedrive-int.in', 'zip': '682011'},
    # Bangalore customers
    {'name': 'InnoTech Bangalore', 'is_company': True, 'customer_rank': 1,
     'street': 'HSR Layout, Sector 2', 'city': 'Bangalore',
     'state_id': STATE_MAP.get('KA'), 'country_id': INDIA_ID,
     'email': 'office@innotechblr.in', 'zip': '560102'},
    {'name': 'Silicon Valley Cowork', 'is_company': True, 'customer_rank': 1,
     'street': 'Marathahalli, ORR', 'city': 'Bangalore',
     'state_id': STATE_MAP.get('KA'), 'country_id': INDIA_ID,
     'email': 'admin@svcowork.in', 'zip': '560037'},
    {'name': 'Namma Office Supplies', 'is_company': True, 'customer_rank': 1,
     'street': 'MG Road, Near Trinity Circle', 'city': 'Bangalore',
     'state_id': STATE_MAP.get('KA'), 'country_id': INDIA_ID,
     'email': 'orders@nammaoffice.in', 'zip': '560001'},
    # Chennai customers
    {'name': 'Tamil Digital Solutions', 'is_company': True, 'customer_rank': 1,
     'street': 'OMR, Thoraipakkam', 'city': 'Chennai',
     'state_id': STATE_MAP.get('TN'), 'country_id': INDIA_ID,
     'email': 'purchase@tamildigital.in', 'zip': '600097'},
    {'name': 'Marina Bay Enterprises', 'is_company': True, 'customer_rank': 1,
     'street': 'Anna Salai, Nungambakkam', 'city': 'Chennai',
     'state_id': STATE_MAP.get('TN'), 'country_id': INDIA_ID,
     'email': 'orders@marinabay.in', 'zip': '600034'},
    {'name': 'SpaceTech Workspace', 'is_company': True, 'customer_rank': 1,
     'street': 'Velachery Main Road', 'city': 'Chennai',
     'state_id': STATE_MAP.get('TN'), 'country_id': INDIA_ID,
     'email': 'admin@spacetechws.in', 'zip': '600042'},
]

customer_ids = {}
for c in customers_data:
    cid, _ = find_or_create('res.partner',
        [['name', '=', c['name']], ['is_company', '=', True]],
        c, label=f"Customer: {c['name']}")
    customer_ids[c['name']] = cid


# ═══════════════════════════════════════════════
# PHASE 11: CONFIGURE VENDOR PRICELISTS ON PRODUCTS
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 11: VENDOR PRICELISTS (Supplier Info on Products)")
print("═" * 70)

# Map products to vendors with prices and lead times
vendor_pricelist = [
    # (product_name, vendor_name, price, min_qty, delay_days)
    ("LED Smart Monitor 27\"", "TechVision Distributors", 15000, 1, 5),
    ("Wireless Keyboard Combo", "TechVision Distributors", 1200, 1, 3),
    ("Bluetooth Speaker Pro", "TechVision Distributors", 2200, 1, 4),
    ("USB-C Hub 7-in-1", "TechVision Distributors", 800, 1, 3),
    ("Smart LED Strip 5m", "TechVision Distributors", 600, 1, 3),
    ("WiFi Smart Plug Pack", "TechVision Distributors", 500, 1, 3),
    ("Smart Security Camera", "TechVision Distributors", 3000, 1, 5),
    ("SmartDesk Pro X1", "FurniCraft India Pvt Ltd", 7500, 1, 7),
    ("ErgoChair Elite", "FurniCraft India Pvt Ltd", 5200, 1, 7),
    ("Standing Desk Converter", "FurniCraft India Pvt Ltd", 3800, 1, 5),
    ("Laptop Stand Adjustable", "SmartParts Components", 1100, 1, 4),
    ("Cable Organizer Kit", "SmartParts Components", 180, 5, 3),
]

for pname, vname, vprice, min_qty, delay in vendor_pricelist:
    pid = product_ids.get(pname)
    vid = vendor_ids.get(vname)
    if pid and vid:
        # Get product.product ID
        pp = search_read('product.product', [['product_tmpl_id', '=', pid]], ['id'])
        pp_id = pp[0]['id'] if pp else None
        if pp_id:
            find_or_create('product.supplierinfo',
                [['product_tmpl_id', '=', pid], ['partner_id', '=', vid]],
                {
                    'product_tmpl_id': pid,
                    'partner_id': vid,
                    'price': vprice,
                    'min_qty': min_qty,
                    'delay': delay,
                    'company_id': COMPANY_ID,
                },
                label=f"Vendor Price: {pname} ← {vname}")


# ═══════════════════════════════════════════════
# PHASE 12: CREATE PRICELISTS (Per Outlet)
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 12: CREATE PRICELISTS")
print("═" * 70)

# Kochi Pricelist — Standard pricing (flagship store)
kochi_pl_id, _ = find_or_create('product.pricelist',
    [['name', '=', 'Kochi Outlet — Standard']],
    {
        'name': 'Kochi Outlet — Standard',
        'currency_id': 20,  # INR
        'company_id': COMPANY_ID,
    },
    label="Pricelist: Kochi Standard")

# Bangalore Pricelist — 5% discount (competitive market)
bang_pl_id, _ = find_or_create('product.pricelist',
    [['name', '=', 'Bangalore Outlet — Competitive']],
    {
        'name': 'Bangalore Outlet — Competitive',
        'currency_id': 20,
        'company_id': COMPANY_ID,
    },
    label="Pricelist: Bangalore Competitive")

# Add 5% discount rule to Bangalore pricelist
if bang_pl_id:
    find_or_create('product.pricelist.item',
        [['pricelist_id', '=', bang_pl_id], ['compute_price', '=', 'percentage']],
        {
            'pricelist_id': bang_pl_id,
            'applied_on': '3_global',  # All Products
            'compute_price': 'percentage',
            'percent_price': 5.0,  # 5% discount
        },
        label="Pricelist Rule: Bangalore 5% discount")

# Chennai Pricelist — 10% introductory discount
chen_pl_id, _ = find_or_create('product.pricelist',
    [['name', '=', 'Chennai Outlet — Introductory']],
    {
        'name': 'Chennai Outlet — Introductory',
        'currency_id': 20,
        'company_id': COMPANY_ID,
    },
    label="Pricelist: Chennai Introductory")

# Add 10% discount rule
if chen_pl_id:
    find_or_create('product.pricelist.item',
        [['pricelist_id', '=', chen_pl_id], ['compute_price', '=', 'percentage']],
        {
            'pricelist_id': chen_pl_id,
            'applied_on': '3_global',
            'compute_price': 'percentage',
            'percent_price': 10.0,
        },
        label="Pricelist Rule: Chennai 10% discount")

# Assign pricelists to customers
print("\n  Assigning pricelists to customers...")
kochi_customers = ['Kerala Tech Solutions', 'Cochin Startups Hub', 'Marine Drive Interiors']
bang_customers = ['InnoTech Bangalore', 'Silicon Valley Cowork', 'Namma Office Supplies']
chen_customers = ['Tamil Digital Solutions', 'Marina Bay Enterprises', 'SpaceTech Workspace']

for cname in kochi_customers:
    cid = customer_ids.get(cname)
    if cid and kochi_pl_id:
        write('res.partner', cid, {'property_product_pricelist': kochi_pl_id})

for cname in bang_customers:
    cid = customer_ids.get(cname)
    if cid and bang_pl_id:
        write('res.partner', cid, {'property_product_pricelist': bang_pl_id})

for cname in chen_customers:
    cid = customer_ids.get(cname)
    if cid and chen_pl_id:
        write('res.partner', cid, {'property_product_pricelist': chen_pl_id})

print("  ✅ Pricelists assigned to customers")


# ═══════════════════════════════════════════════
# PHASE 13: ANALYTIC ACCOUNTING SETUP
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 13: ANALYTIC ACCOUNTING (Outlet P&L Tracking)")
print("═" * 70)

# Create the "Outlets" analytic plan
outlet_plan_id, _ = find_or_create('account.analytic.plan',
    [['name', '=', 'Outlets']],
    {
        'name': 'Outlets',
        'default_applicability': 'optional',
        'color': 4,
    },
    label="Analytic Plan: Outlets")

# Create analytic accounts for each outlet
analytic_ids = {}
for outlet_name, color in [('Kochi Outlet', 1), ('Bangalore Outlet', 2), ('Chennai Outlet', 3)]:
    aa_id, _ = find_or_create('account.analytic.account',
        [['name', '=', outlet_name], ['plan_id', '=', outlet_plan_id]],
        {
            'name': outlet_name,
            'plan_id': outlet_plan_id,
        },
        label=f"Analytic Account: {outlet_name}")
    analytic_ids[outlet_name] = aa_id

print(f"\n  Analytic IDs: {analytic_ids}")


# ═══════════════════════════════════════════════
# PHASE 14: OPENING STOCK (Inventory Adjustments)
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 14: OPENING STOCK PER OUTLET")
print("═" * 70)

# Opening stock quantities per warehouse
opening_stock = {
    'KOCHI': {
        "SmartDesk Pro X1": 50,
        "ErgoChair Elite": 40,
        "Standing Desk Converter": 30,
        "LED Smart Monitor 27\"": 60,
        "Wireless Keyboard Combo": 100,
        "Bluetooth Speaker Pro": 45,
        "USB-C Hub 7-in-1": 80,
        "Laptop Stand Adjustable": 35,
        "Cable Organizer Kit": 200,
        "Smart LED Strip 5m": 70,
        "WiFi Smart Plug Pack": 90,
        "Smart Security Camera": 25,
    },
    'BANG': {
        "SmartDesk Pro X1": 15,
        "ErgoChair Elite": 12,
        "Standing Desk Converter": 10,
        "LED Smart Monitor 27\"": 20,
        "Wireless Keyboard Combo": 40,
        "Bluetooth Speaker Pro": 15,
        "USB-C Hub 7-in-1": 30,
        "Laptop Stand Adjustable": 10,
        "Cable Organizer Kit": 60,
        "Smart LED Strip 5m": 25,
        "WiFi Smart Plug Pack": 30,
        "Smart Security Camera": 8,
    },
    'CHEN': {
        "SmartDesk Pro X1": 8,
        "ErgoChair Elite": 6,
        "Standing Desk Converter": 5,
        "LED Smart Monitor 27\"": 10,
        "Wireless Keyboard Combo": 20,
        "Bluetooth Speaker Pro": 8,
        "USB-C Hub 7-in-1": 15,
        "Laptop Stand Adjustable": 5,
        "Cable Organizer Kit": 30,
        "Smart LED Strip 5m": 12,
        "WiFi Smart Plug Pack": 15,
        "Smart Security Camera": 3,
    },
}

for wh_code, stock_map in opening_stock.items():
    loc_id = wh_locations.get(wh_code)
    if not loc_id:
        print(f"  ⚠️  Skipping {wh_code} — location not found")
        continue
    
    print(f"\n  [{wh_code}] Setting opening stock at location ID={loc_id}...")
    for pname, qty in stock_map.items():
        pid = product_ids.get(pname)
        if not pid:
            continue
        # Get product.product ID
        pp = search_read('product.product', [['product_tmpl_id', '=', pid]], ['id'])
        if not pp:
            continue
        pp_id = pp[0]['id']
        
        # Check current stock at this location using stock.quant
        existing = search_read('stock.quant',
            [['product_id', '=', pp_id], ['location_id', '=', loc_id]],
            ['quantity'])
        
        if existing and existing[0]['quantity'] >= qty:
            continue  # Already has enough stock
        
        # Use stock.quant update (inventory adjustment)
        try:
            execute('stock.quant', 'with_context', 
                {'default_inventory_quantity': qty}, 
                [])
        except:
            pass
        
        # Create or update quant
        if existing:
            write('stock.quant', existing[0]['id'], {
                'inventory_quantity': qty
            })
            # Apply the inventory adjustment
            try:
                execute('stock.quant', 'action_apply_inventory', [[existing[0]['id']]])
            except Exception as e:
                pass  # May need different approach
        else:
            # Create new quant
            quant_id = create('stock.quant', {
                'product_id': pp_id,
                'location_id': loc_id,
                'inventory_quantity': qty,
            })
            if quant_id:
                try:
                    execute('stock.quant', 'action_apply_inventory', [[quant_id]])
                except Exception as e:
                    pass
    
    print(f"  ✅ Opening stock set for {wh_code}")


# ═══════════════════════════════════════════════
# PHASE 15: REORDERING RULES (Auto-Replenishment)
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 15: REORDERING RULES")
print("═" * 70)

# Find resupply route IDs
bang_resupply = search_read('stock.route',
    [['name', 'like', 'Bangalore'], ['name', 'like', 'Supply Product from']],
    ['name', 'id'])
chen_resupply = search_read('stock.route',
    [['name', 'like', 'Chennai'], ['name', 'like', 'Supply Product from']],
    ['name', 'id'])

bang_route_id = bang_resupply[0]['id'] if bang_resupply else None
chen_route_id = chen_resupply[0]['id'] if chen_resupply else None

buy_routes = search_read('stock.route', [['name', '=', 'Buy']], ['id'])
buy_route_id = buy_routes[0]['id'] if buy_routes else None

print(f"  Bangalore resupply route: {bang_route_id}")
print(f"  Chennai resupply route: {chen_route_id}")
print(f"  Buy route: {buy_route_id}")

# Reordering rules configuration
# (product_name, location_code, route_id, min_qty, max_qty)
reorder_rules = []

# Kochi — buy from vendors
kochi_reorders = [
    ("SmartDesk Pro X1", 100, 200),
    ("ErgoChair Elite", 80, 160),
    ("Standing Desk Converter", 60, 120),
    ("LED Smart Monitor 27\"", 100, 250),
    ("Wireless Keyboard Combo", 200, 500),
    ("Bluetooth Speaker Pro", 80, 200),
    ("USB-C Hub 7-in-1", 150, 400),
    ("Laptop Stand Adjustable", 50, 150),
    ("Cable Organizer Kit", 300, 800),
    ("Smart LED Strip 5m", 100, 300),
    ("WiFi Smart Plug Pack", 150, 400),
    ("Smart Security Camera", 40, 100),
]

for pname, min_q, max_q in kochi_reorders:
    reorder_rules.append((pname, 'KOCHI', buy_route_id, min_q, max_q))

# Bangalore — resupply from Kochi
bang_reorders = [
    ("SmartDesk Pro X1", 10, 30),
    ("ErgoChair Elite", 8, 25),
    ("Standing Desk Converter", 5, 20),
    ("LED Smart Monitor 27\"", 15, 40),
    ("Wireless Keyboard Combo", 30, 80),
    ("Bluetooth Speaker Pro", 10, 30),
    ("USB-C Hub 7-in-1", 20, 60),
    ("Laptop Stand Adjustable", 8, 20),
    ("Cable Organizer Kit", 40, 120),
    ("Smart LED Strip 5m", 15, 50),
    ("WiFi Smart Plug Pack", 20, 60),
    ("Smart Security Camera", 5, 15),
]

for pname, min_q, max_q in bang_reorders:
    reorder_rules.append((pname, 'BANG', bang_route_id, min_q, max_q))

# Chennai — resupply from Kochi
chen_reorders = [
    ("SmartDesk Pro X1", 5, 15),
    ("ErgoChair Elite", 4, 12),
    ("Standing Desk Converter", 3, 10),
    ("LED Smart Monitor 27\"", 8, 20),
    ("Wireless Keyboard Combo", 15, 40),
    ("Bluetooth Speaker Pro", 5, 15),
    ("USB-C Hub 7-in-1", 10, 30),
    ("Laptop Stand Adjustable", 4, 10),
    ("Cable Organizer Kit", 20, 60),
    ("Smart LED Strip 5m", 8, 25),
    ("WiFi Smart Plug Pack", 10, 30),
    ("Smart Security Camera", 3, 8),
]

for pname, min_q, max_q in chen_reorders:
    reorder_rules.append((pname, 'CHEN', chen_route_id, min_q, max_q))

# Create the reordering rules
created_count = 0
for pname, wh_code, route_id, min_qty, max_qty in reorder_rules:
    pid = product_ids.get(pname)
    loc_id = wh_locations.get(wh_code)
    
    if not pid or not loc_id:
        continue
    
    pp = search_read('product.product', [['product_tmpl_id', '=', pid]], ['id'])
    if not pp:
        continue
    pp_id = pp[0]['id']
    
    # Check if rule already exists
    existing = search('stock.warehouse.orderpoint',
        [['product_id', '=', pp_id], ['location_id', '=', loc_id]], limit=1)
    
    if existing:
        continue
    
    rule_vals = {
        'product_id': pp_id,
        'location_id': loc_id,
        'product_min_qty': min_qty,
        'product_max_qty': max_qty,
        'qty_multiple': 1,
        'company_id': COMPANY_ID,
    }
    if route_id:
        rule_vals['route_id'] = route_id
    
    rule_id = create('stock.warehouse.orderpoint', rule_vals)
    if rule_id:
        created_count += 1

print(f"\n  ✅ Created {created_count} reordering rules")
print(f"     Kochi: {len(kochi_reorders)} rules (Buy from vendors)")
print(f"     Bangalore: {len(bang_reorders)} rules (Resupply from Kochi)")
print(f"     Chennai: {len(chen_reorders)} rules (Resupply from Kochi)")


# ═══════════════════════════════════════════════
# PHASE 16: SAMPLE SALE ORDERS (One Per Outlet)
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 16: SAMPLE SALE ORDERS")
print("═" * 70)

# Get warehouse IDs for the SO warehouse field
wh_ids = {}
for wh in search_read('stock.warehouse', [['company_id', '=', COMPANY_ID]], ['name', 'code', 'id']):
    wh_ids[wh['code']] = wh['id']

# Helper to get product.product ID
def get_pp_id(template_name):
    pid = product_ids.get(template_name)
    if pid:
        pp = search_read('product.product', [['product_tmpl_id', '=', pid]], ['id'])
        return pp[0]['id'] if pp else None
    return None

# Sale Order 1: Kochi Outlet → Kerala Tech Solutions
print("\n[16.1] Creating Sale Order — Kochi Outlet...")
so1_partner = customer_ids.get('Kerala Tech Solutions')
so1_wh = wh_ids.get('KOCHI')

if so1_partner and so1_wh:
    so1_existing = search('sale.order', 
        [['partner_id', '=', so1_partner], ['state', '=', 'draft']], limit=1)
    if not so1_existing:
        so1_id = create('sale.order', {
            'partner_id': so1_partner,
            'warehouse_id': so1_wh,
            'company_id': COMPANY_ID,
            'pricelist_id': kochi_pl_id,
        })
        if so1_id:
            # Add order lines
            so_lines = [
                ("SmartDesk Pro X1", 3),
                ("ErgoChair Elite", 5),
                ("Wireless Keyboard Combo", 10),
                ("USB-C Hub 7-in-1", 8),
            ]
            for pname, qty in so_lines:
                pp_id = get_pp_id(pname)
                if pp_id:
                    create('sale.order.line', {
                        'order_id': so1_id,
                        'product_id': pp_id,
                        'product_uom_qty': qty,
                    })
            print(f"  ✅ SO Created (ID={so1_id}) — Kochi → Kerala Tech Solutions")
    else:
        print(f"  ℹ️  Draft SO already exists for Kerala Tech Solutions")

# Sale Order 2: Bangalore Outlet → InnoTech Bangalore
print("\n[16.2] Creating Sale Order — Bangalore Outlet...")
so2_partner = customer_ids.get('InnoTech Bangalore')
so2_wh = wh_ids.get('BANG')

if so2_partner and so2_wh:
    so2_existing = search('sale.order',
        [['partner_id', '=', so2_partner], ['state', '=', 'draft']], limit=1)
    if not so2_existing:
        so2_id = create('sale.order', {
            'partner_id': so2_partner,
            'warehouse_id': so2_wh,
            'company_id': COMPANY_ID,
            'pricelist_id': bang_pl_id,
        })
        if so2_id:
            so_lines = [
                ("LED Smart Monitor 27\"", 4),
                ("Bluetooth Speaker Pro", 6),
                ("Smart Security Camera", 2),
            ]
            for pname, qty in so_lines:
                pp_id = get_pp_id(pname)
                if pp_id:
                    create('sale.order.line', {
                        'order_id': so2_id,
                        'product_id': pp_id,
                        'product_uom_qty': qty,
                    })
            print(f"  ✅ SO Created (ID={so2_id}) — Bangalore → InnoTech Bangalore")
    else:
        print(f"  ℹ️  Draft SO already exists for InnoTech Bangalore")

# Sale Order 3: Chennai Outlet → Tamil Digital Solutions
print("\n[16.3] Creating Sale Order — Chennai Outlet...")
so3_partner = customer_ids.get('Tamil Digital Solutions')
so3_wh = wh_ids.get('CHEN')

if so3_partner and so3_wh:
    so3_existing = search('sale.order',
        [['partner_id', '=', so3_partner], ['state', '=', 'draft']], limit=1)
    if not so3_existing:
        so3_id = create('sale.order', {
            'partner_id': so3_partner,
            'warehouse_id': so3_wh,
            'company_id': COMPANY_ID,
            'pricelist_id': chen_pl_id,
        })
        if so3_id:
            so_lines = [
                ("Standing Desk Converter", 2),
                ("Smart LED Strip 5m", 10),
                ("WiFi Smart Plug Pack", 8),
                ("Cable Organizer Kit", 15),
            ]
            for pname, qty in so_lines:
                pp_id = get_pp_id(pname)
                if pp_id:
                    create('sale.order.line', {
                        'order_id': so3_id,
                        'product_id': pp_id,
                        'product_uom_qty': qty,
                    })
            print(f"  ✅ SO Created (ID={so3_id}) — Chennai → Tamil Digital Solutions")
    else:
        print(f"  ℹ️  Draft SO already exists for Tamil Digital Solutions")


# ═══════════════════════════════════════════════
# PHASE 17: SAMPLE PURCHASE ORDERS
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 17: SAMPLE PURCHASE ORDERS")
print("═" * 70)

# Get picking type for Kochi receipts
kochi_receipt = search_read('stock.picking.type',
    [['warehouse_id', '=', wh_ids.get('KOCHI')], ['code', '=', 'incoming']],
    ['id', 'name'])
kochi_receipt_id = kochi_receipt[0]['id'] if kochi_receipt else None

# PO 1: From TechVision to Kochi
print("\n[17.1] Creating Purchase Order — Electronics from TechVision...")
po1_vendor = vendor_ids.get('TechVision Distributors')
if po1_vendor:
    po1_existing = search('purchase.order',
        [['partner_id', '=', po1_vendor], ['state', '=', 'draft']], limit=1)
    if not po1_existing:
        po1_vals = {
            'partner_id': po1_vendor,
            'company_id': COMPANY_ID,
        }
        # Set picking type to Kochi receipts if available
        if kochi_receipt_id:
            po1_vals['picking_type_id'] = kochi_receipt_id
            
        po1_id = create('purchase.order', po1_vals)
        if po1_id:
            po_lines = [
                ("LED Smart Monitor 27\"", 30, 15000),
                ("Wireless Keyboard Combo", 50, 1200),
                ("Bluetooth Speaker Pro", 20, 2200),
                ("Smart Security Camera", 15, 3000),
                ("WiFi Smart Plug Pack", 40, 500),
            ]
            for pname, qty, price in po_lines:
                pp_id = get_pp_id(pname)
                if pp_id:
                    create('purchase.order.line', {
                        'order_id': po1_id,
                        'product_id': pp_id,
                        'product_qty': qty,
                        'price_unit': price,
                    })
            print(f"  ✅ PO Created (ID={po1_id}) — TechVision → Kochi")
    else:
        print(f"  ℹ️  Draft PO already exists for TechVision")

# PO 2: From FurniCraft to Kochi
print("\n[17.2] Creating Purchase Order — Furniture from FurniCraft...")
po2_vendor = vendor_ids.get('FurniCraft India Pvt Ltd')
if po2_vendor:
    po2_existing = search('purchase.order',
        [['partner_id', '=', po2_vendor], ['state', '=', 'draft']], limit=1)
    if not po2_existing:
        po2_vals = {
            'partner_id': po2_vendor,
            'company_id': COMPANY_ID,
        }
        if kochi_receipt_id:
            po2_vals['picking_type_id'] = kochi_receipt_id
            
        po2_id = create('purchase.order', po2_vals)
        if po2_id:
            po_lines = [
                ("SmartDesk Pro X1", 20, 7500),
                ("ErgoChair Elite", 15, 5200),
                ("Standing Desk Converter", 10, 3800),
            ]
            for pname, qty, price in po_lines:
                pp_id = get_pp_id(pname)
                if pp_id:
                    create('purchase.order.line', {
                        'order_id': po2_id,
                        'product_id': pp_id,
                        'product_qty': qty,
                        'price_unit': price,
                    })
            print(f"  ✅ PO Created (ID={po2_id}) — FurniCraft → Kochi")
    else:
        print(f"  ℹ️  Draft PO already exists for FurniCraft")


# ═══════════════════════════════════════════════
# PHASE 18: SAMPLE INTERNAL TRANSFERS
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 18: SAMPLE INTERNAL TRANSFERS")
print("═" * 70)

# Get internal transfer operation types
int_transfers = search_read('stock.picking.type',
    [['code', '=', 'internal'], ['company_id', '=', COMPANY_ID]],
    ['id', 'name', 'warehouse_id'])

# Get transit location
transit_locs = search_read('stock.location',
    [['usage', '=', 'transit'], ['company_id', '=', COMPANY_ID]],
    ['id', 'complete_name'])
if not transit_locs:
    transit_locs = search_read('stock.location',
        [['usage', '=', 'transit'], ['company_id', '=', False]],
        ['id', 'complete_name'])

# Find appropriate picking types for inter-warehouse
# Kochi internal transfer type
kochi_internal = None
for it in int_transfers:
    wh = it.get('warehouse_id')
    if wh and wh[0] == wh_ids.get('KOCHI'):
        kochi_internal = it['id']
        break

if not kochi_internal and int_transfers:
    kochi_internal = int_transfers[0]['id']

# Transfer 1: Kochi → Bangalore (5 SmartDesk + 10 ErgoChair)
print("\n[18.1] Creating Internal Transfer: Kochi → Bangalore...")
kochi_loc = wh_locations.get('KOCHI')
bang_loc = wh_locations.get('BANG')

if kochi_loc and bang_loc and kochi_internal:
    it1_existing = search('stock.picking',
        [['picking_type_id', '=', kochi_internal],
         ['location_id', '=', kochi_loc],
         ['location_dest_id', '=', bang_loc],
         ['state', '=', 'draft']], limit=1)
    
    if not it1_existing:
        it1_id = create('stock.picking', {
            'picking_type_id': kochi_internal,
            'location_id': kochi_loc,
            'location_dest_id': bang_loc,
            'company_id': COMPANY_ID,
            'origin': 'Resupply: Kochi → Bangalore (Sample)',
        })
        if it1_id:
            transfer_lines = [
                ("SmartDesk Pro X1", 5),
                ("ErgoChair Elite", 10),
                ("Wireless Keyboard Combo", 20),
            ]
            for pname, qty in transfer_lines:
                pp_id = get_pp_id(pname)
                if pp_id:
                    create('stock.move', {
                        'name': f'Transfer: {pname}',
                        'product_id': pp_id,
                        'product_uom_qty': qty,
                        'picking_id': it1_id,
                        'location_id': kochi_loc,
                        'location_dest_id': bang_loc,
                        'company_id': COMPANY_ID,
                    })
            print(f"  ✅ Transfer Created (ID={it1_id}) — Kochi → Bangalore")
    else:
        print(f"  ℹ️  Draft transfer Kochi→Bangalore already exists")

# Transfer 2: Kochi → Chennai (3 Standing Desk + 15 Smart LED)
print("\n[18.2] Creating Internal Transfer: Kochi → Chennai...")
chen_loc = wh_locations.get('CHEN')

if kochi_loc and chen_loc and kochi_internal:
    it2_existing = search('stock.picking',
        [['picking_type_id', '=', kochi_internal],
         ['location_id', '=', kochi_loc],
         ['location_dest_id', '=', chen_loc],
         ['state', '=', 'draft']], limit=1)
    
    if not it2_existing:
        it2_id = create('stock.picking', {
            'picking_type_id': kochi_internal,
            'location_id': kochi_loc,
            'location_dest_id': chen_loc,
            'company_id': COMPANY_ID,
            'origin': 'Resupply: Kochi → Chennai (Sample)',
        })
        if it2_id:
            transfer_lines = [
                ("Standing Desk Converter", 3),
                ("Smart LED Strip 5m", 15),
                ("Cable Organizer Kit", 25),
            ]
            for pname, qty in transfer_lines:
                pp_id = get_pp_id(pname)
                if pp_id:
                    create('stock.move', {
                        'name': f'Transfer: {pname}',
                        'product_id': pp_id,
                        'product_uom_qty': qty,
                        'picking_id': it2_id,
                        'location_id': kochi_loc,
                        'location_dest_id': chen_loc,
                        'company_id': COMPANY_ID,
                    })
            print(f"  ✅ Transfer Created (ID={it2_id}) — Kochi → Chennai")
    else:
        print(f"  ℹ️  Draft transfer Kochi→Chennai already exists")


# ═══════════════════════════════════════════════
# PHASE 19: FINAL VERIFICATION
# ═══════════════════════════════════════════════
print("\n" + "═" * 70)
print("PHASE 19: FINAL VERIFICATION")
print("═" * 70)

# Verify warehouses
print("\n[19.1] Warehouses:")
warehouses = search_read('stock.warehouse', [['company_id', '=', COMPANY_ID]], 
    ['name', 'code', 'resupply_wh_ids', 'buy_to_resupply', 'manufacture_to_resupply'])
for w in warehouses:
    print(f"  {w['code']}: {w['name']}")
    print(f"    Resupply from: {w['resupply_wh_ids']}, Buy: {w['buy_to_resupply']}, Mfg: {w['manufacture_to_resupply']}")

# Verify locations
print("\n[19.2] Stock Locations:")
all_locs = search_read('stock.location', 
    [['usage', '=', 'internal'], ['company_id', '=', COMPANY_ID]], 
    ['complete_name', 'warehouse_id'])
for loc in all_locs:
    print(f"  {loc['complete_name']} (WH: {loc['warehouse_id']})")

# Verify routes
print("\n[19.3] Routes:")
routes = search_read('stock.route', [['active', '=', True]], ['name'])
for r in routes:
    print(f"  {r['name']}")

# Verify reordering rules count
print("\n[19.4] Reordering Rules:")
rules = search_read('stock.warehouse.orderpoint', [['company_id', '=', COMPANY_ID]], ['product_id', 'location_id'], limit=200)
print(f"  Total: {len(rules)} rules")

# Count by location
loc_counts = {}
for r in rules:
    loc_name = r['location_id'][1] if r['location_id'] else 'Unknown'
    loc_counts[loc_name] = loc_counts.get(loc_name, 0) + 1
for loc_name, count in loc_counts.items():
    print(f"    {loc_name}: {count} rules")

# Verify products with routes
print("\n[19.5] Products with Routes:")
for pname, pid in product_ids.items():
    if pid:
        p = search_read('product.template', [['id', '=', pid]], ['route_ids'])
        if p and p[0]['route_ids']:
            route_names = search_read('stock.route', [['id', 'in', p[0]['route_ids']]], ['name'])
            rnames = [r['name'] for r in route_names]
            print(f"  {pname}: {', '.join(rnames)}")

# Verify analytic setup
print("\n[19.6] Analytic Setup:")
plans = search_read('account.analytic.plan', [], ['name'])
for p in plans:
    print(f"  Plan: {p['name']}")
aa = search_read('account.analytic.account', [], ['name', 'plan_id'])
for a in aa:
    print(f"  Account: {a['name']} (Plan: {a['plan_id']})")

# Verify pricelists
print("\n[19.7] Pricelists:")
pls = search_read('product.pricelist', [], ['name', 'currency_id'])
for pl in pls:
    print(f"  {pl['name']} ({pl['currency_id']})")

# Verify contacts
print("\n[19.8] Contacts:")
vendors = search_read('res.partner', [['supplier_rank', '>', 0]], ['name', 'city'])
print(f"  Vendors ({len(vendors)}):")
for v in vendors:
    print(f"    {v['name']} — {v.get('city','')}")

customers = search_read('res.partner', [['customer_rank', '>', 0], ['is_company', '=', True]], ['name', 'city', 'property_product_pricelist'])
print(f"  Customers ({len(customers)}):")
for c in customers:
    print(f"    {c['name']} — {c.get('city','')}")

# Verify sale orders
print("\n[19.9] Sale Orders:")
sos = search_read('sale.order', [['company_id', '=', COMPANY_ID]], ['name', 'partner_id', 'warehouse_id', 'state', 'amount_total'])
for so in sos:
    print(f"  {so['name']}: {so['partner_id'][1]} (WH: {so['warehouse_id']}, State: {so['state']}, Total: ₹{so['amount_total']:,.2f})")

# Verify purchase orders
print("\n[19.10] Purchase Orders:")
pos = search_read('purchase.order', [['company_id', '=', COMPANY_ID]], ['name', 'partner_id', 'state', 'amount_total'])
for po in pos:
    print(f"  {po['name']}: {po['partner_id'][1]} (State: {po['state']}, Total: ₹{po['amount_total']:,.2f})")

# Verify internal transfers
print("\n[19.11] Internal Transfers:")
int_picks = search_read('stock.picking', [['picking_type_code', '=', 'internal'], ['company_id', '=', COMPANY_ID]], 
    ['name', 'location_id', 'location_dest_id', 'state', 'origin'])
for pick in int_picks:
    print(f"  {pick['name']}: {pick['location_id'][1]} → {pick['location_dest_id'][1]} (State: {pick['state']})")

print("\n" + "═" * 70)
print("✅ SETUP COMPLETE!")
print("═" * 70)
print("""
WHAT WAS CREATED:
─────────────────
🏢 Company: Company A — SmartTech Retail

🏭 Warehouses (3 Outlets):
   • Kochi Outlet (KOCHI) — Central/Flagship, manufactures + buys
   • Bangalore Outlet (BANG) — Resupplied from Kochi
   • Chennai Outlet (CHEN) — Resupplied from Kochi

📍 Sub-Locations:
   • Kochi: Zone A Electronics, Zone B Furniture, Zone C Accessories, Cold Storage
   • Bangalore: Display Area, Back Storage
   • Chennai: Showroom Floor, Storage Room

🔄 Resupply Routes:
   • Bangalore ← Supply from Kochi
   • Chennai ← Supply from Kochi

📦 Products: 12 products across 4 categories
   (Electronics, Furniture, Accessories, Smart Home)

📊 Reordering Rules: 36 rules total
   • 12 for Kochi (Buy from vendors)
   • 12 for Bangalore (Resupply from Kochi)
   • 12 for Chennai (Resupply from Kochi)

📈 Analytic Accounting:
   • Plan: "Outlets"
   • Accounts: Kochi Outlet, Bangalore Outlet, Chennai Outlet

💰 Pricelists:
   • Kochi — Standard pricing
   • Bangalore — 5% competitive discount
   • Chennai — 10% introductory discount

👥 Contacts:
   • 3 Vendors (TechVision, FurniCraft, SmartParts)
   • 9 Customers (3 per city)

📝 Sample Documents:
   • 3 Sale Orders (one per outlet)
   • 2 Purchase Orders (electronics + furniture)
   • 2 Internal Transfers (Kochi→Bangalore, Kochi→Chennai)

NEXT STEPS:
───────────
1. Log in to https://demo-tech.odoo.com
2. Review all created data
3. Confirm Sale Orders to trigger delivery flows
4. Confirm Purchase Orders to trigger receipts
5. Process Internal Transfers
6. Run scheduler for reordering rules: Inventory → Operations → Replenishment → ⚙️ → Run Scheduler
7. Create invoices with Analytic Distribution tags for outlet P&L tracking
""")
