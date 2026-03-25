"""
============================================================================
ODOO 19 — COMPLETE SETUP FOR BLOG POSTS
============================================================================
Sets up:
  A) SUBCONTRACTING — full end-to-end workflow
     - Install mrp_subcontracting
     - Create subcontractor partner
     - Create subcontracted product + components
     - Create subcontracting BOM
     - Assign resupply subcontractor route
     - Create PO, resupply, receive finished goods

  B) WORK CENTERS & ROUTING — enhanced setup
     - Add codes and tags to existing work centers
     - Configure alternative work centers
     - Create additional work centers
     - Create a NEW product with multi-step routing
     - Demonstrate work order dependencies
============================================================================
"""
import xmlrpc.client
import time
import sys

URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

print("=" * 70)
print("  ODOO 19 — BLOG SETUP: SUBCONTRACTING + WORK CENTERS & ROUTING")
print("=" * 70)

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
if not uid:
    print("Auth failed"); sys.exit(1)
print(f"  Connected — UID: {uid}")

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def ex(model, method, *a, **k):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *a, **k)

def sr(model, domain, fields, limit=0):
    kw = {'fields': fields}
    if limit: kw['limit'] = limit
    return ex(model, 'search_read', [domain], kw)

def search(model, domain, limit=0):
    kw = {}
    if limit: kw['limit'] = limit
    return ex(model, 'search', [domain], kw)

def create(model, vals):
    return ex(model, 'create', [vals])

def write(model, ids, vals):
    return ex(model, 'write', [ids, vals])

def find_or_create(model, domain, vals, label=""):
    existing = search(model, domain, limit=1)
    if existing:
        print(f"  ✅ {label or model} already exists (ID: {existing[0]})")
        return existing[0], False
    new_id = create(model, vals)
    print(f"  ✅ {label or model} created (ID: {new_id})")
    return new_id, True

# ══════════════════════════════════════════════════════════════════════
# PART A: INSTALL SUBCONTRACTING MODULE
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("  PART A: SUBCONTRACTING SETUP")
print("=" * 70)

print("\n[A1] Checking mrp_subcontracting module...")
mod = sr('ir.module.module', [['name','=','mrp_subcontracting']], ['state'])
if mod and mod[0]['state'] == 'installed':
    print("  ✅ Already installed")
else:
    print("  📦 Installing mrp_subcontracting...")
    mod_id = search('ir.module.module', [['name','=','mrp_subcontracting']], limit=1)
    if mod_id:
        try:
            ex('ir.module.module', 'button_immediate_install', [mod_id])
            print("  ✅ mrp_subcontracting installed!")
            time.sleep(10)  # Wait for module installation
        except Exception as e:
            print(f"  ⚠️  Install via button_immediate_install: {e}")
            # Try alternative method
            try:
                write('ir.module.module', mod_id, {'state': 'to install'})
                ex('base', 'update_list', [])
                print("  ⚠️  Module queued for install. May need manual trigger.")
            except Exception as e2:
                print(f"  ❌ Could not install: {e2}")

# Verify installation
time.sleep(3)
mod = sr('ir.module.module', [['name','=','mrp_subcontracting']], ['state'])
sub_installed = mod and mod[0]['state'] == 'installed'
print(f"  Module state: {mod[0]['state'] if mod else 'not found'}")

# ──────────────────────────────────────────────────────────
# A2: Create Subcontractor Partner
# ──────────────────────────────────────────────────────────
print("\n[A2] Creating Subcontractor Partner...")
subcontractor_id, _ = find_or_create('res.partner',
    [['name','=','ProAssemble Subcontractors']],
    {
        'name': 'ProAssemble Subcontractors',
        'is_company': True,
        'supplier_rank': 1,
        'street': '45 Industrial Area, Phase II',
        'city': 'Ernakulam',
        'zip': '682024',
        'country_id': search('res.country', [['code','=','IN']], limit=1)[0] if search('res.country', [['code','=','IN']], limit=1) else False,
        'phone': '+91 484 2345678',
        'email': 'info@proassemble.example.com',
    },
    label="Subcontractor: ProAssemble Subcontractors")

