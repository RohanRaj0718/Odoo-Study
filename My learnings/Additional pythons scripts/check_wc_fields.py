"""Check actual work center field names in Odoo 19"""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)

def fields_get(model):
    return models.execute_kw(DB, uid, PASSWORD, model, 'fields_get',
                             [], {'attributes': ['string', 'type', 'help']})

# Work center fields
print("=" * 60)
print("WORK CENTER FIELDS (mrp.workcenter)")
print("=" * 60)
wc_fields = fields_get('mrp.workcenter')
for fname, fdata in sorted(wc_fields.items()):
    if fdata['type'] not in ('one2many', 'many2many', 'binary'):
        print(f"  {fname:40s} {fdata['type']:12s} {fdata['string']}")

print("\n" + "=" * 60)
print("CAPACITY-RELATED FIELDS")
print("=" * 60)
for fname, fdata in wc_fields.items():
    if 'capaci' in fname.lower() or 'capaci' in fdata['string'].lower():
        print(f"  {fname}: {fdata['string']} ({fdata['type']})")
        if fdata.get('help'):
            print(f"    Help: {fdata['help']}")

print("\n" + "=" * 60)
print("MRP PRODUCTION FIELDS (key ones)")
print("=" * 60)
mo_fields = fields_get('mrp.production')
for key in ['state', 'date_start', 'date_finished', 'product_id', 'product_qty', 
            'qty_produced', 'workorder_ids', 'reservation_state', 'availability']:
    if key in mo_fields:
        f = mo_fields[key]
        print(f"  {key:30s} {f['type']:12s} {f['string']}")
