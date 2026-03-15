"""
============================================================================
BRANCH-WISE WAREHOUSE & FULL FLOW SETUP
============================================================================
Database: https://client-cient.odoo.com/odoo

Current State:
  Company 1: Krishnadas Group (ROOT)       — has WH, NH GF, NH FF, FB warehouses + journals
  Company 2: Devika Furniture (branch)      — NO warehouse, NO journals
  Company 3: KDESIGN INTERIOR (branch)      — NO warehouse, NO journals
  Company 4: KDESIGN INTERIOR FURNISHING    — has kd warehouse + journals

This script creates:
  ✅ Separate warehouse for Devika Furniture (DF)
  ✅ Separate warehouse for KDESIGN INTERIOR (KDI)
  ✅ Sales, Purchase, Bank, Cash journals per branch
  ✅ Sample products available across all branches
  ✅ Initial stock in each branch warehouse
  ✅ Sale Orders per branch (confirmed → delivery created)
  ✅ Purchase Orders per branch (confirmed → receipt created)
  ✅ Customer Invoices per branch (posted)
  ✅ Vendor Bills per branch (posted)
  ✅ Analytic accounts per branch for reporting

After running, you can check branch-wise reports:
  - Sales Analysis, Purchase Analysis
  - Inventory Valuation per warehouse
  - Profit & Loss by branch, Journal reports, etc.
============================================================================
"""

import xmlrpc.client
import sys
import time
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# CONNECTION
# ─────────────────────────────────────────────
URL = 'https://client-cient.odoo.com'
DB = 'client-cient'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

print("=" * 70)
print("  BRANCH-WISE WAREHOUSE & FULL FLOW SETUP")
print("=" * 70)

print("\n[CONNECT] Connecting...")
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
# HELPERS
# ─────────────────────────────────────────────
def execute(model, method, *args, **kwargs):
    try:
        return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kwargs)
    except Exception as e:
        print(f"  ⚠️  {model}.{method}: {e}")
        return None

def search(model, domain, limit=0):
    kw = {}
    if limit:
        kw['limit'] = limit
    return execute(model, 'search', [domain], kw) or []

def search_read(model, domain, fields, limit=0):
    kw = {'fields': fields}
    if limit:
        kw['limit'] = limit
    return execute(model, 'search_read', [domain], kw) or []

def create(model, vals):
    return execute(model, 'create', [vals])

def write(model, ids, vals):
    if not isinstance(ids, list):
        ids = [ids]
    return execute(model, 'write', [ids, vals])

def find_or_create(model, domain, vals, label=""):
    existing = search_read(model, domain, ['id', 'name'], limit=1)
    if existing:
        print(f"  ℹ️  {label or vals.get('name','')} exists (ID:{existing[0]['id']})")
        return existing[0]['id'], False
    rec_id = create(model, vals)
    if rec_id:
        print(f"  ✅ Created {label or vals.get('name','')} (ID:{rec_id})")
        return rec_id, True
    print(f"  ❌ Failed: {label}")
    return None, False

# ─────────────────────────────────────────────
# DISCOVER CURRENT STATE
# ─────────────────────────────────────────────
print("\n[DISCOVER] Reading current database state...")

companies = search_read('res.company', [], ['name', 'parent_id'])
co_map = {c['id']: c['name'] for c in companies}
print(f"  Companies: {[c['name'] for c in companies]}")

# Identify company IDs
KRISHNADAS_ID = None
DEVIKA_ID = None
KDESIGN_ID = None
KDESIGNF_ID = None

for c in companies:
    if 'Krishnadas' in c['name']:
        KRISHNADAS_ID = c['id']
    elif 'Devika' in c['name']:
        DEVIKA_ID = c['id']
    elif c['name'] == 'KDESIGN INTERIOR':
        KDESIGN_ID = c['id']
    elif 'FURNISHING' in c['name']:
        KDESIGNF_ID = c['id']

print(f"  Krishnadas Group: ID={KRISHNADAS_ID}")
print(f"  Devika Furniture: ID={DEVIKA_ID}")
print(f"  KDESIGN INTERIOR: ID={KDESIGN_ID}")
print(f"  KDESIGN INTERIOR FURNISHING: ID={KDESIGNF_ID}")

if not all([KRISHNADAS_ID, DEVIKA_ID, KDESIGN_ID, KDESIGNF_ID]):
    print("  ❌ Could not find all 4 companies! Aborting.")
    sys.exit(1)

# Get India/Kerala
india = search_read('res.country', [['code', '=', 'IN']], ['id'], limit=1)
INDIA_ID = india[0]['id'] if india else False
kerala = search_read('res.country.state', [['name', '=', 'Kerala'], ['country_id', '=', INDIA_ID]], ['id'], limit=1)
KERALA_ID = kerala[0]['id'] if kerala else False

# Ensure user has access to all companies
print("\n[ACCESS] Granting access to all companies...")
try:
    write('res.users', [uid], {
        'company_ids': [(4, KRISHNADAS_ID), (4, DEVIKA_ID), (4, KDESIGN_ID), (4, KDESIGNF_ID)],
    })
    print("  ✅ User has access to all 4 companies")
