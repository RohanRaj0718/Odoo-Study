"""
Practice Database Setup — Mirror of Client's PSI Database
==========================================================
Replicates the EXACT structure of the client's Odoo database onto
the new practice database at https://client-cient.odoo.com

MAPPING (Client → Practice):
  Companies:
    Parappattu Group          → Krishnadas Group
    Georgeon Furniture        → Devika Furniture
    PSQUARE INTERIOR          → KDESIGN INTERIOR
    PSQUARE INTERIOR FURNISHING → KDESIGN INTERIOR FURNISHING

  Warehouses (all under Krishnadas Group):
    Parappattu Group (WH)     → Krishnadas Group (WH)
    Near Home GF (NH GF)      → Near Home GF (NH GF)
    Near Home FF (NH FF)      → Near Home FF (NH FF)
    Factory Building (FB)     → Factory Building (FB)

  Locations same structure, product categories same, 
  bank journals same pattern with different last 4 digits.

  Customers/Vendors: different names, same Kerala/India addresses.
"""

import xmlrpc.client
import sys
import time

# ──────────────────────────────────────────────────────────
# CONNECTION SETTINGS
# ──────────────────────────────────────────────────────────
URL = 'https://client-cient.odoo.com'
DB = 'client-cient'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

# ──────────────────────────────────────────────────────────
# CONNECT
# ──────────────────────────────────────────────────────────
print("=" * 70)
print("  PRACTICE DATABASE SETUP — MIRROR OF CLIENT DATABASE")
print("=" * 70)

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
if not uid:
    print("❌ Authentication failed!")
    sys.exit(1)
print(f"✅ Connected as UID {uid}")

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

# ──────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────
def execute(model, method, *args, **kwargs):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kwargs)

def search_read(model, domain, fields, limit=0):
    kw = {'fields': fields}
    if limit:
        kw['limit'] = limit
    if not domain:
        domain = []
    return execute(model, 'search_read', [domain], kw)

def search(model, domain, limit=0):
    kw = {}
    if limit:
        kw['limit'] = limit
    if not domain:
        domain = []
    return execute(model, 'search', [domain], kw)

def create(model, vals):
    return execute(model, 'create', [vals])

def write(model, ids, vals):
    return execute(model, 'write', [ids, vals])

def find_or_create(model, domain, vals, label=""):
    existing = search_read(model, domain, ['id', 'name'], limit=1)
    if existing:
        print(f"  ℹ️  {label or vals.get('name', '')} already exists (ID: {existing[0]['id']})")
        return existing[0]['id']
    rec_id = create(model, vals)
    print(f"  ✅ Created {label or vals.get('name', '')} (ID: {rec_id})")
    return rec_id

# Get India country ID and Kerala state ID
india = search_read('res.country', [['code', '=', 'IN']], ['id'])
INDIA_ID = india[0]['id'] if india else False

kerala = search_read('res.country.state', [['name', '=', 'Kerala'], ['country_id', '=', INDIA_ID]], ['id'])
KERALA_ID = kerala[0]['id'] if kerala else False

print(f"  India ID: {INDIA_ID}, Kerala ID: {KERALA_ID}")

# ══════════════════════════════════════════════════════════
# PHASE 1: RENAME DEFAULT COMPANY & SET UP COMPANY HIERARCHY
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 1: COMPANY HIERARCHY")
print("═" * 70)

# Rename the default company to "Krishnadas Group" (mirrors Parappattu Group)
# Find the main/root company (smallest ID, or named Krishnadas Group if already renamed)
default_company = search_read('res.company', [], ['id', 'name', 'parent_id'])
# Sort by ID to get the original root company
default_company.sort(key=lambda x: x['id'])
# Find root companies (no parent) 
root_companies = [c for c in default_company if not c['parent_id']]
# Pick the one with the smallest ID (original company)
main_co = root_companies[0] if root_companies else default_company[0]
MAIN_COMPANY_ID = main_co['id']

if main_co['name'] != 'Krishnadas Group':
    print(f"\n  Renaming company '{main_co['name']}' (ID: {MAIN_COMPANY_ID}) → Krishnadas Group")

write('res.company', [MAIN_COMPANY_ID], {
    'name': 'Krishnadas Group',
    'street': 'Krishnadas Trading Company',
    'street2': 'Krishnadas Plaza, Near Municipal Bus Stand',
    'city': 'Pathanamthitta',
    'state_id': KERALA_ID,
    'zip': '689645',
    'country_id': INDIA_ID,
    'email': 'mail@kdesigninterior.com',
    'phone': '0468221850',
    'vat': '32AABFK5678M1ZQ',
})
if main_co['name'] != 'Krishnadas Group':
    print("  ✅ Krishnadas Group configured (root parent)")
else:
    print(f"  ℹ️  Krishnadas Group already configured (ID: {MAIN_COMPANY_ID})")

# Also update the partner record for this company
main_partner = search_read('res.partner', [['is_company', '=', True], ['name', '=', 'Krishnadas Group']], ['id'], limit=1)
if main_partner:
    write('res.partner', [main_partner[0]['id']], {
        'street': 'Krishnadas Trading Company',
        'street2': 'Krishnadas Plaza, Near Municipal Bus Stand',
        'city': 'Pathanamthitta',
        'state_id': KERALA_ID,
        'zip': '689645',
        'country_id': INDIA_ID,
        'email': 'mail@kdesigninterior.com',
        'phone': '0468221850',
        'vat': '32AABFK5678M1ZQ',
    })

