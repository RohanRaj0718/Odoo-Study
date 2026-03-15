"""
Inspect Odoo 19 database for Manufacturing setup:
- Work Centers, BOMs, Operations/Routing
- Subcontracting configuration
- Products, Vendors
"""
import xmlrpc.client
import sys

URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

print("=" * 70)
print("  INSPECTING ODOO 19 DATABASE - MANUFACTURING SETUP")
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

# 1. Check installed modules
print("\n" + "=" * 70)
print("1. INSTALLED MFG-RELATED MODULES")
print("=" * 70)
mods = sr('ir.module.module', [['state','=','installed'], ['name','in',
    ['mrp','mrp_subcontracting','mrp_workorder','quality_control','maintenance',
     'purchase','sale_management','stock','mrp_plm']]], 
    ['name','shortdesc','state'])
for m in mods:
    print(f"  ✅ {m['name']:30s} — {m['shortdesc']}")

# 2. Check MRP settings
print("\n" + "=" * 70)
print("2. MRP SETTINGS (subcontracting, work orders)")
print("=" * 70)
try:
    settings = sr('res.config.settings', [], ['group_mrp_routings', 'module_mrp_subcontracting'], limit=1)
    if settings:
        for k,v in settings[0].items():
            if k != 'id':
                print(f"  {k}: {v}")
    else:
        print("  No settings record found — checking ir.config_parameter")
except Exception as e:
    print(f"  Error reading settings: {e}")

# Check config params
try:
    params = sr('ir.config_parameter', [['key','ilike','mrp']], ['key','value'])
    for p in params:
        print(f"  param: {p['key']} = {p['value']}")
except:
    pass

# 3. Work Centers
print("\n" + "=" * 70)
print("3. WORK CENTERS")
print("=" * 70)
wcs = sr('mrp.workcenter', [], ['name','code','time_efficiency','capacity',
    'time_start','time_stop','costs_hour','alternative_workcenter_ids','working_state'])
if wcs:
    for wc in wcs:
        print(f"\n  📍 {wc['name']} (code: {wc.get('code','N/A')})")
        print(f"     Efficiency: {wc.get('time_efficiency',100)}% | Capacity: {wc.get('capacity',1)}")
        print(f"     Setup: {wc.get('time_start',0)} min | Cleanup: {wc.get('time_stop',0)} min")
        print(f"     Cost/hr: {wc.get('costs_hour',0)} | State: {wc.get('working_state','')}")
        if wc.get('alternative_workcenter_ids'):
            alt_wcs = sr('mrp.workcenter', [['id','in',wc['alternative_workcenter_ids']]], ['name'])
            alts = [a['name'] for a in alt_wcs]
            print(f"     Alternatives: {', '.join(alts)}")
else:
    print("  ❌ No work centers found")

# 4. Bill of Materials
print("\n" + "=" * 70)
print("4. BILLS OF MATERIALS")
print("=" * 70)
boms = sr('mrp.bom', [], ['product_tmpl_id','type','product_qty','subcontractor_ids','bom_line_ids','operation_ids'])
if boms:
    for b in boms:
        btype = b.get('type','normal')
        print(f"\n  📋 BOM #{b['id']}: {b['product_tmpl_id'][1] if b['product_tmpl_id'] else 'N/A'}")
        print(f"     Type: {btype} | Qty: {b.get('product_qty',1)}")
        if btype == 'subcontract' and b.get('subcontractor_ids'):
            subs = sr('res.partner', [['id','in',b['subcontractor_ids']]], ['name'])
            print(f"     Subcontractors: {', '.join(s['name'] for s in subs)}")
        
        # Components
        if b.get('bom_line_ids'):
            lines = sr('mrp.bom.line', [['id','in', b['bom_line_ids']]], ['product_id','product_qty'])
            for l in lines:
                print(f"     Component: {l['product_id'][1]} x {l['product_qty']}")
        
        # Operations
        if b.get('operation_ids'):
            ops = sr('mrp.routing.workcenter', [['id','in', b['operation_ids']]], 
                     ['name','workcenter_id','time_cycle_manual','sequence'])
            for op in sorted(ops, key=lambda x: x.get('sequence',0)):
                print(f"     Operation: {op['name']} @ {op['workcenter_id'][1] if op['workcenter_id'] else 'N/A'} ({op.get('time_cycle_manual',0)} min)")
else:
    print("  ❌ No BOMs found")

# 5. Manufacturing Orders
print("\n" + "=" * 70)
print("5. MANUFACTURING ORDERS (recent)")
print("=" * 70)
mos = sr('mrp.production', [], ['name','product_id','state','product_qty','date_start'], limit=10)
for mo in mos:
    print(f"  {mo['name']}: {mo['product_id'][1]} x {mo['product_qty']} — {mo['state']}")

# 6. Subcontracting-related products and routes
print("\n" + "=" * 70)
print("6. SUBCONTRACTING ROUTES & PRODUCTS")
print("=" * 70)
try:
    sub_routes = sr('stock.route', [['name','ilike','subcontract']], ['name','active'])
    for r in sub_routes:
        print(f"  Route: {r['name']} (active: {r['active']})")
except:
    print("  No subcontracting routes found")

# Check for subcontracting BOMs
sub_boms = sr('mrp.bom', [['type','=','subcontract']], ['product_tmpl_id','subcontractor_ids'])
if sub_boms:
    print(f"\n  Found {len(sub_boms)} subcontracting BOM(s):")
    for sb in sub_boms:
        print(f"    - {sb['product_tmpl_id'][1] if sb['product_tmpl_id'] else 'N/A'}")
else:
    print("\n  No subcontracting BOMs found yet")

# 7. Vendors/Partners related to subcontracting
print("\n" + "=" * 70)
print("7. VENDORS/SUPPLIERS")
print("=" * 70)
vendors = sr('res.partner', [['supplier_rank','>',0]], ['name','supplier_rank','city'], limit=20)
for v in vendors:
    print(f"  {v['name']} (rank: {v['supplier_rank']}) — {v.get('city','')}")

# 8. Products (finished goods)
print("\n" + "=" * 70)
print("8. PRODUCTS (Storable)")
print("=" * 70)
prods = sr('product.template', [['type','=','consu']], ['name','type','categ_id','list_price','standard_price'], limit=30)
if not prods:
    prods = sr('product.template', [], ['name','type','categ_id','list_price','standard_price'], limit=30)
for p in prods:
    cat = p['categ_id'][1] if p['categ_id'] else ''
    print(f"  {p['name']:40s} | Type: {p['type']:10s} | Cat: {cat} | Sale: {p.get('list_price',0)} | Cost: {p.get('standard_price',0)}")

# 9. Check for purchase orders from subcontractors
print("\n" + "=" * 70)
print("9. PURCHASE ORDERS (recent)")
print("=" * 70)
pos = sr('purchase.order', [], ['name','partner_id','state','amount_total','date_order'], limit=10)
for po in pos:
    print(f"  {po['name']}: {po['partner_id'][1]} — {po['state']} — {po.get('amount_total',0)}")

print("\n" + "=" * 70)
print("INSPECTION COMPLETE")
print("=" * 70)