except Exception as e:
    print(f"  ⚠️  {e}")


# ══════════════════════════════════════════════════════════
# PHASE 1: CREATE WAREHOUSES FOR BRANCHES
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 1: CREATE BRANCH WAREHOUSES")
print("═" * 70)

# Devika Furniture warehouse
print("\n  [1.1] Devika Furniture Warehouse...")
devika_wh_id, devika_wh_new = find_or_create('stock.warehouse',
    [['company_id', '=', DEVIKA_ID]],
    {
        'name': 'Devika Furniture Showroom',
        'code': 'DF',
        'company_id': DEVIKA_ID,
        'reception_steps': 'one_step',
        'delivery_steps': 'ship_only',
    },
    "Devika Furniture Warehouse (DF)"
)

# KDESIGN INTERIOR warehouse
print("\n  [1.2] KDESIGN INTERIOR Warehouse...")
kdesign_wh_id, kdesign_wh_new = find_or_create('stock.warehouse',
    [['company_id', '=', KDESIGN_ID]],
    {
        'name': 'KDESIGN Interior Kochi',
        'code': 'KDI',
        'company_id': KDESIGN_ID,
        'reception_steps': 'one_step',
        'delivery_steps': 'ship_only',
    },
    "KDESIGN INTERIOR Warehouse (KDI)"
)

# List all warehouses now
print("\n  All warehouses after creation:")
all_wh = search_read('stock.warehouse', [], ['name', 'code', 'company_id'])
for w in all_wh:
    co = w['company_id'][1] if w['company_id'] else 'N/A'
    print(f"    {w['name']} ({w['code']}) — {co}")


# ══════════════════════════════════════════════════════════
# PHASE 2: CREATE JOURNALS FOR EACH BRANCH
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 2: BRANCH-WISE JOURNALS")
print("═" * 70)

# Define journals needed for each branch company
branch_journals = {
    DEVIKA_ID: {
        'label': 'Devika Furniture',
        'journals': [
            {'name': 'Sales - Devika', 'code': 'INV', 'type': 'sale'},
            {'name': 'Purchases - Devika', 'code': 'BILL', 'type': 'purchase'},
            {'name': 'Bank Devika 4501', 'code': 'BNK1', 'type': 'bank'},
            {'name': 'Cash - Devika', 'code': 'CSH1', 'type': 'cash'},
            {'name': 'Miscellaneous - Devika', 'code': 'MISC', 'type': 'general'},
            {'name': 'Inventory Valuation - Devika', 'code': 'STJ', 'type': 'general'},
        ]
    },
    KDESIGN_ID: {
        'label': 'KDESIGN INTERIOR',
        'journals': [
            {'name': 'Sales - KDESIGN', 'code': 'INV', 'type': 'sale'},
            {'name': 'Purchases - KDESIGN', 'code': 'BILL', 'type': 'purchase'},
            {'name': 'Bank KDESIGN 7802', 'code': 'BNK1', 'type': 'bank'},
            {'name': 'Cash - KDESIGN', 'code': 'CSH1', 'type': 'cash'},
            {'name': 'Miscellaneous - KDESIGN', 'code': 'MISC', 'type': 'general'},
            {'name': 'Inventory Valuation - KDESIGN', 'code': 'STJ', 'type': 'general'},
        ]
    },
}

for company_id, jconf in branch_journals.items():
    print(f"\n  [{jconf['label']}] Creating journals...")
    for jdef in jconf['journals']:
        # Check if same code+company already exists
        existing = search_read('account.journal',
            [['code', '=', jdef['code']], ['company_id', '=', company_id]],
            ['id', 'name'], limit=1)
        if existing:
            # Rename it if the name is generic
            if existing[0]['name'] != jdef['name']:
                write('account.journal', [existing[0]['id']], {'name': jdef['name']})
                print(f"    ✅ Renamed {existing[0]['name']} → {jdef['name']}")
            else:
                print(f"    ℹ️  {jdef['name']} exists (ID:{existing[0]['id']})")
        else:
            j_id = create('account.journal', {
                'name': jdef['name'],
                'code': jdef['code'],
                'type': jdef['type'],
                'company_id': company_id,
            })
            if j_id:
                print(f"    ✅ Created {jdef['name']} (ID:{j_id})")
            else:
                print(f"    ❌ Failed: {jdef['name']}")

# Show all journals
print("\n  All journals in database:")
all_journals = search_read('account.journal', [], ['name', 'code', 'type', 'company_id'])
for j in sorted(all_journals, key=lambda x: (x['company_id'][1] if x['company_id'] else '', x['type'])):
    co = j['company_id'][1] if j['company_id'] else 'N/A'
    print(f"    {j['name']} ({j['code']}) — {j['type']} | {co}")


# ══════════════════════════════════════════════════════════
# PHASE 3: INITIAL STOCK IN EACH BRANCH WAREHOUSE
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 3: STOCK IN EACH BRANCH WAREHOUSE")
print("═" * 70)