# Create child company: Devika Furniture (mirrors Georgeon Furniture)
print("\n  Creating Devika Furniture (child of Krishnadas Group)...")
devika_id = find_or_create('res.company',
    [['name', '=', 'Devika Furniture']],
    {
        'name': 'Devika Furniture',
        'parent_id': MAIN_COMPANY_ID,
        'street': 'Thekkekunnel Building',
        'street2': 'St. Thomas Junction Ring Road, Pathanamthitta',
        'city': 'Pathanamthitta',
        'state_id': KERALA_ID,
        'zip': '689645',
        'country_id': INDIA_ID,
        'email': 'devikafurniture@gmail.com',
        'phone': '9744990700',
        'vat': '32AABFK5678M1ZQ',  # Same GST as parent
    },
    "Devika Furniture"
)

# Create child company: KDESIGN INTERIOR (mirrors PSQUARE INTERIOR)
print("\n  Creating KDESIGN INTERIOR (child of Krishnadas Group)...")
kdesign_id = find_or_create('res.company',
    [['name', '=', 'KDESIGN INTERIOR']],
    {
        'name': 'KDESIGN INTERIOR',
        'parent_id': MAIN_COMPANY_ID,
        'street': 'KDESIGN INTERIOR KOCHI BRANCH',
        'street2': '39/825, Plot No. 28, New Market, Kadavanthara',
        'city': 'Kochi',
        'state_id': KERALA_ID,
        'zip': '682020',
        'country_id': INDIA_ID,
        'email': '',
        'phone': '9645',
        'vat': '32AABFK5678M1ZQ',  # Same GST as parent
    },
    "KDESIGN INTERIOR"
)

# Create separate root company: KDESIGN INTERIOR FURNISHING
# (mirrors PSQUARE INTERIOR FURNISHING — different legal entity)
print("\n  Creating KDESIGN INTERIOR FURNISHING (separate root company)...")
kdesignf_id = find_or_create('res.company',
    [['name', '=', 'KDESIGN INTERIOR FURNISHING']],
    {
        'name': 'KDESIGN INTERIOR FURNISHING',
        # NO parent_id — separate legal entity
        'street': '5-76/3, Krishnadas Building-8',
        'street2': 'THONNIAMALA, PATHANAMTHITTA',
        'city': 'Pathanamthitta',
        'state_id': KERALA_ID,
        'zip': '689668',
        'country_id': INDIA_ID,
        'email': 'mail@kdesigninterior.com',
        'phone': '+919448030850',
        'vat': '32AAKCK2345R1Z5',  # Different GSTIN
    },
    "KDESIGN INTERIOR FURNISHING"
)

# Give the current user access to all 4 companies
print("\n  Granting current user access to all companies...")
try:
    write('res.users', [uid], {
        'company_ids': [(4, MAIN_COMPANY_ID), (4, devika_id), (4, kdesign_id), (4, kdesignf_id)],
        'company_id': MAIN_COMPANY_ID,
    })
    print("  ✅ User has access to all 4 companies")
except Exception as e:
    print(f"  ⚠️  Could not update user company access: {e}")

# ══════════════════════════════════════════════════════════
# PHASE 2: INSTALL REQUIRED MODULES
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 2: CHECKING / INSTALLING MODULES")
print("═" * 70)

required_modules = ['repair', 'stock_sms']
for mod_name in required_modules:
    mod = search_read('ir.module.module', [['name', '=', mod_name]], ['id', 'state'], limit=1)
    if mod and mod[0]['state'] != 'installed':
        print(f"  Installing module: {mod_name}...")
        try:
            execute('ir.module.module', 'button_immediate_install', [mod[0]['id']])
            print(f"  ✅ Installed {mod_name}")
            time.sleep(3)
        except Exception as e:
            print(f"  ⚠️  Could not install {mod_name}: {e}")
    elif mod and mod[0]['state'] == 'installed':
        print(f"  ℹ️  {mod_name} already installed")
    else:
        print(f"  ⚠️  Module {mod_name} not found in database")


# ══════════════════════════════════════════════════════════
# PHASE 3: CONFIGURE WAREHOUSES
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 3: WAREHOUSES & LOCATIONS")
print("═" * 70)

# Enable Storage Locations in settings
print("\n  Enabling Storage Locations setting...")
try:
    config_ids = search('res.config.settings', [], limit=1)
    if config_ids:
        write('res.config.settings', config_ids, {'group_stock_multi_locations': True})
    else:
        config_id = create('res.config.settings', {'group_stock_multi_locations': True})
        execute('res.config.settings', 'execute', [[config_id]])
    print("  ✅ Storage Locations enabled")
except Exception as e:
    print(f"  ⚠️  Settings update note: {e}")

# Try enabling via res.config.settings execute approach
try:
    new_config = create('res.config.settings', {
        'group_stock_multi_locations': True,
    })
    execute('res.config.settings', 'execute', [[new_config]])
    print("  ✅ Settings saved via execute")
except Exception as e:
    print(f"  ℹ️  Settings note: {e}")

# Rename default warehouse to "Krishnadas Group"
wh = search_read('stock.warehouse', [['company_id', '=', MAIN_COMPANY_ID]], ['id', 'name', 'code'])
if wh:
    main_wh_id = wh[0]['id']
    write('stock.warehouse', [main_wh_id], {'name': 'Krishnadas Group'})
    print(f"  ✅ Renamed default warehouse → Krishnadas Group (WH)")
else:
    main_wh_id = None
    print("  ⚠️  No default warehouse found!")

# Create Near Home GF warehouse
print("\n  Creating Near Home GF warehouse...")
nhgf_wh_id = find_or_create('stock.warehouse',
    [['code', '=', 'NH GF'], ['company_id', '=', MAIN_COMPANY_ID]],
    {
        'name': 'Near Home GF',
        'code': 'NH GF',
        'company_id': MAIN_COMPANY_ID,
        'reception_steps': 'one_step',
        'delivery_steps': 'ship_only',
    },
    "Near Home GF warehouse"
)

