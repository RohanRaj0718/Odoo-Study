import xmlrpc.client

URL = "https://rohanraj0718-infintor.odoo.com"
DB = "rohanraj0718-infintor-main-29796979"
USERNAME = "rohanraj.infintor@gmail.com"
PASSWORD = "Virat@ronaldo1"

try:
    print(f"Connecting to {URL} with DB {DB} as {USERNAME}...")
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(URL))
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    
    if uid:
        print(f"SUCCESS! Logged in with UID: {uid}")
    else:
        print("FAILED: Authentication returned False (Invalid credentials).")
except Exception as e:
    print(f"ERROR: {e}")