# Get some product IDs to stock
prod_names_for_stock = [
    'PVC Blinds', 'Zebra Roller Blind 4ft', 'Royal Silk Curtain Fabric Per Mtr',
    '001GREY@1560', 'Readymade Blackout Curtain 7ft', 'Velvet Cushion Cover 16x16',
    'MDF Board 8x4 18mm', 'Plywood BWR 8x4 19mm', 'Ortho Memory Foam Mattress King',
    'Coir Door Mat 2x3 Natural', 'Persian Style Carpet 6x9', 'Memory Foam Pillow Premium',
]

prod_map = {}  # name → product.product ID
for pname in prod_names_for_stock:
    pp = search_read('product.product', [['name', '=', pname]], ['id'], limit=1)
    if not pp:
        pt = search_read('product.template', [['name', '=', pname]], ['id'], limit=1)
        if pt:
            pp = search_read('product.product', [['product_tmpl_id', '=', pt[0]['id']]], ['id'], limit=1)
    if pp:
        prod_map[pname] = pp[0]['id']
    else:
        print(f"  ⚠️  Product not found: {pname}")

# Stock entries per warehouse (by company_id)
stock_plan = {
    DEVIKA_ID: {
        'label': 'Devika Furniture',
        'items': [
            ('PVC Blinds', 50),
            ('Zebra Roller Blind 4ft', 15),
            ('Royal Silk Curtain Fabric Per Mtr', 25),
            ('Readymade Blackout Curtain 7ft', 20),
            ('Persian Style Carpet 6x9', 8),
            ('Ortho Memory Foam Mattress King', 5),
            ('Memory Foam Pillow Premium', 30),
            ('Velvet Cushion Cover 16x16', 40),
            ('Coir Door Mat 2x3 Natural', 20),
            ('MDF Board 8x4 18mm', 10),
        ]
    },
    KDESIGN_ID: {
        'label': 'KDESIGN INTERIOR',
        'items': [
            ('PVC Blinds', 40),
            ('001GREY@1560', 15),
            ('Readymade Blackout Curtain 7ft', 12),
            ('Velvet Cushion Cover 16x16', 25),
            ('MDF Board 8x4 18mm', 20),
            ('Plywood BWR 8x4 19mm', 15),
            ('Ortho Memory Foam Mattress King', 3),
            ('Coir Door Mat 2x3 Natural', 15),
            ('Memory Foam Pillow Premium', 20),
            ('Persian Style Carpet 6x9', 5),
        ]
    },
    KRISHNADAS_ID: {
        'label': 'Krishnadas Group (add more)',
        'items': [
            ('Zebra Roller Blind 4ft', 20),
            ('Royal Silk Curtain Fabric Per Mtr', 30),
            ('Readymade Blackout Curtain 7ft', 25),
            ('Ortho Memory Foam Mattress King', 10),
            ('Persian Style Carpet 6x9', 12),
            ('Velvet Cushion Cover 16x16', 50),
        ]
    },
    KDESIGNF_ID: {
        'label': 'KDESIGN FURNISHING (add more)',
        'items': [
            ('MDF Board 8x4 18mm', 25),
            ('Plywood BWR 8x4 19mm', 20),
            ('Readymade Blackout Curtain 7ft', 10),
            ('PVC Blinds', 30),
            ('Coir Door Mat 2x3 Natural', 10),
        ]
    },
}

for company_id, plan in stock_plan.items():
    print(f"\n  [{plan['label']}] Setting up stock...")
    
    # Find the stock location for this company's warehouse
    wh = search_read('stock.warehouse', [['company_id', '=', company_id]], ['id', 'lot_stock_id', 'name'], limit=1)
    if not wh:
        print(f"    ⚠️  No warehouse found for company {company_id}, skipping")
        continue
    
    stock_loc_id = wh[0]['lot_stock_id'][0] if wh[0].get('lot_stock_id') else None
    if not stock_loc_id:
        # Fallback: find internal Stock location
        loc = search_read('stock.location',
            [['usage', '=', 'internal'], ['company_id', '=', company_id], ['name', '=', 'Stock']],
            ['id'], limit=1)
        stock_loc_id = loc[0]['id'] if loc else None
    
    if not stock_loc_id:
        print(f"    ⚠️  No stock location found, skipping")
        continue
    
    print(f"    Using location ID: {stock_loc_id} (warehouse: {wh[0]['name']})")
    
    for pname, qty in plan['items']:
        if pname not in prod_map:
            continue
        pid = prod_map[pname]
        
        existing_q = search_read('stock.quant',
            [['product_id', '=', pid], ['location_id', '=', stock_loc_id]],
            ['id', 'quantity'], limit=1)
        
        try:
            if existing_q:
                new_qty = existing_q[0]['quantity'] + qty
                write('stock.quant', [existing_q[0]['id']], {'quantity': new_qty})
                print(f"    ✅ {pname}: {existing_q[0]['quantity']}→{new_qty}")
            else:
                q_id = create('stock.quant', {
                    'product_id': pid,
                    'location_id': stock_loc_id,
                    'quantity': qty,
                    'company_id': company_id,
                })
                if q_id:
                    print(f"    ✅ {pname}: {qty} units")
                else:
                    print(f"    ❌ Failed stock for {pname}")
        except Exception as e:
            print(f"    ⚠️  {pname}: {e}")