# Create Near Home FF warehouse
print("\n  Creating Near Home FF warehouse...")
nhff_wh_id = find_or_create('stock.warehouse',
    [['code', '=', 'NH FF'], ['company_id', '=', MAIN_COMPANY_ID]],
    {
        'name': 'Near Home FF',
        'code': 'NH FF',
        'company_id': MAIN_COMPANY_ID,
        'reception_steps': 'one_step',
        'delivery_steps': 'ship_only',
    },
    "Near Home FF warehouse"
)

# Create Factory Building warehouse
print("\n  Creating Factory Building warehouse...")
fb_wh_id = find_or_create('stock.warehouse',
    [['code', '=', 'FB'], ['company_id', '=', MAIN_COMPANY_ID]],
    {
        'name': 'Factory Building',
        'code': 'FB',
        'company_id': MAIN_COMPANY_ID,
        'reception_steps': 'one_step',
        'delivery_steps': 'ship_only',
    },
    "Factory Building warehouse"
)

# Create sub-locations under main WH/Stock (6 floors)
print("\n  Creating floor sub-locations under WH/Stock...")
if main_wh_id:
    # Find WH/Stock location
    wh_stock = search_read('stock.location', 
        [['warehouse_id', '=', main_wh_id], ['usage', '=', 'internal'], ['name', '=', 'Stock']], 
        ['id', 'complete_name'], limit=1)
    
    if not wh_stock:
        # Try broader search
        wh_stock = search_read('stock.location',
            [['usage', '=', 'internal'], ['company_id', '=', MAIN_COMPANY_ID], ['complete_name', 'like', 'WH/Stock']],
            ['id', 'complete_name'], limit=1)
    
    if wh_stock:
        stock_loc_id = wh_stock[0]['id']
        print(f"  Found WH/Stock location: ID={stock_loc_id}")
        
        floors = ['Ground Floor', 'First Floor', 'Second Floor', 'Third Floor', 'Fourth Floor', 'Fifth Floor']
        for floor in floors:
            find_or_create('stock.location',
                [['name', '=', floor], ['location_id', '=', stock_loc_id]],
                {
                    'name': floor,
                    'location_id': stock_loc_id,
                    'usage': 'internal',
                    'company_id': MAIN_COMPANY_ID,
                },
                f"WH/{floor}"
            )
    else:
        print("  ⚠️  Could not find WH/Stock location")


# ══════════════════════════════════════════════════════════
# PHASE 4: PRODUCT CATEGORIES
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 4: PRODUCT CATEGORIES")
print("═" * 70)

# The client has these custom categories (plus default Goods, Expenses, Services, Raw Materials)
custom_categories = [
    "Raw Materials",
    "Customized Furniture",
    "Kichen & Wardrobe",
    "Readymade Curtain",
    "Blinds",
    "Upholstery",
    "Curtain Fabric",
    "Furnishing Fabric",
    "Wallpaper",
    "Carpets",
    "Door Mats",
    "Cleaning & Hygiene Products",
    "Mattress",
    "Pillows",
    "Cushions",
    "Beddings",
    "Kichen Appliances",
    "Kichen Hardware",
    "Designer Fans",
    "Indoor Pots",
    "Indoor Plants",
    "Mosquaito Shutters",
    "Wall Art",
    "Outdoor Furniture",
    "Office Furniture",
    "Home Décor",
    "Curtain Fittings",
    "Furniture",
    "Clocks",
    "Home Furnishing",
    "Wallframes",
    "Crockery",
]

for cat_name in custom_categories:
    find_or_create('product.category',
        [['name', '=', cat_name]],
        {'name': cat_name},
        f"Category: {cat_name}"
    )


# ══════════════════════════════════════════════════════════
# PHASE 5: SAMPLE PRODUCTS (representative set across categories)
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 5: SAMPLE PRODUCTS")
print("═" * 70)

# Build category name → ID map
all_cats = search_read('product.category', [], ['id', 'name'])
cat_map = {c['name']: c['id'] for c in all_cats}

