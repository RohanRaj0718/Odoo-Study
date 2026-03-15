"""
Deep verification: Check all MOs, WOs, quality points, and WC details in company 2.
"""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def x(model, method, *args, **kw):
    return models.execute_kw(DB, uid, PASSWORD, model, method, *args, **kw)

def sr(model, domain, fields, limit=100):
    return x(model, 'search_read', [domain], {'fields': fields, 'limit': limit})

COMPANY = 2

# ── ALL MOs ──
print("=== ALL MANUFACTURING ORDERS (company 2) ===")
mos = sr('mrp.production', [['company_id', '=', COMPANY]], 
         ['name', 'state', 'product_id', 'workorder_ids', 'qty_producing', 'product_qty'])
for mo in mos:
    print(f"  [{mo['id']}] {mo['name']} | state={mo['state']} | product={mo['product_id'][1]} | qty={mo['product_qty']} | WOs={mo['workorder_ids']}")

# ── ALL WORK ORDERS ──
print("\n=== ALL WORK ORDERS (company 2) ===")
wos = sr('mrp.workorder', [['company_id', '=', COMPANY]], 
         ['name', 'state', 'workcenter_id', 'production_id', 'duration_expected', 'duration',
          'qty_producing', 'qty_produced', 'blocked_by_workorder_ids'])
for wo in wos:
    print(f"  [{wo['id']}] {wo['name']} | state={wo['state']} | WC={wo['workcenter_id'][1] if wo['workcenter_id'] else 'N/A'}")
    print(f"    MO={wo['production_id'][1] if wo['production_id'] else 'N/A'} | duration_expected={wo['duration_expected']}min")
    if wo.get('blocked_by_workorder_ids'):
        print(f"    blocked_by: {wo['blocked_by_workorder_ids']}")

# ── WORK CENTER DETAILS ──
print("\n=== WORK CENTER DETAILS (company 2) ===")
wcs = sr('mrp.workcenter', [['company_id', '=', COMPANY]], 
         ['name', 'code', 'resource_calendar_id', 'capacity_ids', 'employee_ids',
          'time_start', 'time_stop', 'oee_target', 'working_state'])
for wc in wcs:
    print(f"\n  [{wc['id']}] {wc['name']} (code={wc.get('code', 'N/A')})")
    print(f"    Working Hours: {wc['resource_calendar_id']}")
    print(f"    Capacity IDs: {wc['capacity_ids']}")
    print(f"    Employees: {wc['employee_ids']}")
    print(f"    Setup time: {wc['time_start']}min | Cleanup: {wc['time_stop']}min")
    print(f"    OEE Target: {wc['oee_target']}%")
    print(f"    Working State: {wc['working_state']}")

# ── CHECK ALL WORK CENTERS (including company 1) ──
print("\n=== ALL WORK CENTERS (all companies) ===")
all_wcs = sr('mrp.workcenter', [], ['name', 'company_id', 'code'])
for wc in all_wcs:
    print(f"  [{wc['id']}] {wc['name']} | company={wc['company_id']}")

# ── QUALITY POINTS ──
print("\n=== QUALITY POINTS ===")
try:
    qps = sr('quality.point', [], ['name', 'title', 'test_type_id', 'operation_id', 'product_ids', 'company_id'])
    for qp in qps:
        print(f"  [{qp['id']}] {qp.get('title', qp.get('name', 'N/A'))} | type={qp['test_type_id']} | operation={qp['operation_id']}")
except Exception as e:
    print(f"  Error: {e}")

# ── QUALITY TEST TYPES ──
print("\n=== QUALITY TEST TYPES ===")
try:
    ttypes = sr('quality.point.test_type', [], ['name', 'technical_name'])
    for tt in ttypes:
        print(f"  [{tt['id']}] {tt['name']} (tech={tt.get('technical_name', 'N/A')})")
except Exception as e:
    print(f"  Error: {e}")

# ── CHECK WO STATES (selection values) ──
print("\n=== WORK ORDER STATE SELECTION ===")
wo_fields = x('mrp.workorder', 'fields_get', [['state']], {'attributes': ['selection']})
if 'state' in wo_fields:
    for val, label in wo_fields['state']['selection']:
        print(f"  '{val}' → {label}")

# ── CHECK MO STATES ──
print("\n=== MO STATE SELECTION ===")
mo_fields = x('mrp.production', 'fields_get', [['state']], {'attributes': ['selection']})
if 'state' in mo_fields:
    for val, label in mo_fields['state']['selection']:
        print(f"  '{val}' → {label}")

# ── Check employee PINs ──
print("\n=== EMPLOYEES WITH PINS ===")
try:
    emps = sr('hr.employee', [['company_id', '=', COMPANY]], ['name', 'pin', 'barcode'])
    for emp in emps:
        has_pin = bool(emp.get('pin'))
        has_barcode = bool(emp.get('barcode'))
        print(f"  [{emp['id']}] {emp['name']} | PIN={'set' if has_pin else 'not set'} | barcode={'set' if has_barcode else 'not set'}")
except Exception as e:
    print(f"  Error: {e}")

# ── MRP Display fields (shop floor related) ──
print("\n=== MRP WORKCENTER FIELDS FOR SHOP FLOOR ===")
wc_fields = x('mrp.workcenter', 'fields_get', [], {'attributes': ['string', 'type']})
for fname, fdata in sorted(wc_fields.items()):
    if any(kw in fname.lower() or kw in fdata['string'].lower() for kw in ['display', 'shop', 'floor', 'oee', 'performance', 'productivity']):
        print(f"  {fname}: {fdata['string']} ({fdata['type']})")

print("\n=== DONE ===")