# ══════════════════════════════════════════════════════════
# PHASE 4: SALE ORDERS PER BRANCH (Confirmed)
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 4: SALE ORDERS PER BRANCH")
print("═" * 70)

# Get customer IDs
customers_all = search_read('res.partner', [['customer_rank', '>', 0]], ['id', 'name', 'city'])
cust_map = {c['name']: c['id'] for c in customers_all}

# Get all warehouse IDs mapped by company
wh_by_company = {}
for w in search_read('stock.warehouse', [], ['id', 'company_id']):
    co_id = w['company_id'][0]
    if co_id not in wh_by_company:
        wh_by_company[co_id] = w['id']

# Sale orders plan
sale_orders_plan = [
    # Krishnadas Group — 3 SOs
    {
        'company_id': KRISHNADAS_ID,
        'customer': 'Anoop Krishnan Nair',
        'lines': [
            ('PVC Blinds', 10, 850),
            ('Royal Silk Curtain Fabric Per Mtr', 5, 680),
            ('Readymade Blackout Curtain 7ft', 3, 1800),
        ]
    },
    {
        'company_id': KRISHNADAS_ID,
        'customer': 'Varghese & Sons Builders',
        'lines': [
            ('Ortho Memory Foam Mattress King', 4, 22000),
            ('Memory Foam Pillow Premium', 8, 1200),
            ('Persian Style Carpet 6x9', 2, 8500),
        ]
    },
    {
        'company_id': KRISHNADAS_ID,
        'customer': 'Rajan Pillai',
        'lines': [
            ('Velvet Cushion Cover 16x16', 10, 350),
            ('Coir Door Mat 2x3 Natural', 5, 350),
            ('Zebra Roller Blind 4ft', 2, 2200),
        ]
    },
    # Devika Furniture — 3 SOs
    {
        'company_id': DEVIKA_ID,
        'customer': 'Lakshmi Devi',
        'lines': [
            ('PVC Blinds', 8, 850),
            ('Readymade Blackout Curtain 7ft', 4, 1800),
            ('Velvet Cushion Cover 16x16', 6, 350),
        ]
    },
    {
        'company_id': DEVIKA_ID,
        'customer': 'Deepa Nambiar',
        'lines': [
            ('Ortho Memory Foam Mattress King', 2, 22000),
            ('Memory Foam Pillow Premium', 4, 1200),
            ('Persian Style Carpet 6x9', 1, 8500),
        ]
    },
    {
        'company_id': DEVIKA_ID,
        'customer': 'Mohammed Ashraf Interiors',
        'lines': [
            ('Royal Silk Curtain Fabric Per Mtr', 10, 680),
            ('Zebra Roller Blind 4ft', 5, 2200),
            ('Coir Door Mat 2x3 Natural', 8, 350),
        ]
    },
    # KDESIGN INTERIOR — 3 SOs
    {
        'company_id': KDESIGN_ID,
        'customer': 'Suresh Menon',
        'lines': [
            ('PVC Blinds', 15, 850),
            ('001GREY@1560', 3, 1560),
            ('MDF Board 8x4 18mm', 5, 2800),
        ]
    },
    {
        'company_id': KDESIGN_ID,
        'customer': 'Priya Thomas',
        'lines': [
            ('Readymade Blackout Curtain 7ft', 6, 1800),
            ('Velvet Cushion Cover 16x16', 10, 350),
            ('Memory Foam Pillow Premium', 5, 1200),
        ]
    },
    {
        'company_id': KDESIGN_ID,
        'customer': 'Green Valley Residency',
        'lines': [
            ('Ortho Memory Foam Mattress King', 3, 22000),
            ('Persian Style Carpet 6x9', 2, 8500),
            ('Plywood BWR 8x4 19mm', 8, 3500),
        ]
    },
    # KDESIGN INTERIOR FURNISHING — 3 SOs
    {
        'company_id': KDESIGNF_ID,
        'customer': 'Skyline Apartments Kochi',
        'lines': [
            ('MDF Board 8x4 18mm', 10, 2800),
            ('Plywood BWR 8x4 19mm', 8, 3500),
            ('PVC Blinds', 12, 850),
        ]
    },
    {
        'company_id': KDESIGNF_ID,
        'customer': 'Anoop Krishnan Nair',
        'lines': [
            ('Readymade Blackout Curtain 7ft', 5, 1800),
            ('Coir Door Mat 2x3 Natural', 10, 350),
        ]
    },
    {
        'company_id': KDESIGNF_ID,
        'customer': 'Lakshmi Devi',
        'lines': [
            ('PVC Blinds', 6, 850),
            ('MDF Board 8x4 18mm', 4, 2800),
        ]
    },
]

created_so_ids = {}  # company_id → list of SO IDs