# Create representative products across categories (similar to client's 9243 but just samples)
sample_products = [
    # Beddings
    {"name": "@2499 ATLANTIC CLASSIC BEDSHEET", "categ_id": cat_map.get("Beddings", 1), "list_price": 2499, "standard_price": 1500},
    {"name": "@2799 ATLANTIC PREMIUM BEDSHEET", "categ_id": cat_map.get("Beddings", 1), "list_price": 2799, "standard_price": 1700},
    {"name": "@2999 ARTIC HUES BEDSHEET", "categ_id": cat_map.get("Beddings", 1), "list_price": 2999, "standard_price": 1800},
    {"name": "@3599 ANDRIA BEDSHEET", "categ_id": cat_map.get("Beddings", 1), "list_price": 3599, "standard_price": 2200},
    
    # Blinds
    {"name": "PVC Blinds", "categ_id": cat_map.get("Blinds", 1), "list_price": 850, "standard_price": 450},
    {"name": "101445 Roller Blind Clutch With Chain", "categ_id": cat_map.get("Blinds", 1), "list_price": 350, "standard_price": 180},
    {"name": "Zebra Roller Blind 4ft", "categ_id": cat_map.get("Blinds", 1), "list_price": 2200, "standard_price": 1200},
    {"name": "Venetian Aluminium Blind 25mm", "categ_id": cat_map.get("Blinds", 1), "list_price": 1800, "standard_price": 950},
    
    # Curtain Fabric
    {"name": "Royal Silk Curtain Fabric Per Mtr", "categ_id": cat_map.get("Curtain Fabric", 1), "list_price": 680, "standard_price": 350},
    {"name": "Cotton Blend Curtain 48inch", "categ_id": cat_map.get("Curtain Fabric", 1), "list_price": 450, "standard_price": 220},
    {"name": "Velvet Blackout Curtain Fabric", "categ_id": cat_map.get("Curtain Fabric", 1), "list_price": 1200, "standard_price": 650},
    
    # Curtain Fittings
    {"name": "001YE0043 Somfy Track", "categ_id": cat_map.get("Curtain Fittings", 1), "list_price": 4500, "standard_price": 2800},
    {"name": "0071555-Handle Fixing Screw", "categ_id": cat_map.get("Curtain Fittings", 1), "list_price": 25, "standard_price": 12},
    {"name": "0062409-K125 Fixed Track", "categ_id": cat_map.get("Curtain Fittings", 1), "list_price": 1800, "standard_price": 950},
    {"name": "061468-K063 Track 4-5 Mtr", "categ_id": cat_map.get("Curtain Fittings", 1), "list_price": 3200, "standard_price": 1800},
    
    # Furniture
    {"name": "1/9261 Las Vegas Recliner Ivory @ 39000", "categ_id": cat_map.get("Furniture", 1), "list_price": 39000, "standard_price": 24000},
    {"name": "1/9097 Carolina Lithgow Black @ 24000", "categ_id": cat_map.get("Furniture", 1), "list_price": 24000, "standard_price": 15000},
    {"name": "Modular Office Chair Ergonomic", "categ_id": cat_map.get("Furniture", 1), "list_price": 12500, "standard_price": 7500},
    
    # Customized Furniture
    {"name": "Custom Kitchen Cabinet Set 10ft", "categ_id": cat_map.get("Customized Furniture", 1), "list_price": 85000, "standard_price": 55000},
    {"name": "Custom Built Wardrobe 6x8", "categ_id": cat_map.get("Customized Furniture", 1), "list_price": 65000, "standard_price": 40000},
    
    # Kichen & Wardrobe
    {"name": "Modular Kitchen L-Shape Standard", "categ_id": cat_map.get("Kichen & Wardrobe", 1), "list_price": 120000, "standard_price": 75000},
    {"name": "Sliding Door Wardrobe 8ft", "categ_id": cat_map.get("Kichen & Wardrobe", 1), "list_price": 55000, "standard_price": 35000},
    
    # Kichen Hardware
    {"name": "0041896-WICKER BASKET", "categ_id": cat_map.get("Kichen Hardware", 1), "list_price": 950, "standard_price": 500},
    {"name": "0041899-WICKER BASKET", "categ_id": cat_map.get("Kichen Hardware", 1), "list_price": 1100, "standard_price": 580},
    {"name": "0041906-Beech Rails", "categ_id": cat_map.get("Kichen Hardware", 1), "list_price": 750, "standard_price": 380},
    
    # Kichen Appliances
    {"name": "Built-in Chimney 60cm Auto Clean", "categ_id": cat_map.get("Kichen Appliances", 1), "list_price": 18500, "standard_price": 12000},
    {"name": "Built-in Hob 4 Burner SS", "categ_id": cat_map.get("Kichen Appliances", 1), "list_price": 14500, "standard_price": 9500},
    
    # Wallpaper
    {"name": "3D Wallpaper Premium Floral", "categ_id": cat_map.get("Wallpaper", 1), "list_price": 450, "standard_price": 220},
    {"name": "Korean Wallpaper PVC Roll 57sqft", "categ_id": cat_map.get("Wallpaper", 1), "list_price": 850, "standard_price": 420},
    
    # Carpets
    {"name": "Persian Style Carpet 6x9", "categ_id": cat_map.get("Carpets", 1), "list_price": 8500, "standard_price": 4500},
    {"name": "Shaggy Carpet 5x7 Grey", "categ_id": cat_map.get("Carpets", 1), "list_price": 4200, "standard_price": 2200},
    
    # Door Mats
    {"name": "Coir Door Mat 2x3 Natural", "categ_id": cat_map.get("Door Mats", 1), "list_price": 350, "standard_price": 180},
    {"name": "Rubber Anti-Slip Mat Large", "categ_id": cat_map.get("Door Mats", 1), "list_price": 550, "standard_price": 280},
    
    # Mattress
    {"name": "Ortho Memory Foam Mattress King", "categ_id": cat_map.get("Mattress", 1), "list_price": 22000, "standard_price": 14000},
    {"name": "Spring Mattress Queen 6inch", "categ_id": cat_map.get("Mattress", 1), "list_price": 15000, "standard_price": 9500},
    
    # Pillows
    {"name": "Memory Foam Pillow Premium", "categ_id": cat_map.get("Pillows", 1), "list_price": 1200, "standard_price": 650},
    {"name": "Microfiber Pillow Soft", "categ_id": cat_map.get("Pillows", 1), "list_price": 450, "standard_price": 220},
    
    # Cushions
    {"name": "Velvet Cushion Cover 16x16", "categ_id": cat_map.get("Cushions", 1), "list_price": 350, "standard_price": 170},
    {"name": "Embroidered Cushion Set of 5", "categ_id": cat_map.get("Cushions", 1), "list_price": 1200, "standard_price": 600},

    # Upholstery
    {"name": "Rexine Seat Cover Per Mtr", "categ_id": cat_map.get("Upholstery", 1), "list_price": 650, "standard_price": 350},
    {"name": "Premium Sofa Fabric 54inch", "categ_id": cat_map.get("Upholstery", 1), "list_price": 900, "standard_price": 480},
    
    # Furnishing Fabric
    {"name": "Blackout Lining Fabric 48inch", "categ_id": cat_map.get("Furnishing Fabric", 1), "list_price": 280, "standard_price": 140},
    {"name": "Organza Sheer Fabric White", "categ_id": cat_map.get("Furnishing Fabric", 1), "list_price": 350, "standard_price": 180},
    
    # Readymade Curtain
    {"name": "Readymade Blackout Curtain 7ft", "categ_id": cat_map.get("Readymade Curtain", 1), "list_price": 1800, "standard_price": 950},
    {"name": "Readymade Sheer Curtain White 9ft", "categ_id": cat_map.get("Readymade Curtain", 1), "list_price": 1200, "standard_price": 650},
    
    # Cleaning & Hygiene Products
    {"name": "Glass Cleaner 500ml", "categ_id": cat_map.get("Cleaning & Hygiene Products", 1), "list_price": 180, "standard_price": 95},
    {"name": "Fabric Stain Remover Spray", "categ_id": cat_map.get("Cleaning & Hygiene Products", 1), "list_price": 250, "standard_price": 130},
    
    # Designer Fans
    {"name": "BLDC Designer Ceiling Fan 48inch", "categ_id": cat_map.get("Designer Fans", 1), "list_price": 8500, "standard_price": 5200},
    
    # Indoor Pots & Plants
    {"name": "Ceramic Indoor Pot Large", "categ_id": cat_map.get("Indoor Pots", 1), "list_price": 650, "standard_price": 320},
    {"name": "Money Plant in Pot", "categ_id": cat_map.get("Indoor Plants", 1), "list_price": 350, "standard_price": 150},
    
    # Mosquito Shutters
    {"name": "Mosquaito Roller Shutter Window 4x3", "categ_id": cat_map.get("Mosquaito Shutters", 1), "list_price": 3200, "standard_price": 1800},
    
    # Wall Art
    {"name": "Canvas Abstract Wall Art 24x36", "categ_id": cat_map.get("Wall Art", 1), "list_price": 2500, "standard_price": 1200},
    
    # Home Décor
    {"name": "LED String Lights Warm White 10m", "categ_id": cat_map.get("Home Décor", 1), "list_price": 450, "standard_price": 220},
    {"name": "Decorative Vase Ceramic Tall", "categ_id": cat_map.get("Home Décor", 1), "list_price": 1200, "standard_price": 600},
    
    # Outdoor Furniture
    {"name": "Garden Chair Plastic Stackable", "categ_id": cat_map.get("Outdoor Furniture", 1), "list_price": 2200, "standard_price": 1300},
    
    # Office Furniture
    {"name": "Executive Desk 5ft Walnut", "categ_id": cat_map.get("Office Furniture", 1), "list_price": 18000, "standard_price": 11000},
    
    # Clocks
    {"name": "Wall Clock Wooden Vintage 14inch", "categ_id": cat_map.get("Clocks", 1), "list_price": 1800, "standard_price": 900},
    
    # Home Furnishing
    {"name": "Table Runner Silk 72inch", "categ_id": cat_map.get("Home Furnishing", 1), "list_price": 650, "standard_price": 320},
    
    # Wallframes
    {"name": "Photo Frame Set of 7 Black", "categ_id": cat_map.get("Wallframes", 1), "list_price": 1500, "standard_price": 750},
    
    # Crockery
    {"name": "Dinner Set 32pcs Bone China", "categ_id": cat_map.get("Crockery", 1), "list_price": 4500, "standard_price": 2500},
    
    # Some Goods category items (like client)
    {"name": "001GREY@1560", "categ_id": cat_map.get("Goods", 1), "list_price": 1560, "standard_price": 800},
    {"name": "ESS Mat (DWR)", "categ_id": cat_map.get("Goods", 1), "list_price": 3500, "standard_price": 2000},
    {"name": "1001573 Sonesse 40 RTS 3/30", "categ_id": cat_map.get("Goods", 1), "list_price": 12000, "standard_price": 7500},
    {"name": "010MB/010MW (Bouque)@1950", "categ_id": cat_map.get("Goods", 1), "list_price": 1950, "standard_price": 1100},
    
    # Raw Materials
    {"name": "MDF Board 8x4 18mm", "categ_id": cat_map.get("Raw Materials", 1), "list_price": 2800, "standard_price": 1800},
    {"name": "Plywood BWR 8x4 19mm", "categ_id": cat_map.get("Raw Materials", 1), "list_price": 3500, "standard_price": 2200},
    {"name": "Laminate Sheet 8x4 1mm", "categ_id": cat_map.get("Raw Materials", 1), "list_price": 1200, "standard_price": 750},
    {"name": "Edge Band Tape 22mm PVC", "categ_id": cat_map.get("Raw Materials", 1), "list_price": 8, "standard_price": 4},
    {"name": "Fevicol SR 998 5kg", "categ_id": cat_map.get("Raw Materials", 1), "list_price": 850, "standard_price": 550},
    
    # Services
    {"name": "Interior Design Consultation", "categ_id": cat_map.get("Services", 1), "list_price": 5000, "standard_price": 0, "type": "service"},
    {"name": "Curtain Installation Service", "categ_id": cat_map.get("Services", 1), "list_price": 1500, "standard_price": 0, "type": "service"},
    {"name": "Furniture Assembly Service", "categ_id": cat_map.get("Services", 1), "list_price": 2000, "standard_price": 0, "type": "service"},
]

