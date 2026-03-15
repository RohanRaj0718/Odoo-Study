"""
Install Recruitment Module and Website HR Recruitment in Demo Database
"""
import xmlrpc.client
import time

URL = 'https://demo-tech.odoo.com'
DB = 'demo-tech'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
print(f'Authenticated: uid={uid}')

models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

# Install hr_recruitment
print("\n=== Installing hr_recruitment module ===")
mod_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search',
    [[['name', '=', 'hr_recruitment']]])
if mod_ids:
    print(f"  Module ID: {mod_ids[0]}")
    try:
        models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'button_immediate_install', [mod_ids])
        print("  hr_recruitment installed successfully!")
    except Exception as e:
        print(f"  Install error: {e}")
        print("  Trying alternative install method...")
        try:
            models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'button_install', [mod_ids])
            print("  Install triggered, waiting for it to complete...")
            time.sleep(15)
        except Exception as e2:
            print(f"  Alternative method error: {e2}")

# Verify installation
print("\n=== Verifying installation ===")
# Re-authenticate after module install
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
mods = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', 'in', ['hr_recruitment', 'website_hr_recruitment']]]], 
    {'fields': ['name', 'state']})
for m in mods:
    print(f"  {m['name']}: {m['state']}")

print("\nDone!")