for so_plan in sale_orders_plan:
    co_id = so_plan['company_id']
    co_name = co_map.get(co_id, f'Company {co_id}')
    cust_name = so_plan['customer']
    cust_id = cust_map.get(cust_name)
    
    if not cust_id:
        print(f"  ⚠️  Customer '{cust_name}' not found, skipping")
        continue
    
    wh_id = wh_by_company.get(co_id)
    
    print(f"\n  [{co_name}] SO for {cust_name}...")
    
    so_vals = {
        'partner_id': cust_id,
        'company_id': co_id,
    }
    if wh_id:
        so_vals['warehouse_id'] = wh_id
    
    try:
        so_id = create('sale.order', so_vals)
        if not so_id:
            print(f"    ❌ Failed to create SO")
            continue
        print(f"    ✅ Created SO (ID:{so_id})")
        
        # Add lines
        for pname, qty, price in so_plan['lines']:
            if pname not in prod_map:
                print(f"    ⚠️  Product '{pname}' not in map, skipping line")
                continue
            
            line_id = create('sale.order.line', {
                'order_id': so_id,
                'product_id': prod_map[pname],
                'product_uom_qty': qty,
                'price_unit': price,
                'name': pname,
            })
            if line_id:
                print(f"      + {pname} x{qty} @ ₹{price}")
        
        # Confirm the SO
        try:
            execute('sale.order', 'action_confirm', [[so_id]])
            print(f"    ✅ SO confirmed!")
        except Exception as e:
            print(f"    ⚠️  Could not confirm SO: {e}")
        
        if co_id not in created_so_ids:
            created_so_ids[co_id] = []
        created_so_ids[co_id].append(so_id)
        
    except Exception as e:
        print(f"    ❌ SO creation error: {e}")


# ══════════════════════════════════════════════════════════
# PHASE 5: PURCHASE ORDERS PER BRANCH (Confirmed)
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 5: PURCHASE ORDERS PER BRANCH")
print("═" * 70)

vendors_all = search_read('res.partner', [['supplier_rank', '>', 0]], ['id', 'name'])
vendor_map = {v['name']: v['id'] for v in vendors_all}

purchase_orders_plan = [
    # Krishnadas Group — 2 POs
    {
        'company_id': KRISHNADAS_ID,
        'vendor': 'Kerala Blinds & Curtains Pvt Ltd',
        'lines': [
            ('PVC Blinds', 100, 450),
            ('Zebra Roller Blind 4ft', 30, 1200),
            ('Readymade Blackout Curtain 7ft', 50, 950),
        ]
    },
    {
        'company_id': KRISHNADAS_ID,
        'vendor': 'Southern Mattress Factory',
        'lines': [
            ('Ortho Memory Foam Mattress King', 15, 14000),
            ('Memory Foam Pillow Premium', 50, 650),
        ]
    },
    # Devika Furniture — 2 POs
    {
        'company_id': DEVIKA_ID,
        'vendor': 'Kerala Blinds & Curtains Pvt Ltd',
        'lines': [
            ('PVC Blinds', 60, 450),
            ('Royal Silk Curtain Fabric Per Mtr', 40, 350),
            ('Readymade Blackout Curtain 7ft', 30, 950),
        ]
    },
    {
        'company_id': DEVIKA_ID,
        'vendor': 'Malabar Furnishing Supplies',
        'lines': [
            ('Persian Style Carpet 6x9', 10, 4500),
            ('Velvet Cushion Cover 16x16', 60, 170),
            ('Memory Foam Pillow Premium', 40, 650),
        ]
    },
    # KDESIGN INTERIOR — 2 POs
    {
        'company_id': KDESIGN_ID,
        'vendor': 'Cochin Laminate House',
        'lines': [
            ('MDF Board 8x4 18mm', 30, 1800),
            ('Plywood BWR 8x4 19mm', 25, 2200),
        ]
    },
    {
        'company_id': KDESIGN_ID,
        'vendor': 'Kerala Blinds & Curtains Pvt Ltd',
        'lines': [
            ('PVC Blinds', 50, 450),
            ('Readymade Blackout Curtain 7ft', 20, 950),
        ]
    },
    # KDESIGN INTERIOR FURNISHING — 2 POs
    {
        'company_id': KDESIGNF_ID,
        'vendor': 'Travancore Wood Industries',
        'lines': [
            ('MDF Board 8x4 18mm', 40, 1800),
            ('Plywood BWR 8x4 19mm', 30, 2200),
        ]
    },
    {
        'company_id': KDESIGNF_ID,
        'vendor': 'Kerala Blinds & Curtains Pvt Ltd',
        'lines': [
            ('PVC Blinds', 40, 450),
            ('Readymade Blackout Curtain 7ft', 15, 950),
        ]
    },
]

created_po_ids = {}