for prod in sample_products:
    # In Odoo 19 saas: 'consu' = Goods (storable), 'service' = Service
    product_type = prod.pop('type', 'consu')
    if product_type == 'goods':
        product_type = 'consu'
    find_or_create('product.template',
        [['name', '=', prod['name']]],
        {**prod, 'type': product_type, 'sale_ok': True, 'purchase_ok': True},
        f"Product: {prod['name']}"
    )


# ══════════════════════════════════════════════════════════
# PHASE 6: CUSTOMERS (different names, same Kerala/India region)
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 6: CUSTOMERS")
print("═" * 70)

customers_data = [
    {
        "name": "Anoop Krishnan Nair", "is_company": False, "customer_rank": 1,
        "email": "anoop.nair@gmail.com", "phone": "9847123456",
        "street": "Sreelakshmi, TC 14/2056", "city": "Pathanamthitta",
        "state_id": KERALA_ID, "zip": "689645", "country_id": INDIA_ID,
    },
    {
        "name": "Suresh Menon", "is_company": False, "customer_rank": 1,
        "email": "suresh.menon@yahoo.com", "phone": "9495234567",
        "street": "Menon Nivas, Near Govt Hospital", "city": "Kochi",
        "state_id": KERALA_ID, "zip": "682020", "country_id": INDIA_ID,
    },
    {
        "name": "Priya Thomas", "is_company": False, "customer_rank": 1,
        "email": "priya.thomas@outlook.com", "phone": "8129345678",
        "street": "Rose Villa, Kadavanthara", "city": "Kochi",
        "state_id": KERALA_ID, "zip": "682020", "country_id": INDIA_ID,
    },
    {
        "name": "Varghese & Sons Builders", "is_company": True, "customer_rank": 1,
        "email": "info@varghesesons.in", "phone": "0468228800",
        "street": "Varghese Tower, Ring Road", "city": "Pathanamthitta",
        "state_id": KERALA_ID, "zip": "689645", "country_id": INDIA_ID,
        "vat": "32AABFV1234Q1ZP",
    },
    {
        "name": "Green Valley Residency", "is_company": True, "customer_rank": 1,
        "email": "admin@greenvalley.co.in", "phone": "04842556789",
        "street": "NH 66, Maradu Junction", "city": "Kochi",
        "state_id": KERALA_ID, "zip": "682304", "country_id": INDIA_ID,
        "vat": "32AABFG5678R1ZK",
    },
    {
        "name": "Lakshmi Devi", "is_company": False, "customer_rank": 1,
        "email": "lakshmi.devi@gmail.com", "phone": "9544456789",
        "street": "Devi Mandiram, Omalloor", "city": "Pathanamthitta",
        "state_id": KERALA_ID, "zip": "689647", "country_id": INDIA_ID,
    },
    {
        "name": "Mohammed Ashraf Interiors", "is_company": True, "customer_rank": 1,
        "email": "ashraf@ashrafinteriors.com", "phone": "9744567890",
        "street": "MG Road, Near KSRTC", "city": "Thiruvalla",
        "state_id": KERALA_ID, "zip": "689101", "country_id": INDIA_ID,
        "vat": "32AABFM8901S1ZJ",
    },
    {
        "name": "Rajan Pillai", "is_company": False, "customer_rank": 1,
        "email": "rajan.pillai@proton.me", "phone": "8589678901",
        "street": "Nandanam, Konni", "city": "Pathanamthitta",
        "state_id": KERALA_ID, "zip": "689691", "country_id": INDIA_ID,
    },
    {
        "name": "Skyline Apartments Kochi", "is_company": True, "customer_rank": 1,
        "email": "purchase@skylinekochi.com", "phone": "04842789012",
        "street": "Palarivattom Junction", "city": "Kochi",
        "state_id": KERALA_ID, "zip": "682025", "country_id": INDIA_ID,
        "vat": "32AABFS2345T1ZI",
    },
    {
        "name": "Deepa Nambiar", "is_company": False, "customer_rank": 1,
        "email": "deepa.nambiar@gmail.com", "phone": "7012890123",
        "street": "Nambiar House, Pandalam", "city": "Pathanamthitta",
        "state_id": KERALA_ID, "zip": "689501", "country_id": INDIA_ID,
    },
]