# Also create a second subcontractor
subcontractor2_id, _ = find_or_create('res.partner',
    [['name','=','QuickBuild Manufacturing']],
    {
        'name': 'QuickBuild Manufacturing',
        'is_company': True,
        'supplier_rank': 1,
        'street': '78 MIDC Industrial Estate',
        'city': 'Pune',
        'zip': '411026',
        'country_id': search('res.country', [['code','=','IN']], limit=1)[0] if search('res.country', [['code','=','IN']], limit=1) else False,
        'phone': '+91 20 67890123',
        'email': 'sales@quickbuild.example.com',
    },
    label="Subcontractor: QuickBuild Manufacturing")

# ──────────────────────────────────────────────────────────
# A3: Create Subcontracted Product + Components
# ──────────────────────────────────────────────────────────
print("\n[A3] Creating subcontracted product and components...")

# The subcontracted product: ErgoChair Pro (assembled by subcontractor)
ergo_chair_tmpl_id, _ = find_or_create('product.template',
    [['name','=','ErgoChair Pro (Subcontracted)']],
    {
        'name': 'ErgoChair Pro (Subcontracted)',
        'type': 'consu',
        'list_price': 15000.0,
        'standard_price': 8500.0,
        'default_code': 'ERGO-SUB-001',
        'description_sale': 'Premium ergonomic office chair assembled by speciality subcontractor',
    },
    label="Product: ErgoChair Pro (Subcontracted)")

# Components for the chair
comp_data = [
    ('Chair Frame - Aluminium', 'COMP-FRAME-AL', 2500.0),
    ('Mesh Back Panel', 'COMP-MESH-01', 1200.0),
    ('Seat Cushion - Memory Foam', 'COMP-SEAT-MF', 1800.0),
    ('Armrest Set (Pair)', 'COMP-ARM-01', 800.0),
    ('Gas Lift Cylinder', 'COMP-GAS-01', 600.0),
    ('5-Star Wheel Base', 'COMP-BASE-01', 700.0),
    ('Lumbar Support Mechanism', 'COMP-LUMB-01', 900.0),
]

comp_ids = {}
for cname, ccode, ccost in comp_data:
    cid, _ = find_or_create('product.template',
        [['default_code','=',ccode]],
        {
            'name': cname,
            'type': 'consu',
            'default_code': ccode,
            'standard_price': ccost,
            'list_price': 0.0,
        },
        label=f"Component: {cname}")
    # Get the product.product variant
    variant = sr('product.product', [['product_tmpl_id','=',cid]], ['id'], limit=1)
    comp_ids[ccode] = variant[0]['id'] if variant else cid

# Get the product variant of the finished good
ergo_variant = sr('product.product', [['product_tmpl_id','=',ergo_chair_tmpl_id]], ['id'], limit=1)
ergo_product_id = ergo_variant[0]['id'] if ergo_variant else None

# ──────────────────────────────────────────────────────────
# A4: Create Subcontracting BOM
# ──────────────────────────────────────────────────────────
print("\n[A4] Creating Subcontracting BOM...")

if sub_installed:
    # Check if BOM already exists
    existing_bom = sr('mrp.bom', [['product_tmpl_id','=',ergo_chair_tmpl_id]], ['id'])
    if existing_bom:
        print(f"  ✅ BOM already exists (ID: {existing_bom[0]['id']})")
        bom_sub_id = existing_bom[0]['id']
    else:
        bom_vals = {
            'product_tmpl_id': ergo_chair_tmpl_id,
            'product_qty': 1.0,
            'type': 'subcontract',
            'subcontractor_ids': [(6, 0, [subcontractor_id])],
            'bom_line_ids': [
                (0, 0, {'product_id': comp_ids['COMP-FRAME-AL'], 'product_qty': 1.0}),
                (0, 0, {'product_id': comp_ids['COMP-MESH-01'], 'product_qty': 1.0}),
                (0, 0, {'product_id': comp_ids['COMP-SEAT-MF'], 'product_qty': 1.0}),
                (0, 0, {'product_id': comp_ids['COMP-ARM-01'], 'product_qty': 1.0}),
                (0, 0, {'product_id': comp_ids['COMP-GAS-01'], 'product_qty': 1.0}),
                (0, 0, {'product_id': comp_ids['COMP-BASE-01'], 'product_qty': 1.0}),
                (0, 0, {'product_id': comp_ids['COMP-LUMB-01'], 'product_qty': 1.0}),
            ],
        }
        try:
            bom_sub_id = create('mrp.bom', bom_vals)
            print(f"  ✅ Subcontracting BOM created (ID: {bom_sub_id})")
        except Exception as e:
            print(f"  ❌ Error creating subcontracting BOM: {e}")
            bom_sub_id = None
