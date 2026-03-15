"""Quick check: POS & India modules status in client DB"""
import xmlrpc.client
URL = "https://psi-122test.odoo.com"
DB = "psi-122test"
USERNAME = "georgey@psquareinterior.com"
PASSWORD = "Psquare@1"

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def sr(model, domain, fields, limit=100):
    return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], {'fields': fields, 'limit': limit})

# Check POS and India modules
modules_to_check = [
    'point_of_sale', 'l10n_in', 'l10n_in_edi', 'l10n_in_ewaybill', 
    'l10n_in_reports', 'l10n_in_ewaybill_stock', 'pos_sale',
    'pos_loyalty', 'pos_discount', 'pos_restaurant', 'pos_hr',
    'pos_mercury', 'pos_stripe', 'pos_adyen', 'pos_razorpay',
    'pos_pine_labs', 'whatsapp', 'sms'
]

print("=" * 70)
print("MODULE STATUS CHECK")
print("=" * 70)

for mod_name in modules_to_check:
    result = sr('ir.module.module', [['name', '=', mod_name]], ['name', 'shortdesc', 'state'])
    if result:
        m = result[0]
        status = "✅ INSTALLED" if m['state'] == 'installed' else f"❌ {m['state'].upper()}"
        print(f"  {m['name']:30s} {m['shortdesc']:40s} {status}")
    else:
        print(f"  {mod_name:30s} {'NOT FOUND':40s}")

# Check Razorpay specifically (popular in India)
print("\n" + "=" * 70)
print("PAYMENT TERMINALS AVAILABLE")
print("=" * 70)

terminal_modules = sr('ir.module.module', 
    [['name', 'like', 'pos_%'], ['category_id.name', 'like', '%Sale%']], 
    ['name', 'shortdesc', 'state'], limit=50)

for m in sorted(terminal_modules, key=lambda x: x['name']):
    status = "✅" if m['state'] == 'installed' else "❌"
    print(f"  {status} {m['name']:35s} {m['shortdesc'][:40]:40s} ({m['state']})")

# Check current payment methods
print("\n" + "=" * 70)
print("CURRENT PAYMENT METHODS")
print("=" * 70)

try:
    pms = sr('account.payment.method', [], ['name', 'payment_type'])
    for p in pms:
        print(f"  {p['name']} ({p['payment_type']})")
except Exception as e:
    print(f"  Error: {e}")

# Check installed Indian localization details
print("\n" + "=" * 70)
print("INDIA LOCALIZATION — INSTALLED FEATURES")
print("=" * 70)

india_modules = sr('ir.module.module', 
    [['name', 'like', 'l10n_in%'], ['state', '=', 'installed']], 
    ['name', 'shortdesc', 'state'])
if india_modules:
    for m in india_modules:
        print(f"  ✅ {m['name']:30s} {m['shortdesc']}")
else:
    print("  No Indian modules installed!")

# Also check for any l10n_in modules available but not installed
india_available = sr('ir.module.module', 
    [['name', 'like', 'l10n_in%'], ['state', '!=', 'installed']], 
    ['name', 'shortdesc', 'state'])
if india_available:
    print("\n  Available but NOT installed:")
    for m in india_available:
        print(f"  ❌ {m['name']:30s} {m['shortdesc']:40s} ({m['state']})")

print("\n✅ Check complete!")