for cust in customers_data:
    find_or_create('res.partner',
        [['name', '=', cust['name']]],
        cust,
        f"Customer: {cust['name']}"
    )


# ══════════════════════════════════════════════════════════
# PHASE 7: VENDORS (mirrors the types of vendors client has)
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 7: VENDORS")
print("═" * 70)

vendors_data = [
    {
        "name": "Kerala Blinds & Curtains Pvt Ltd", "is_company": True, "supplier_rank": 1,
        "email": "sales@keralablinds.com", "phone": "04842556677",
        "street": "Industrial Area, Edappally", "city": "Kochi",
        "state_id": KERALA_ID, "zip": "682024", "country_id": INDIA_ID,
        "vat": "32AABCK1234N1ZM",
    },
    {
        "name": "Travancore Wood Industries", "is_company": True, "supplier_rank": 1,
        "email": "info@travancorewood.in", "phone": "0468225566",
        "street": "SIDCO Industrial Estate", "city": "Pathanamthitta",
        "state_id": KERALA_ID, "zip": "689645", "country_id": INDIA_ID,
        "vat": "32AABCT5678P1ZL",
    },
    {
        "name": "Malabar Furnishing Supplies", "is_company": True, "supplier_rank": 1,
        "email": "orders@malabarfurnishing.com", "phone": "04952336677",
        "street": "SM Street", "city": "Kozhikode",
        "state_id": KERALA_ID, "zip": "673001", "country_id": INDIA_ID,
        "vat": "32AABCM9012Q1ZK",
    },
    {
        "name": "Southern Mattress Factory", "is_company": True, "supplier_rank": 1,
        "email": "supply@southernmattress.com", "phone": "04712778899",
        "street": "Kazhakkoottam", "city": "Thiruvananthapuram",
        "state_id": KERALA_ID, "zip": "695582", "country_id": INDIA_ID,
        "vat": "32AABCS3456R1ZJ",
    },
    {
        "name": "Cochin Laminate House", "is_company": True, "supplier_rank": 1,
        "email": "info@cochinlaminate.com", "phone": "04842667788",
        "street": "Aluva Industrial Area", "city": "Kochi",
        "state_id": KERALA_ID, "zip": "683101", "country_id": INDIA_ID,
        "vat": "32AABCC7890S1ZI",
    },
    {
        "name": "Nizar Hardware & Tools", "is_company": True, "supplier_rank": 1,
        "email": "nizar@nizarhardware.com", "phone": "9847456789",
        "street": "Main Bazaar Road", "city": "Pathanamthitta",
        "state_id": KERALA_ID, "zip": "689645", "country_id": INDIA_ID,
        "vat": "32AABCN4567T1ZH",
    },
    {
        "name": "Decor World Imports", "is_company": True, "supplier_rank": 1,
        "email": "imports@decorworld.in", "phone": "04842889900",
        "street": "Willingdon Island", "city": "Kochi",
        "state_id": KERALA_ID, "zip": "682003", "country_id": INDIA_ID,
        "vat": "32AABCD8901U1ZG",
    },
    {
        "name": "Godrej Interio Distributor Kerala", "is_company": True, "supplier_rank": 1,
        "email": "distributor.kerala@godrejinterio.com", "phone": "04842990011",
        "street": "MG Road, Ravipuram", "city": "Kochi",
        "state_id": KERALA_ID, "zip": "682016", "country_id": INDIA_ID,
        "vat": "32AABCG2345V1ZF",
    },
]