else:
    print("  ⚠️  mrp_subcontracting not installed — creating as normal BOM placeholder")
    existing_bom = sr('mrp.bom', [['product_tmpl_id','=',ergo_chair_tmpl_id]], ['id'])
    if existing_bom:
        bom_sub_id = existing_bom[0]['id']
        print(f"  ✅ BOM already exists (ID: {bom_sub_id})")
    else:
        bom_vals = {
            'product_tmpl_id': ergo_chair_tmpl_id,
            'product_qty': 1.0,
            'type': 'normal',
            'bom_line_ids': [
                (0, 0, {'product_id': comp_ids['COMP-FRAME-AL'], 'product_qty': 1.0}),
                (0, 0, {'product_id': comp_ids['COMP-MESH-01'], 'product_qty': 1.0}),
                (0, 0, {'product_id': comp_ids['COMP-SEAT-MF'], 'product_qty': 1.0}),
                (0, 0, {'product_id': comp_ids['COMP-ARM-01'], 'product_qty': 1.0}),
                (0, 0, {'product_id': comp_ids['COMP-GAS-01'], 'product_qty': 1.0}),
                (0, 0, {'product_id': comp_ids['COMP-BASE-01'], 'product_qty': 1.0}),
                (0, 0, {'product_id': comp_ids['COMP-LUMB-01'], 'product_qty': 1.0}),
            ],
        }
        bom_sub_id = create('mrp.bom', bom_vals)
        print(f"  ✅ BOM created as normal type (ID: {bom_sub_id})")

# ──────────────────────────────────────────────────────────
# A5: Set Resupply Subcontractor route on components
# ──────────────────────────────────────────────────────────
print("\n[A5] Checking subcontracting routes on components...")
if sub_installed:
    sub_routes = sr('stock.route', [['name','ilike','resupply subcontract']], ['name','id'])
    if sub_routes:
        route_id = sub_routes[0]['id']
        print(f"  Found route: {sub_routes[0]['name']} (ID: {route_id})")
        for ccode, cprod_id in comp_ids.items():
            # Get the product template
            prod = sr('product.product', [['id','=',cprod_id]], ['product_tmpl_id'])
            if prod:
                tmpl_id = prod[0]['product_tmpl_id'][0]
                write('product.template', [tmpl_id], {'route_ids': [(4, route_id)]})
                print(f"    ✅ Route added to {ccode}")
    else:
        print("  ⚠️  No 'Resupply Subcontractor' route found")
else:
    print("  ⏭️  Skipping route assignment (module not installed)")

# ──────────────────────────────────────────────────────────
# A6: Add vendor info (subcontractor) to the product
# ──────────────────────────────────────────────────────────
print("\n[A6] Adding subcontractor as vendor on the product...")
if ergo_product_id:
    existing_seller = sr('product.supplierinfo', 
        [['product_tmpl_id','=',ergo_chair_tmpl_id], ['partner_id','=',subcontractor_id]], ['id'])
    if not existing_seller:
        create('product.supplierinfo', {
            'product_tmpl_id': ergo_chair_tmpl_id,
            'partner_id': subcontractor_id,
            'price': 8500.0,
            'min_qty': 1.0,
            'delay': 7,
        })
        print(f"  ✅ Vendor info created for ProAssemble Subcontractors")
    else:
        print(f"  ✅ Vendor info already exists")