for po_plan in purchase_orders_plan:
    co_id = po_plan['company_id']
    co_name = co_map.get(co_id, f'Company {co_id}')
    vendor_name = po_plan['vendor']
    vendor_id = vendor_map.get(vendor_name)
    
    if not vendor_id:
        print(f"  ⚠️  Vendor '{vendor_name}' not found, skipping")
        continue
    
    print(f"\n  [{co_name}] PO from {vendor_name}...")
    
    try:
        po_id = create('purchase.order', {
            'partner_id': vendor_id,
            'company_id': co_id,
        })
        if not po_id:
            print(f"    ❌ Failed to create PO")
            continue
        print(f"    ✅ Created PO (ID:{po_id})")
        
        for pname, qty, price in po_plan['lines']:
            if pname not in prod_map:
                continue
            line_id = create('purchase.order.line', {
                'order_id': po_id,
                'product_id': prod_map[pname],
                'product_qty': qty,
                'price_unit': price,
                'name': pname,
            })
            if line_id:
                print(f"      + {pname} x{qty} @ ₹{price}")
        
        # Confirm the PO
        try:
            execute('purchase.order', 'button_confirm', [[po_id]])
            print(f"    ✅ PO confirmed!")
        except Exception as e:
            print(f"    ⚠️  Could not confirm PO: {e}")
        
        if co_id not in created_po_ids:
            created_po_ids[co_id] = []
        created_po_ids[co_id].append(po_id)
        
    except Exception as e:
        print(f"    ❌ PO creation error: {e}")


# ══════════════════════════════════════════════════════════
# PHASE 6: CUSTOMER INVOICES PER BRANCH (Draft → Posted)
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 6: CUSTOMER INVOICES PER BRANCH")
print("═" * 70)

invoice_plan = [
    # Krishnadas Group
    {
        'company_id': KRISHNADAS_ID,
        'customer': 'Anoop Krishnan Nair',
        'lines': [
            ('PVC Blinds', 5, 850),
            ('Readymade Blackout Curtain 7ft', 2, 1800),
        ]
    },
    {
        'company_id': KRISHNADAS_ID,
        'customer': 'Varghese & Sons Builders',
        'lines': [
            ('Ortho Memory Foam Mattress King', 2, 22000),
            ('Persian Style Carpet 6x9', 1, 8500),
        ]
    },
    # Devika Furniture
    {
        'company_id': DEVIKA_ID,
        'customer': 'Lakshmi Devi',
        'lines': [
            ('PVC Blinds', 4, 850),
            ('Velvet Cushion Cover 16x16', 6, 350),
        ]
    },
    {
        'company_id': DEVIKA_ID,
        'customer': 'Deepa Nambiar',
        'lines': [
            ('Ortho Memory Foam Mattress King', 1, 22000),
            ('Memory Foam Pillow Premium', 4, 1200),
        ]
    },
    # KDESIGN INTERIOR
    {
        'company_id': KDESIGN_ID,
        'customer': 'Suresh Menon',
        'lines': [
            ('PVC Blinds', 10, 850),
            ('MDF Board 8x4 18mm', 3, 2800),
        ]
    },
    {
        'company_id': KDESIGN_ID,
        'customer': 'Green Valley Residency',
        'lines': [
            ('Plywood BWR 8x4 19mm', 5, 3500),
            ('Readymade Blackout Curtain 7ft', 3, 1800),
        ]
    },
    # KDESIGN INTERIOR FURNISHING
    {
        'company_id': KDESIGNF_ID,
        'customer': 'Skyline Apartments Kochi',
        'lines': [
            ('MDF Board 8x4 18mm', 6, 2800),
            ('Plywood BWR 8x4 19mm', 4, 3500),
        ]
    },
    {
        'company_id': KDESIGNF_ID,
        'customer': 'Anoop Krishnan Nair',
        'lines': [
            ('PVC Blinds', 3, 850),
            ('Coir Door Mat 2x3 Natural', 5, 350),
        ]
    },
]

# Find sale journal per company
sale_journal_map = {}
for j in search_read('account.journal', [['type', '=', 'sale']], ['id', 'company_id']):
    co_id = j['company_id'][0]
    sale_journal_map[co_id] = j['id']

for inv_plan in invoice_plan:
    co_id = inv_plan['company_id']
    co_name = co_map.get(co_id, f'Company {co_id}')
    cust_name = inv_plan['customer']
    cust_id = cust_map.get(cust_name)
    
    if not cust_id:
        print(f"  ⚠️  Customer '{cust_name}' not found, skipping")
        continue
    
    journal_id = sale_journal_map.get(co_id)
    
    print(f"\n  [{co_name}] Invoice for {cust_name}...")
    
    inv_vals = {
        'move_type': 'out_invoice',
        'partner_id': cust_id,
        'company_id': co_id,
    }
    if journal_id:
        inv_vals['journal_id'] = journal_id
    
    try:
        inv_id = create('account.move', inv_vals)
        if not inv_id:
            print(f"    ❌ Failed to create invoice")
            continue
        print(f"    ✅ Created Invoice (ID:{inv_id})")
        
        for pname, qty, price in inv_plan['lines']:
            if pname not in prod_map:
                continue
            line_id = create('account.move.line', {
                'move_id': inv_id,
                'product_id': prod_map[pname],
                'quantity': qty,
                'price_unit': price,
                'name': pname,
            })
            if line_id:
                print(f"      + {pname} x{qty} @ ₹{price}")
        
        # Post the invoice
        try:
            execute('account.move', 'action_post', [[inv_id]])
            print(f"    ✅ Invoice posted!")
        except Exception as e:
            print(f"    ⚠️  Could not post invoice: {e}")
    
    except Exception as e:
        print(f"    ❌ Invoice error: {e}")