for vendor in vendors_data:
    find_or_create('res.partner',
        [['name', '=', vendor['name']]],
        vendor,
        f"Vendor: {vendor['name']}"
    )


# ══════════════════════════════════════════════════════════
# PHASE 8: BANK JOURNALS (mirrors client's bank journals)
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 8: BANK JOURNALS")
print("═" * 70)

# For Krishnadas Group (mirrors Parappattu Group's bank journals)
bank_journals_main = [
    {"name": "Bank Fed 3185", "code": "BNK2", "type": "bank", "company_id": MAIN_COMPANY_ID},
    {"name": "Bank SIB 0388", "code": "BNK3", "type": "bank", "company_id": MAIN_COMPANY_ID},
    {"name": "Bank Yes 0024", "code": "BNK1", "type": "bank", "company_id": MAIN_COMPANY_ID},
]

# Check if BNK1 code already exists for main company (default Bank journal)
existing_bnk1 = search_read('account.journal', 
    [['code', '=', 'BNK1'], ['company_id', '=', MAIN_COMPANY_ID]], 
    ['id', 'name'])

for bj in bank_journals_main:
    # Skip BNK1 if it already exists — just rename it
    if bj['code'] == 'BNK1' and existing_bnk1:
        write('account.journal', [existing_bnk1[0]['id']], {'name': bj['name']})
        print(f"  ✅ Renamed existing BNK1 → {bj['name']}")
        continue
    
    find_or_create('account.journal',
        [['code', '=', bj['code']], ['company_id', '=', bj['company_id']]],
        bj,
        f"Journal: {bj['name']}"
    )

# Cash journal for main company — check if exists
existing_cash = search_read('account.journal', 
    [['type', '=', 'cash'], ['company_id', '=', MAIN_COMPANY_ID]], 
    ['id', 'name'])
if existing_cash:
    print(f"  ℹ️  Cash journal already exists: {existing_cash[0]['name']}")
else:
    find_or_create('account.journal',
        [['code', '=', 'CSH1'], ['company_id', '=', MAIN_COMPANY_ID]],
        {"name": "Cash", "code": "CSH1", "type": "cash", "company_id": MAIN_COMPANY_ID},
        "Journal: Cash"
    )


# ══════════════════════════════════════════════════════════
# PHASE 9: INITIAL STOCK (matches client's on-hand inventory)
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 9: INITIAL STOCK QUANTITIES")
print("═" * 70)

# Find the product IDs and location IDs we need
stock_entries = [
    {"product_name": "ESS Mat (DWR)", "location_name": "Fifth Floor", "qty": 10.0},
    {"product_name": "001GREY@1560", "location_name": "Stock", "qty": 8.0, "wh_code": "WH"},
    {"product_name": "PVC Blinds", "location_name": "Stock", "qty": 137.5, "wh_code": "WH"},
]

for entry in stock_entries:
    # Find product
    prod = search_read('product.product', [['name', '=', entry['product_name']]], ['id'], limit=1)
    if not prod:
        prod_tmpl = search_read('product.template', [['name', '=', entry['product_name']]], ['id'], limit=1)
        if prod_tmpl:
            prod = search_read('product.product', [['product_tmpl_id', '=', prod_tmpl[0]['id']]], ['id'], limit=1)
    
    if not prod:
        print(f"  ⚠️  Product '{entry['product_name']}' not found, skipping stock entry")
        continue
    
    # Find location
    loc_domain = [['name', '=', entry['location_name']], ['usage', '=', 'internal'], ['company_id', '=', MAIN_COMPANY_ID]]
    if entry.get('wh_code'):
        loc_domain.append(['complete_name', 'like', entry['wh_code']])
    
    loc = search_read('stock.location', loc_domain, ['id', 'complete_name'], limit=1)
    if not loc:
        # Broader search
        loc = search_read('stock.location', 
            [['name', '=', entry['location_name']], ['usage', '=', 'internal']], 
            ['id', 'complete_name'], limit=1)
    
    if not loc:
        print(f"  ⚠️  Location '{entry['location_name']}' not found, skipping")
        continue
    
    # Update stock quant
    try:
        existing_quant = search_read('stock.quant', 
            [['product_id', '=', prod[0]['id']], ['location_id', '=', loc[0]['id']]], 
            ['id', 'quantity'])
        
        if existing_quant:
            write('stock.quant', [existing_quant[0]['id']], {'quantity': entry['qty']})
            loc_name = loc[0]['complete_name']
            print(f"  ✅ Updated stock: {entry['product_name']} → {entry['qty']} at {loc_name}")
        else:
            quant_id = create('stock.quant', {
                'product_id': prod[0]['id'],
                'location_id': loc[0]['id'],
                'quantity': entry['qty'],
                'company_id': MAIN_COMPANY_ID,
            })
            loc_name = loc[0]['complete_name']
            print(f"  ✅ Created stock: {entry['product_name']} → {entry['qty']} at {loc_name}")
    except Exception as e:
        print(f"  ⚠️  Could not set stock for {entry['product_name']}: {e}")