# ──────────────────────────────────────────────────────────
# A7: Stock some components
# ──────────────────────────────────────────────────────────
print("\n[A7] Setting initial stock for components...")
for ccode, cprod_id in comp_ids.items():
    try:
        quant = sr('stock.quant', [['product_id','=',cprod_id],['location_id.usage','=','internal']], ['quantity'], limit=1)
        if quant and quant[0]['quantity'] > 0:
            print(f"  ✅ {ccode}: already has stock ({quant[0]['quantity']})")
        else:
            # Find internal location
            locs = sr('stock.location', [['usage','=','internal'],['name','ilike','stock']], ['id','complete_name'], limit=1)
            if locs:
                ex('stock.quant', 'create', [{
                    'product_id': cprod_id,
                    'location_id': locs[0]['id'],
                    'inventory_quantity': 50.0,
                }])
                # Apply inventory
                quants = search('stock.quant', [['product_id','=',cprod_id],['location_id','=',locs[0]['id']]])
                if quants:
                    try:
                        ex('stock.quant', 'action_apply_inventory', [quants])
                        print(f"  ✅ {ccode}: stocked 50 units")
                    except:
                        print(f"  ⚠️  {ccode}: quant created, inventory apply may need manual step")
            else:
                print(f"  ⚠️  No internal stock location found")
    except Exception as e:
        print(f"  ⚠️  {ccode}: {e}")

# ──────────────────────────────────────────────────────────
# A8: Create Purchase Order for subcontracted product
# ──────────────────────────────────────────────────────────
print("\n[A8] Creating Purchase Order for subcontracted product...")
existing_po = sr('purchase.order', [['partner_id','=',subcontractor_id]], ['name','state'])
if existing_po:
    print(f"  ✅ PO already exists: {existing_po[0]['name']} ({existing_po[0]['state']})")
else:
    if ergo_product_id:
        try:
            po_id = create('purchase.order', {
                'partner_id': subcontractor_id,
                'order_line': [(0, 0, {
                    'product_id': ergo_product_id,
                    'product_qty': 5.0,
                    'price_unit': 8500.0,
                    'name': 'ErgoChair Pro (Subcontracted) - 5 units',
                })],
            })
            print(f"  ✅ PO created (ID: {po_id})")
            # Confirm the PO
            try:
                ex('purchase.order', 'button_confirm', [[po_id]])
                print(f"  ✅ PO confirmed!")
            except Exception as e:
                print(f"  ⚠️  Could not confirm PO: {e}")
        except Exception as e:
            print(f"  ❌ Error creating PO: {e}")


# ══════════════════════════════════════════════════════════════════════
# PART B: WORK CENTERS & ROUTING ENHANCEMENT
# ══════════════════════════════════════════════════════════════════════
print("\n\n" + "=" * 70)
print("  PART B: WORK CENTERS & ROUTING ENHANCEMENT")
print("=" * 70)

# ──────────────────────────────────────────────────────────
# B1: Add codes to existing work centers
# ──────────────────────────────────────────────────────────
print("\n[B1] Adding codes & enhancing existing work centers...")

wc_updates = {
    'Cutting Station': {'code': 'CUT-01', 'time_efficiency': 95.0},
    'Assembly Line': {'code': 'ASM-01'},
    'Quality Testing': {'code': 'QC-01', 'time_efficiency': 100.0},
    'Packaging': {'code': 'PKG-01'},
}

wc_ids = {}
for wc_name, updates in wc_updates.items():
    wcs = sr('mrp.workcenter', [['name','=',wc_name]], ['id','name'])
    if wcs:
        write('mrp.workcenter', [wcs[0]['id']], updates)
        wc_ids[wc_name] = wcs[0]['id']
        print(f"  ✅ Updated {wc_name} → code: {updates.get('code','')}")
    else:
        print(f"  ⚠️  Work center '{wc_name}' not found")