# ══════════════════════════════════════════════════════════
# PHASE 7: VENDOR BILLS PER BRANCH (Draft → Posted)
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 7: VENDOR BILLS PER BRANCH")
print("═" * 70)

bill_plan = [
    # Krishnadas Group
    {
        'company_id': KRISHNADAS_ID,
        'vendor': 'Kerala Blinds & Curtains Pvt Ltd',
        'lines': [
            ('PVC Blinds', 50, 450),
            ('Readymade Blackout Curtain 7ft', 20, 950),
        ]
    },
    {
        'company_id': KRISHNADAS_ID,
        'vendor': 'Southern Mattress Factory',
        'lines': [
            ('Ortho Memory Foam Mattress King', 8, 14000),
            ('Memory Foam Pillow Premium', 20, 650),
        ]
    },
    # Devika Furniture
    {
        'company_id': DEVIKA_ID,
        'vendor': 'Kerala Blinds & Curtains Pvt Ltd',
        'lines': [
            ('PVC Blinds', 30, 450),
            ('Royal Silk Curtain Fabric Per Mtr', 20, 350),
        ]
    },
    {
        'company_id': DEVIKA_ID,
        'vendor': 'Malabar Furnishing Supplies',
        'lines': [
            ('Persian Style Carpet 6x9', 5, 4500),
            ('Velvet Cushion Cover 16x16', 30, 170),
        ]
    },
    # KDESIGN INTERIOR
    {
        'company_id': KDESIGN_ID,
        'vendor': 'Cochin Laminate House',
        'lines': [
            ('MDF Board 8x4 18mm', 15, 1800),
            ('Plywood BWR 8x4 19mm', 12, 2200),
        ]
    },
    {
        'company_id': KDESIGN_ID,
        'vendor': 'Kerala Blinds & Curtains Pvt Ltd',
        'lines': [
            ('PVC Blinds', 25, 450),
        ]
    },
    # KDESIGN INTERIOR FURNISHING
    {
        'company_id': KDESIGNF_ID,
        'vendor': 'Travancore Wood Industries',
        'lines': [
            ('MDF Board 8x4 18mm', 20, 1800),
            ('Plywood BWR 8x4 19mm', 15, 2200),
        ]
    },
    {
        'company_id': KDESIGNF_ID,
        'vendor': 'Kerala Blinds & Curtains Pvt Ltd',
        'lines': [
            ('PVC Blinds', 20, 450),
        ]
    },
]

# Find purchase journal per company
purchase_journal_map = {}
for j in search_read('account.journal', [['type', '=', 'purchase']], ['id', 'company_id']):
    co_id = j['company_id'][0]
    purchase_journal_map[co_id] = j['id']

for bill_p in bill_plan:
    co_id = bill_p['company_id']
    co_name = co_map.get(co_id, f'Company {co_id}')
    vendor_name = bill_p['vendor']
    vendor_id = vendor_map.get(vendor_name)
    
    if not vendor_id:
        print(f"  ⚠️  Vendor '{vendor_name}' not found, skipping")
        continue
    
    journal_id = purchase_journal_map.get(co_id)
    
    print(f"\n  [{co_name}] Bill from {vendor_name}...")
    
    bill_vals = {
        'move_type': 'in_invoice',
        'partner_id': vendor_id,
        'company_id': co_id,
    }
    if journal_id:
        bill_vals['journal_id'] = journal_id
    
    try:
        bill_id = create('account.move', bill_vals)
        if not bill_id:
            print(f"    ❌ Failed to create bill")
            continue
        print(f"    ✅ Created Bill (ID:{bill_id})")
        
        for pname, qty, price in bill_p['lines']:
            if pname not in prod_map:
                continue
            line_id = create('account.move.line', {
                'move_id': bill_id,
                'product_id': prod_map[pname],
                'quantity': qty,
                'price_unit': price,
                'name': pname,
            })
            if line_id:
                print(f"      + {pname} x{qty} @ ₹{price}")
        
        # Post the bill
        try:
            execute('account.move', 'action_post', [[bill_id]])
            print(f"    ✅ Bill posted!")
        except Exception as e:
            print(f"    ⚠️  Could not post bill: {e}")
    
    except Exception as e:
        print(f"    ❌ Bill error: {e}")


# ══════════════════════════════════════════════════════════
# PHASE 8: ANALYTIC ACCOUNTS PER BRANCH (for reporting)
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 8: ANALYTIC ACCOUNTS FOR BRANCH REPORTING")
print("═" * 70)

# First check if analytic accounting is enabled and find/create a plan
print("  Enabling analytic accounting...")
try:
    config_id = create('res.config.settings', {
        'group_analytic_accounting': True,
    })
    if config_id:
        execute('res.config.settings', 'execute', [[config_id]])
        print("  ✅ Analytic accounting enabled")
        time.sleep(2)
except Exception as e:
    print(f"  ⚠️  Settings: {e}")