# ══════════════════════════════════════════════════════════
# PHASE 10: SAMPLE PURCHASE ORDER (mirrors P00001 from client)
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 10: SAMPLE PURCHASE ORDER")
print("═" * 70)

# Get the vendor
vendor = search_read('res.partner', [['name', '=', 'Kerala Blinds & Curtains Pvt Ltd']], ['id'], limit=1)
if vendor:
    vendor_id = vendor[0]['id']
    
    # Check if PO already exists
    existing_po = search_read('purchase.order', [['partner_id', '=', vendor_id]], ['id', 'name'], limit=1)
    if existing_po:
        print(f"  ℹ️  PO already exists for this vendor: {existing_po[0]['name']}")
    else:
        # Get products for the PO
        pvc_prod = search_read('product.product', [['name', '=', 'PVC Blinds']], ['id'], limit=1)
        roller_prod = search_read('product.product', [['name', '=', '101445 Roller Blind Clutch With Chain']], ['id'], limit=1)
        venetian_prod = search_read('product.product', [['name', '=', 'Venetian Aluminium Blind 25mm']], ['id'], limit=1)
        
        try:
            po_id = create('purchase.order', {
                'partner_id': vendor_id,
                'company_id': MAIN_COMPANY_ID,
            })
            print(f"  ✅ Created Purchase Order (ID: {po_id})")
            
            # Add order lines
            if pvc_prod:
                create('purchase.order.line', {
                    'order_id': po_id,
                    'product_id': pvc_prod[0]['id'],
                    'product_qty': 50.0,
                    'price_unit': 450.0,
                    'name': 'PVC Blinds',
                })
                print("    ✅ Added line: PVC Blinds x50")
            
            if roller_prod:
                create('purchase.order.line', {
                    'order_id': po_id,
                    'product_id': roller_prod[0]['id'],
                    'product_qty': 20.0,
                    'price_unit': 180.0,
                    'name': '101445 Roller Blind Clutch With Chain',
                })
                print("    ✅ Added line: Roller Blind Clutch x20")
            
            if venetian_prod:
                create('purchase.order.line', {
                    'order_id': po_id,
                    'product_id': venetian_prod[0]['id'],
                    'product_qty': 10.0,
                    'price_unit': 950.0,
                    'name': 'Venetian Aluminium Blind 25mm',
                })
                print("    ✅ Added line: Venetian Blind x10")
            
            # Confirm the PO (like client's P00001 in 'purchase' state)
            try:
                execute('purchase.order', 'button_confirm', [[po_id]])
                print("  ✅ Purchase Order confirmed!")
            except Exception as e:
                print(f"  ⚠️  Could not confirm PO: {e}")
        
        except Exception as e:
            print(f"  ⚠️  Could not create PO: {e}")
else:
    print("  ⚠️  Vendor not found, skipping PO creation")


# ══════════════════════════════════════════════════════════
# PHASE 11: INVENTORY SETTINGS (match client's configuration)
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  PHASE 11: INVENTORY SETTINGS")
print("═" * 70)

try:
    config_id = create('res.config.settings', {
        'group_stock_multi_locations': True,    # Storage Locations: ON
        'group_stock_adv_location': False,       # Multi-Step Routes: OFF
        'group_stock_production_lot': False,      # Lots & Serial Numbers: OFF
        'group_stock_tracking_lot': False,        # Packages: OFF
        'group_stock_tracking_owner': False,      # Consignment: OFF
        'group_stock_reception_report': False,    # Reception Report: OFF
        'group_stock_sign_delivery': False,       # Signature: OFF
        'module_stock_dropshipping': False,       # Dropshipping: OFF
        'module_stock_landed_costs': False,       # Landed Costs: OFF
        'module_stock_picking_batch': False,      # Batch Transfers: OFF
    })
    execute('res.config.settings', 'execute', [[config_id]])
    print("  ✅ Inventory settings configured to match client")
except Exception as e:
    print(f"  ⚠️  Settings note: {e}")


# ══════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 70)
print("  SETUP COMPLETE — SUMMARY")
print("═" * 70)

# Count what we have
companies = search_read('res.company', [], ['name', 'parent_id'])
warehouses = search_read('stock.warehouse', [], ['name', 'code', 'company_id'])
categories = search_read('product.category', [], ['name'])
products = search_read('product.template', [], ['name'], limit=1)
prod_count = len(search('product.template', []))
customers = search_read('res.partner', [['customer_rank', '>', 0]], ['name'])
vendors = search_read('res.partner', [['supplier_rank', '>', 0]], ['name'])

print(f"""
  📊 PRACTICE DATABASE STATUS:
  ────────────────────────────
  Companies:          {len(companies)}
""")
for c in companies:
    parent = c['parent_id'][1] if c['parent_id'] else "ROOT"
    print(f"    • {c['name']} (parent: {parent})")

print(f"""
  Warehouses:         {len(warehouses)}""")
for w in warehouses:
    print(f"    • {w['name']} ({w['code']}) — {w['company_id'][1]}")

print(f"""
  Product Categories: {len(categories)}
  Products:           {prod_count}
  Customers:          {len(customers)}
  Vendors:            {len(vendors)}

  🔗 Database URL: {URL}/odoo
  
  ✅ Your practice database now mirrors your client's structure!
  
  MAPPING REFERENCE:
  ──────────────────
  Client                        → Practice
  Parappattu Group              → Krishnadas Group
  Georgeon Furniture            → Devika Furniture
  PSQUARE INTERIOR              → KDESIGN INTERIOR
  PSQUARE INTERIOR FURNISHING   → KDESIGN INTERIOR FURNISHING
  
  Same Kerala/India addresses, same warehouse structure,
  same product categories, different company & contact names.
""")