# ──────────────────────────────────────────────────────────
# B2: Create NEW work centers
# ──────────────────────────────────────────────────────────
print("\n[B2] Creating additional work centers...")

new_wcs = [
    {
        'name': 'CNC Machine Station',
        'code': 'CNC-01',
        'time_efficiency': 90.0,
        'oee_target': 85.0,
        'time_start': 15.0,
        'time_stop': 10.0,
        'costs_hour': 50.0,
    },
    {
        'name': 'Painting & Finishing',
        'code': 'PNT-01',
        'time_efficiency': 100.0,
        'oee_target': 90.0,
        'time_start': 20.0,
        'time_stop': 15.0,
        'costs_hour': 40.0,
    },
    {
        'name': 'Welding Station',
        'code': 'WLD-01',
        'time_efficiency': 85.0,
        'oee_target': 80.0,
        'time_start': 10.0,
        'time_stop': 10.0,
        'costs_hour': 45.0,
    },
    {
        'name': 'Assembly Line 2',
        'code': 'ASM-02',
        'time_efficiency': 100.0,
        'oee_target': 90.0,
        'time_start': 10.0,
        'time_stop': 5.0,
        'costs_hour': 35.0,
    },
]

for wc_data in new_wcs:
    wc_id, created = find_or_create('mrp.workcenter',
        [['name','=',wc_data['name']]],
        wc_data,
        label=f"Work Center: {wc_data['name']}")
    wc_ids[wc_data['name']] = wc_id

# ──────────────────────────────────────────────────────────
# B3: Configure Alternative Work Centers
# ──────────────────────────────────────────────────────────
print("\n[B3] Configuring alternative work centers...")

# Assembly Line <-> Assembly Line 2
if 'Assembly Line' in wc_ids and 'Assembly Line 2' in wc_ids:
    asm1 = wc_ids['Assembly Line']
    asm2 = wc_ids['Assembly Line 2']
    write('mrp.workcenter', [asm1], {'alternative_workcenter_ids': [(4, asm2)]})
    write('mrp.workcenter', [asm2], {'alternative_workcenter_ids': [(4, asm1)]})
    print(f"  ✅ Assembly Line ↔ Assembly Line 2: mutual alternatives")

# ──────────────────────────────────────────────────────────
# B4: Create a NEW complex product with multi-step routing
# ──────────────────────────────────────────────────────────
print("\n[B4] Creating product with multi-step routing: Executive Standing Desk...")

desk_tmpl_id, _ = find_or_create('product.template',
    [['default_code','=','EXSD-001']],
    {
        'name': 'Executive Standing Desk',
        'type': 'consu',
        'default_code': 'EXSD-001',
        'list_price': 25000.0,
        'standard_price': 12000.0,
        'description_sale': 'Premium height-adjustable standing desk with CNC-cut wood top, welded steel frame, and premium finish',
    },
    label="Product: Executive Standing Desk")

# Components for the standing desk
desk_comps = [
    ('Solid Oak Wood Plank', 'COMP-OAK-01', 3000.0),
    ('Steel Tube Frame Set', 'COMP-STUBE-01', 2000.0),
    ('Dual Motor Lift System', 'COMP-MOTOR-02', 4000.0),
    ('Touch Control Panel', 'COMP-CTRL-02', 1500.0),
    ('Cable Management Tray', 'COMP-CABLE-01', 300.0),
    ('Premium Finish Coating', 'COMP-COAT-01', 500.0),
    ('Mounting Hardware Set', 'COMP-HDWR-02', 200.0),
]

desk_comp_ids = {}
for cname, ccode, ccost in desk_comps:
    cid, _ = find_or_create('product.template',
        [['default_code','=',ccode]],
        {
            'name': cname,
            'type': 'consu',
            'default_code': ccode,
            'standard_price': ccost,
            'list_price': 0.0,
        },
        label=f"Component: {cname}")
    variant = sr('product.product', [['product_tmpl_id','=',cid]], ['id'], limit=1)
    desk_comp_ids[ccode] = variant[0]['id'] if variant else cid

