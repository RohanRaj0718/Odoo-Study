"""Debug single internal transfer creation in Odoo 19."""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

def ex(mod, met, *a, **k):
    return models.execute_kw(DB, uid, PASSWORD, mod, met, *a, **k)

def sex(mod, met, *a, **k):
    try:
        return models.execute_kw(DB, uid, PASSWORD, mod, met, *a, **k)
    except xmlrpc.client.Fault as e:
        if 'cannot marshal None' in str(e):
            return True
        raise

def sr(mod, d, f):
    return ex(mod, 'search_read', [d], {'fields': f, 'limit': 50})

print("Creating picking...")
pick_id = ex('stock.picking', 'create', [{
    'picking_type_id': 7,
    'location_id': 5,
    'location_dest_id': 28,
    'company_id': 1,
}])
print(f"Picking: {pick_id}")

print("Creating move (no 'name' field)...")
move_id = ex('stock.move', 'create', [{
    'product_id': 109,
    'product_uom_qty': 5.0,
    'location_id': 5,
    'location_dest_id': 28,
    'picking_id': pick_id,
    'company_id': 1,
}])
print(f"Move: {move_id}")

print("Confirming...")
sex('stock.picking', 'action_confirm', [[pick_id]])
print("Confirmed")

print("Setting qty done...")
ex('stock.move', 'write', [[move_id], {'quantity': 5.0}])
print("Qty set")

print("Validating...")
try:
    res = ex('stock.picking', 'button_validate', [[pick_id]])
    print(f"Validate result: {res}")
except xmlrpc.client.Fault as e:
    if 'cannot marshal None' in str(e):
        print("Validated (returned None)")
    else:
        print(f"Validate error: {str(e)[:200]}")

# Check state
pick = sr('stock.picking', [['id', '=', pick_id]], ['name', 'state'])
print(f"Pick state: {pick}")

mv = sr('stock.move', [['id', '=', move_id]], ['state', 'account_move_id', 'quantity'])
print(f"Move: {mv}")
if mv:
    je = mv[0].get('account_move_id')
    print(f"JE linked: {je}")
