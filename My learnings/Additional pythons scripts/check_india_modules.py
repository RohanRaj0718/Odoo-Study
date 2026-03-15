"""Check which Indian localization modules are currently installed on client-cient."""
import xmlrpc.client

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

# Search for all Indian localization modules
modules = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', 'like', 'l10n_in']]],
    {'fields': ['name', 'shortdesc', 'state', 'installed_version'], 'limit': 50}
)

print("=" * 80)
print("INDIAN LOCALIZATION MODULES STATUS")
print("=" * 80)
for m in sorted(modules, key=lambda x: x['name']):
    status = "✅ INSTALLED" if m['state'] == 'installed' else "❌ NOT INSTALLED" if m['state'] == 'uninstalled' else f"⚠️ {m['state']}"
    ver = m['installed_version'] or '-'
    print(f"  {status:20s} | {m['name']:35s} | {m['shortdesc']:45s} | v{ver}")

print("\n" + "=" * 80)
print("KEY MODULES FOR DELIVERY CHALLAN / E-WAY BILL:")
print("=" * 80)
key_modules = ['l10n_in', 'l10n_in_edi', 'l10n_in_ewaybill', 'l10n_in_ewaybill_stock', 'l10n_in_reports']
for km in key_modules:
    found = [m for m in modules if m['name'] == km]
    if found:
        m = found[0]
        state = m['state']
        print(f"  {m['name']:35s} → {m['shortdesc']:40s} → {state.upper()}")
    else:
        print(f"  {km:35s} → NOT FOUND in apps list")