# ──────────────────────────────────────────────────────────
# B5: Create BOM with Operations (Routing)
# ──────────────────────────────────────────────────────────
print("\n[B5] Creating BOM with multi-step routing for Executive Standing Desk...")

existing_desk_bom = sr('mrp.bom', [['product_tmpl_id','=',desk_tmpl_id]], ['id'])
if existing_desk_bom:
    print(f"  ✅ BOM already exists (ID: {existing_desk_bom[0]['id']})")
else:
    # Resolve work center IDs
    def get_wc_id(name):
        wcs = sr('mrp.workcenter', [['name','=',name]], ['id'], limit=1)
        return wcs[0]['id'] if wcs else False

    operations = [
        {
            'name': 'CNC Cut Wood Top',
            'workcenter_id': get_wc_id('CNC Machine Station'),
            'time_cycle_manual': 45.0,
            'sequence': 10,
        },
        {
            'name': 'Weld Steel Frame',
            'workcenter_id': get_wc_id('Welding Station'),
            'time_cycle_manual': 60.0,
            'sequence': 20,
        },
        {
            'name': 'Sand & Prep Surface',
            'workcenter_id': get_wc_id('Cutting Station'),
            'time_cycle_manual': 30.0,
            'sequence': 30,
        },
        {
            'name': 'Apply Premium Finish',
            'workcenter_id': get_wc_id('Painting & Finishing'),
            'time_cycle_manual': 40.0,
            'sequence': 40,
        },
        {
            'name': 'Assemble Desk Components',
            'workcenter_id': get_wc_id('Assembly Line'),
            'time_cycle_manual': 50.0,
            'sequence': 50,
        },
        {
            'name': 'Install Electronics & Motor',
            'workcenter_id': get_wc_id('Assembly Line'),
            'time_cycle_manual': 35.0,
            'sequence': 60,
        },
        {
            'name': 'Quality Inspection & Testing',
            'workcenter_id': get_wc_id('Quality Testing'),
            'time_cycle_manual': 20.0,
            'sequence': 70,
        },
        {
            'name': 'Final Packaging',
            'workcenter_id': get_wc_id('Packaging'),
            'time_cycle_manual': 25.0,
            'sequence': 80,
        },
    ]

    bom_vals = {
        'product_tmpl_id': desk_tmpl_id,
        'product_qty': 1.0,
        'type': 'normal',
        'bom_line_ids': [
            (0, 0, {'product_id': desk_comp_ids['COMP-OAK-01'], 'product_qty': 1.0}),
            (0, 0, {'product_id': desk_comp_ids['COMP-STUBE-01'], 'product_qty': 1.0}),
            (0, 0, {'product_id': desk_comp_ids['COMP-MOTOR-02'], 'product_qty': 1.0}),
            (0, 0, {'product_id': desk_comp_ids['COMP-CTRL-02'], 'product_qty': 1.0}),
            (0, 0, {'product_id': desk_comp_ids['COMP-CABLE-01'], 'product_qty': 1.0}),
            (0, 0, {'product_id': desk_comp_ids['COMP-COAT-01'], 'product_qty': 1.0}),
            (0, 0, {'product_id': desk_comp_ids['COMP-HDWR-02'], 'product_qty': 1.0}),
        ],
        'operation_ids': [(0, 0, op) for op in operations],
    }

    try:
        desk_bom_id = create('mrp.bom', bom_vals)
        print(f"  ✅ BOM with 8 operations created (ID: {desk_bom_id})")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        desk_bom_id = None

# ──────────────────────────────────────────────────────────
# B6: Stock components for the standing desk
# ──────────────────────────────────────────────────────────
print("\n[B6] Setting stock for desk components...")
locs = sr('stock.location', [['usage','=','internal'],['name','ilike','stock']], ['id'], limit=1)
stock_loc_id = locs[0]['id'] if locs else None

