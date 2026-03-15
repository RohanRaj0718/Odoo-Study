"""Check all locations, transit locations, and test inter-branch transfer feasibility"""
import xmlrpc.client

URL='https://client-cient.odoo.com'; DB='client-cient'; U='rohan.raj@infintor.com'; P='Rohanraj@1'
common=xmlrpc.client.ServerProxy(URL+'/xmlrpc/2/common',allow_none=True)
uid=common.authenticate(DB,U,P,{})
models=xmlrpc.client.ServerProxy(URL+'/xmlrpc/2/object',allow_none=True)

def sr(m,d,f,limit=0):
    kw = {'fields':f}
    if limit: kw['limit'] = limit
    return models.execute_kw(DB,uid,P,m,'search_read',[d],kw)

def search(m,d):
    return models.execute_kw(DB,uid,P,m,'search',[d])

print("=" * 80)
print("  LOCATION ANALYSIS FOR INTER-BRANCH TRANSFERS")
print("=" * 80)

# 1. ALL locations
print("\n📍 ALL LOCATIONS:")
locs = sr('stock.location', [], ['name','complete_name','usage','company_id','active'])
for loc in sorted(locs, key=lambda x: x['complete_name']):
    co = loc['company_id'][1] if loc['company_id'] else '** NO COMPANY **'
    marker = " ⭐" if loc['usage'] == 'transit' else ""
    marker = " 🔄" if 'inter' in loc['name'].lower() else marker
    print(f"  [{loc['id']:3d}] {loc['complete_name']:55s} | {loc['usage']:12s} | {co}{marker}")

# 2. Transit locations specifically
print("\n🚚 TRANSIT LOCATIONS:")
transit = [l for l in locs if l['usage'] == 'transit']
if transit:
    for t in transit:
        co = t['company_id'][1] if t['company_id'] else '** NO COMPANY **'
        print(f"  [{t['id']:3d}] {t['complete_name']:55s} | {co}")
else:
    print("  None found!")

# 3. Check for inactive transit locations
print("\n🔍 INACTIVE TRANSIT LOCATIONS:")
inactive_transit = sr('stock.location', [['usage','=','transit'],['active','=',False]], 
                       ['name','complete_name','usage','company_id','active'])
if inactive_transit:
    for t in inactive_transit:
        co = t['company_id'][1] if t['company_id'] else '** NO COMPANY **'
        print(f"  [{t['id']:3d}] {t['complete_name']:55s} | {co} (INACTIVE)")
else:
    print("  None found!")

# 4. Intercompany transit specifically
print("\n🔄 INTERCOMPANY-RELATED LOCATIONS:")
inter = [l for l in locs if 'inter' in l['name'].lower() or 'inter' in l['complete_name'].lower()]
if inter:
    for i in inter:
        co = i['company_id'][1] if i['company_id'] else '** NO COMPANY **'
        print(f"  [{i['id']:3d}] {i['complete_name']:55s} | {i['usage']:12s} | {co}")
else:
    print("  None found by name. Checking location fields...")
    # Check all location fields for transit-related ones
    all_fields = models.execute_kw(DB,uid,P,'stock.location','fields_get',[],
                                    {'attributes':['string','type']})
    transit_fields = {k:v for k,v in all_fields.items() 
                      if 'transit' in k.lower() or 'transit' in v.get('string','').lower()
                      or 'inter' in k.lower() or 'inter' in v.get('string','').lower()}
    for fname, finfo in transit_fields.items():
        print(f"  Field: {fname} → {finfo['string']} ({finfo['type']})")

# 5. Check warehouse transit locations
print("\n🏭 WAREHOUSE TRANSIT LOCATIONS (from warehouse config):")
whs = sr('stock.warehouse', [], ['name','code','company_id','lot_stock_id'])
for w in whs:
    co = w['company_id'][1] if w['company_id'] else 'N/A'
    print(f"  {w['name']} ({w['code']}) — Company: {co}")

# 6. Check inter-warehouse route/rules
print("\n📋 STOCK RULES (push/pull) related to transit:")
rules = sr('stock.rule', [], ['name','action','location_src_id','location_dest_id','company_id'])
for r in rules:
    src = r['location_src_id'][1] if r['location_src_id'] else 'N/A'
    dest = r['location_dest_id'][1] if r['location_dest_id'] else 'N/A'
    co = r['company_id'][1] if r['company_id'] else 'N/A'
    if 'transit' in src.lower() or 'transit' in dest.lower() or 'inter' in src.lower() or 'inter' in dest.lower():
        print(f"  {r['name']:50s} | {src} → {dest} | {co}")

# 7. Check what "usage" options exist for locations
print("\n📊 LOCATION USAGE TYPES in this database:")
usage_map = {}
for loc in locs:
    u = loc['usage']
    if u not in usage_map:
        usage_map[u] = 0
    usage_map[u] += 1
for u, count in sorted(usage_map.items()):
    print(f"  {u}: {count} locations")

# 8. Look for virtual locations (Partners, Scrap, etc.)
print("\n🔮 VIRTUAL/SPECIAL LOCATIONS:")
virtual = [l for l in locs if l['usage'] in ('transit', 'inventory', 'production', 'supplier', 'customer')]
for v in sorted(virtual, key=lambda x: x['usage']):
    co = v['company_id'][1] if v['company_id'] else '** NO COMPANY **'
    print(f"  [{v['id']:3d}] {v['complete_name']:55s} | {v['usage']:12s} | {co}")

print("\n" + "=" * 80)
print("  CONCLUSION")
print("=" * 80)
