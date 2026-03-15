import xmlrpc.client
import sys

URL='https://demo-tech.odoo.com'; DB='demo-tech'; U='rohan.raj@infintor.com'; P='Rohanraj@1'
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, U, P, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def ex(model, method, *a, **k):
    return models.execute_kw(DB, uid, P, model, method, *a, **k)
def sr(model, domain, fields, limit=0):
    kw = {'fields': fields}
    if limit: kw['limit'] = limit
    return ex(model, 'search_read', [domain], kw)

# Check mrp_subcontracting module
print("=" * 70)
print("1. CHECK mrp_subcontracting MODULE")
print("=" * 70)
mods = sr('ir.module.module', [['name','=','mrp_subcontracting']], ['name','state','shortdesc'])
for m in mods:
    print(f"  {m['name']}: {m['state']} — {m['shortdesc']}")

# Check BOM fields for subcontracting
print("\n" + "=" * 70)
print("2. BOM SUBCONTRACTING FIELDS")
print("=" * 70)
bom_fields = ex('mrp.bom', 'fields_get', [], {'attributes': ['string','type']})
for fname in sorted(bom_fields.keys()):
    if 'subcontract' in fname.lower() or 'sub_contract' in fname.lower():
        print(f"  {fname:45s} {bom_fields[fname]['type']:15s} {bom_fields[fname]['string']}")

# 3. Work Centers
print("\n" + "=" * 70)
print("3. WORK CENTERS")
print("=" * 70)
wcs = sr('mrp.workcenter', [], ['name','code','time_efficiency','capacity_ids',
    'time_start','time_stop','costs_hour','alternative_workcenter_ids','working_state','oee_target'])
for wc in wcs:
    print(f"\n  Work Center: {wc['name']} (code: {wc.get('code','N/A')})")
    print(f"    Efficiency: {wc.get('time_efficiency',100)}% | OEE Target: {wc.get('oee_target',0)}%")
    print(f"    Setup: {wc.get('time_start',0)} min | Cleanup: {wc.get('time_stop',0)} min")
    print(f"    Cost/hr: {wc.get('costs_hour',0)} | State: {wc.get('working_state','')}")
    if wc.get('alternative_workcenter_ids'):
        alt_wcs = sr('mrp.workcenter', [['id','in',wc['alternative_workcenter_ids']]], ['name'])
        print(f"    Alternatives: {', '.join(a['name'] for a in alt_wcs)}")

# 4. BOMs
print("\n" + "=" * 70)
print("4. BILLS OF MATERIALS")
print("=" * 70)
boms = sr('mrp.bom', [], ['product_tmpl_id','type','product_qty','bom_line_ids','operation_ids'])
for b in boms:
    print(f"\n  BOM #{b['id']}: {b['product_tmpl_id'][1] if b['product_tmpl_id'] else 'N/A'}")
    print(f"    Type: {b.get('type','normal')} | Qty: {b.get('product_qty',1)}")
    if b.get('bom_line_ids'):
        lines = sr('mrp.bom.line', [['id','in', b['bom_line_ids']]], ['product_id','product_qty'])
        for l in lines:
            print(f"    Component: {l['product_id'][1]} x {l['product_qty']}")
    if b.get('operation_ids'):
        ops = sr('mrp.routing.workcenter', [['id','in', b['operation_ids']]], 
                 ['name','workcenter_id','time_cycle_manual','sequence'])
        for op in sorted(ops, key=lambda x: x.get('sequence',0)):
            wc_name = op['workcenter_id'][1] if op['workcenter_id'] else 'N/A'
            print(f"    Operation: {op['name']} @ {wc_name} ({op.get('time_cycle_manual',0)} min)")

# 5. MOs
print("\n" + "=" * 70)
print("5. MANUFACTURING ORDERS")
print("=" * 70)
mos = sr('mrp.production', [], ['name','product_id','state','product_qty'], limit=10)
for mo in mos:
    print(f"  {mo['name']}: {mo['product_id'][1]} x {mo['product_qty']} — {mo['state']}")

# 6. Subcontracting routes
print("\n" + "=" * 70)
print("6. SUBCONTRACTING ROUTES")
print("=" * 70)
try:
    routes = sr('stock.route', [['name','ilike','subcontract']], ['name','active'])
    for r in routes:
        print(f"  Route: {r['name']} (active: {r['active']})")
except Exception as e:
    print(f"  {e}")

# Sub-BOMs
sub_boms = sr('mrp.bom', [['type','=','subcontract']], ['product_tmpl_id'])
print(f"\n  Subcontracting BOMs: {len(sub_boms)}")
for sb in sub_boms:
    print(f"    - {sb['product_tmpl_id'][1]}")

# 7. Vendors
print("\n" + "=" * 70)
print("7. VENDORS")
print("=" * 70)
vendors = sr('res.partner', [['supplier_rank','>',0]], ['name','supplier_rank'], limit=20)
for v in vendors:
    print(f"  {v['name']} (rank: {v['supplier_rank']})")

# 8. Products
print("\n" + "=" * 70)
print("8. PRODUCTS")
print("=" * 70)
prods = sr('product.template', [], ['name','type','list_price','standard_price'], limit=30)
for p in prods:
    print(f"  {p['name']:45s} type={p['type']:10s} sale={p.get('list_price',0):8.2f} cost={p.get('standard_price',0):8.2f}")

# 9. Purchase Orders
print("\n" + "=" * 70)
print("9. PURCHASE ORDERS")
print("=" * 70)
pos = sr('purchase.order', [], ['name','partner_id','state','amount_total'], limit=10)
for po in pos:
    print(f"  {po['name']}: {po['partner_id'][1]} — {po['state']} — {po.get('amount_total',0)}")

print("\n\nDONE!")