if stock_loc_id:
    for ccode, cprod_id in desk_comp_ids.items():
        try:
            quant = sr('stock.quant', [['product_id','=',cprod_id],['location_id','=',stock_loc_id]], ['quantity'], limit=1)
            if quant and quant[0]['quantity'] > 0:
                print(f"  ✅ {ccode}: already has {quant[0]['quantity']} in stock")
            else:
                ex('stock.quant', 'create', [{
                    'product_id': cprod_id,
                    'location_id': stock_loc_id,
                    'inventory_quantity': 20.0,
                }])
                quants = search('stock.quant', [['product_id','=',cprod_id],['location_id','=',stock_loc_id]])
                if quants:
                    try:
                        ex('stock.quant', 'action_apply_inventory', [quants])
                        print(f"  ✅ {ccode}: stocked 20 units")
                    except:
                        print(f"  ⚠️  {ccode}: created, manual apply needed")
        except Exception as e:
            print(f"  ⚠️  {ccode}: {e}")

# ──────────────────────────────────────────────────────────
# B7: Create Manufacturing Order for routing demo
# ──────────────────────────────────────────────────────────
print("\n[B7] Creating Manufacturing Order for Executive Standing Desk...")
desk_variant = sr('product.product', [['product_tmpl_id','=',desk_tmpl_id]], ['id'], limit=1)
if desk_variant:
    desk_product_id = desk_variant[0]['id']
    existing_mo = sr('mrp.production', [['product_id','=',desk_product_id]], ['name','state'], limit=1)
    if existing_mo:
        print(f"  ✅ MO already exists: {existing_mo[0]['name']} ({existing_mo[0]['state']})")
    else:
        try:
            mo_id = create('mrp.production', {
                'product_id': desk_product_id,
                'product_qty': 2.0,
            })
            print(f"  ✅ MO created (ID: {mo_id})")
            # Confirm the MO
            try:
                ex('mrp.production', 'action_confirm', [[mo_id]])
                print(f"  ✅ MO confirmed!")
            except Exception as e:
                print(f"  ⚠️  Could not confirm MO: {e}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

# ══════════════════════════════════════════════════════════════════════
# FINAL VERIFICATION
# ══════════════════════════════════════════════════════════════════════
print("\n\n" + "=" * 70)
print("  FINAL VERIFICATION")
print("=" * 70)

# Work Centers
print("\n[VERIFY] Work Centers:")
all_wcs = sr('mrp.workcenter', [], ['name','code','time_efficiency','costs_hour','alternative_workcenter_ids','time_start','time_stop'])
for wc in all_wcs:
    alt_names = []
    if wc.get('alternative_workcenter_ids'):
        alts = sr('mrp.workcenter', [['id','in',wc['alternative_workcenter_ids']]], ['name'])
        alt_names = [a['name'] for a in alts]
    alt_str = f" | Alt: {', '.join(alt_names)}" if alt_names else ""
    print(f"  {wc['name']:25s} [{wc.get('code',''):6s}] Eff:{wc.get('time_efficiency',0):5.0f}% Cost:₹{wc.get('costs_hour',0):5.0f}/hr Setup:{wc.get('time_start',0):.0f}m Clean:{wc.get('time_stop',0):.0f}m{alt_str}")

# BOMs
print("\n[VERIFY] Bills of Materials:")
all_boms = sr('mrp.bom', [], ['product_tmpl_id','type','operation_ids','bom_line_ids'])
for b in all_boms:
    ops_count = len(b.get('operation_ids', []))
    lines_count = len(b.get('bom_line_ids', []))
    print(f"  {b['product_tmpl_id'][1]:45s} Type: {b['type']:12s} Comps: {lines_count} Ops: {ops_count}")

# MOs
print("\n[VERIFY] Manufacturing Orders:")
all_mos = sr('mrp.production', [], ['name','product_id','state','product_qty'], limit=10)
for mo in all_mos:
    print(f"  {mo['name']}: {mo['product_id'][1]} x {mo['product_qty']} — {mo['state']}")

print("\n" + "=" * 70)
print("  SETUP COMPLETE!")
print("=" * 70)