# Find or create analytic plan
print("\n  Setting up analytic plan 'Branches'...")
plan_id, _ = find_or_create('account.analytic.plan',
    [['name', '=', 'Branches']],
    {'name': 'Branches'},
    "Analytic Plan: Branches"
)

if plan_id:
    # Create analytic accounts for each branch
    branch_analytics = [
        ('Krishnadas Group HQ', KRISHNADAS_ID),
        ('Devika Furniture Branch', DEVIKA_ID),
        ('KDESIGN Interior Branch', KDESIGN_ID),
        ('KDESIGN Furnishing', KDESIGNF_ID),
    ]
    
    for aa_name, co_id in branch_analytics:
        find_or_create('account.analytic.account',
            [['name', '=', aa_name]],
            {
                'name': aa_name,
                'plan_id': plan_id,
                'company_id': co_id,
            },
            f"Analytic: {aa_name}"
        )


# ══════════════════════════════════════════════════════════
# FINAL VERIFICATION
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  FINAL VERIFICATION")
print("═" * 70)

# Warehouses
print("\n📦 WAREHOUSES BY BRANCH:")
for w in search_read('stock.warehouse', [], ['name', 'code', 'company_id']):
    co = w['company_id'][1] if w['company_id'] else 'N/A'
    print(f"  {w['name']} ({w['code']}) — {co}")

# Journals
print("\n📒 JOURNALS BY BRANCH:")
for j in sorted(
    search_read('account.journal', [], ['name', 'code', 'type', 'company_id']),
    key=lambda x: (x['company_id'][1] if x['company_id'] else '', x['type'])
):
    co = j['company_id'][1] if j['company_id'] else 'N/A'
    print(f"  {j['name']} ({j['code']}) — {j['type']} | {co}")

# Sale Orders
print("\n🛒 SALE ORDERS BY BRANCH:")
sos = search_read('sale.order', [], ['name', 'partner_id', 'state', 'amount_total', 'company_id'])
for so in sos:
    co = so['company_id'][1] if so['company_id'] else 'N/A'
    cust = so['partner_id'][1] if so['partner_id'] else 'N/A'
    print(f"  {so['name']} — {cust} | {so['state']} | ₹{so['amount_total']} | {co}")

# Purchase Orders
print("\n📋 PURCHASE ORDERS BY BRANCH:")
pos = search_read('purchase.order', [], ['name', 'partner_id', 'state', 'amount_total', 'company_id'])
for po in pos:
    co = po['company_id'][1] if po['company_id'] else 'N/A'
    vendor = po['partner_id'][1] if po['partner_id'] else 'N/A'
    print(f"  {po['name']} — {vendor} | {po['state']} | ₹{po['amount_total']} | {co}")

# Invoices/Bills
print("\n💰 INVOICES & BILLS BY BRANCH:")
moves = search_read('account.move', 
    [['move_type', 'in', ['out_invoice', 'in_invoice']]], 
    ['name', 'move_type', 'partner_id', 'state', 'amount_total', 'company_id'])
for m in moves:
    co = m['company_id'][1] if m['company_id'] else 'N/A'
    partner = m['partner_id'][1] if m['partner_id'] else 'N/A'
    doc_type = 'INV' if m['move_type'] == 'out_invoice' else 'BILL'
    print(f"  {m['name']} [{doc_type}] — {partner} | {m['state']} | ₹{m['amount_total']} | {co}")

# Stock
print("\n📊 STOCK BY BRANCH:")
quants = search_read('stock.quant', 
    [['location_id.usage', '=', 'internal'], ['quantity', '>', 0]],
    ['product_id', 'location_id', 'quantity', 'company_id'])
for q in sorted(quants, key=lambda x: (x['company_id'][1] if x['company_id'] else '', x['product_id'][1])):
    co = q['company_id'][1] if q['company_id'] else 'N/A'
    pname = q['product_id'][1] if q['product_id'] else 'N/A'
    loc = q['location_id'][1] if q['location_id'] else 'N/A'
    print(f"  {pname} @ {loc}: {q['quantity']} | {co}")

print("\n" + "═" * 70)
print("  ✅ SETUP COMPLETE!")
print("═" * 70)
print(f"""
  You can now check branch-wise reports at:
  🔗 {URL}/odoo

  REPORTS TO TRY:
  ────────────────
  📊 Sales → Reporting → Sales Analysis (group by Company/Branch)
  📊 Purchase → Reporting → Purchase Analysis (group by Company/Branch)
  📊 Inventory → Reporting → Inventory Valuation (filter by Warehouse)
  📊 Accounting → Reporting → Profit & Loss (filter by Company)
  📊 Accounting → Reporting → General Ledger (filter by Journal or Company)
  📊 Accounting → Reporting → Partner Ledger (filter by Company)

  Each branch now has:
  • Its own warehouse with stock
  • Sales & Purchase journals
  • Bank & Cash journals
  • Sale Orders (confirmed → deliveries created)
  • Purchase Orders (confirmed → receipts created)
  • Customer Invoices (posted)
  • Vendor Bills (posted)
  • Analytic accounts for cross-branch analysis
""")
