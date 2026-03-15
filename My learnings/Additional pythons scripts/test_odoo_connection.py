"""
Test connection to Odoo database via XML-RPC API
"""
import xmlrpc.client

# Odoo connection details
URL = "https://demo-company15.odoo.com"
DB = "demo-company15"  # On Odoo Online, DB name is usually the subdomain
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

print("=" * 60)
print("TESTING ODOO XML-RPC CONNECTION")
print("=" * 60)

# Step 1: Test common endpoint (version info)
print("\n[1] Testing server connection...")
try:
    common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
    version = common.version()
    print(f"    ✅ Connected! Odoo Version: {version.get('server_version', 'unknown')}")
except Exception as e:
    print(f"    ❌ Connection failed: {e}")
    print("    Trying without SSL verification...")
    import ssl
    context = ssl._create_unverified_context()
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True, context=context)
        version = common.version()
        print(f"    ✅ Connected (no SSL verify)! Version: {version.get('server_version', 'unknown')}")
    except Exception as e2:
        print(f"    ❌ Still failed: {e2}")
        exit(1)

# Step 2: Authenticate
print("\n[2] Authenticating...")
db_names_to_try = ["demo-company15", "Demo-Company", "demo-company15-main-18013460"]
uid = None
used_db = None

for db_name in db_names_to_try:
    try:
        uid = common.authenticate(db_name, USERNAME, PASSWORD, {})
        if uid:
            used_db = db_name
            print(f"    ✅ Authenticated! UID: {uid}, Database: {db_name}")
            break
        else:
            print(f"    ❌ Auth failed with DB: {db_name} (wrong credentials or DB name)")
    except Exception as e:
        print(f"    ❌ Error with DB '{db_name}': {e}")

if not uid:
    print("\n    ❌ Could not authenticate with any database name.")
    print("    Please check:")
    print("    1. Is the URL correct? (demo-company15.odoo.com)")
    print("    2. What is the exact database name?")
    print("    3. Are the credentials correct?")
    print("\n    TIP: The database name for Odoo Online is usually")
    print("    the subdomain (e.g., 'demo-company15')")
    exit(1)

# Step 3: Test API access
print("\n[3] Testing API access...")
try:
    models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)
    
    # Try to read the user's own info
    user_info = models.execute_kw(used_db, uid, PASSWORD,
        'res.users', 'read', [uid], {'fields': ['name', 'email', 'company_id']})
    
    if user_info:
        user = user_info[0]
        print(f"    ✅ API working!")
        print(f"    User: {user.get('name', 'N/A')}")
        print(f"    Email: {user.get('email', 'N/A')}")
        company = user.get('company_id', [False, 'N/A'])
        if isinstance(company, list):
            print(f"    Company: {company[1]}")
        else:
            print(f"    Company: {company}")
except Exception as e:
    print(f"    ❌ API test failed: {e}")
    exit(1)

# Step 4: Check available modules
print("\n[4] Checking installed modules...")
try:
    modules = models.execute_kw(used_db, uid, PASSWORD,
        'ir.module.module', 'search_read',
        [[['state', '=', 'installed'], ['name', 'in', ['account', 'sale', 'purchase', 'stock']]]],
        {'fields': ['name', 'shortdesc', 'state']})
    
    for mod in modules:
        print(f"    ✅ {mod['shortdesc']} ({mod['name']}) - {mod['state']}")
    
    installed_names = [m['name'] for m in modules]
    if 'account' not in installed_names:
        print("    ⚠️  Accounting NOT installed - will need to install it")
    if 'sale' not in installed_names:
        print("    ⚠️  Sales NOT installed - will need to install it")
    if 'purchase' not in installed_names:
        print("    ⚠️  Purchase NOT installed - will need to install it")
        
except Exception as e:
    print(f"    ⚠️  Could not check modules: {e}")

# Step 5: Check if bank journal exists
print("\n[5] Checking bank journal...")
try:
    journals = models.execute_kw(used_db, uid, PASSWORD,
        'account.journal', 'search_read',
        [[['type', '=', 'bank']]],
        {'fields': ['name', 'code', 'type']})
    
    if journals:
        for j in journals:
            print(f"    ✅ Bank Journal: {j['name']} (Code: {j['code']})")
    else:
        print("    ⚠️  No bank journal found - will create one")
except Exception as e:
    print(f"    ⚠️  Could not check journals: {e}")

print("\n" + "=" * 60)
print("CONNECTION TEST COMPLETE")
print("=" * 60)
print(f"\nDatabase: {used_db}")
print(f"UID: {uid}")
print("Ready to create practice data!")
