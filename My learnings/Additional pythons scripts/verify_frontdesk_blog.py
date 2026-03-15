"""
Verify BLOG_FrontDesk_PUBLISH_READY_V2.md against the demo database.
Confirms every claim made in the blog is correct.
"""
import xmlrpc.client

URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
print(f"✅ Authenticated: uid={uid}")

models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

passed = 0
failed = 0

def check(description, condition):
    global passed, failed
    if condition:
        print(f"  ✅ PASS: {description}")
        passed += 1
    else:
        print(f"  ❌ FAIL: {description}")
        failed += 1

# ============================================================
# 1. Frontdesk module is installed
# ============================================================
print("\n=== 1. Module Installation ===")
mod = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read', 
    [[['name', '=', 'frontdesk']]], {'fields': ['state']})
check("Frontdesk module is installed", mod and mod[0]['state'] == 'installed')

# ============================================================
# 2. Stations exist
# ============================================================
print("\n=== 2. Stations ===")
stations = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.frontdesk', 'search_read', [[]], 
    {'fields': ['name', 'host_selection', 'authenticate_guest', 'theme', 'self_check_in', 
                'drink_offer', 'kiosk_url', 'drink_ids', 'responsible_ids', 'host_ids',
                'ask_email', 'ask_phone', 'ask_company', 'notify_email', 'notify_sms', 'notify_discuss']})
check("At least 2 stations exist", len(stations) >= 2)

# Find Main Lobby
lobby = [s for s in stations if 'Main Lobby' in s['name']]
check("Main Lobby station exists", len(lobby) == 1)
if lobby:
    l = lobby[0]
    check("Main Lobby - theme is light", l['theme'] == 'light')
    check("Main Lobby - host selection enabled", l['host_selection'] == True)
    check("Main Lobby - authenticate guest enabled", l['authenticate_guest'] == True)
    check("Main Lobby - email is required", l['ask_email'] == 'required')
    check("Main Lobby - phone is optional", l['ask_phone'] == 'optional')
    check("Main Lobby - organization is required", l['ask_company'] == 'required')
    check("Main Lobby - offer drinks enabled", l['drink_offer'] == True)
    check("Main Lobby - self check-in disabled", l['self_check_in'] == False)
    check("Main Lobby - notify by email enabled", l['notify_email'] == True)
    check("Main Lobby - notify by discuss enabled", l['notify_discuss'] == True)
    check("Main Lobby - has kiosk URL", bool(l['kiosk_url']))
    check("Main Lobby - has hosts assigned", len(l['host_ids']) >= 1)
    check("Main Lobby - Rohan Raj is responsible", uid in l['responsible_ids'])

# Find Conference Room Entrance
conf = [s for s in stations if 'Conference' in s['name']]
check("Conference Room Entrance station exists", len(conf) == 1)
if conf:
    c = conf[0]
    check("Conference - theme is dark", c['theme'] == 'dark')
    check("Conference - host selection enabled", c['host_selection'] == True)
    check("Conference - self check-in enabled", c['self_check_in'] == True)
    check("Conference - offer drinks enabled", c['drink_offer'] == True)
    check("Conference - notify by discuss enabled", c['notify_discuss'] == True)
    check("Conference - has kiosk URL", bool(c['kiosk_url']))

# ============================================================
# 3. Drinks
# ============================================================
print("\n=== 3. Drinks ===")
drinks = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.drink', 'search_read', [[]], 
    {'fields': ['name', 'sequence', 'notify_user_ids']})
drink_names = [d['name'] for d in drinks]
check("At least 5 drinks exist", len(drinks) >= 5)
check("Water exists", 'Water' in drink_names)
check("Cola exists", 'Cola' in drink_names)
check("Coffee exists", 'Coffee' in drink_names)
check("Tea exists", 'Tea' in drink_names)
check("Fresh Juice exists", 'Fresh Juice' in drink_names)
for d in drinks:
    check(f"Drink '{d['name']}' has notify users", len(d['notify_user_ids']) >= 1)

# ============================================================
# 4. Planned Visitor
# ============================================================
print("\n=== 4. Planned Visitor ===")
visitors = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.visitor', 'search_read', 
    [[['name', '=', 'Meera Krishnan']]], 
    {'fields': ['name', 'company', 'email', 'phone', 'station_id', 'state', 'host_ids']})
check("Planned visitor Meera Krishnan exists", len(visitors) == 1)
if visitors:
    v = visitors[0]
    check("Visitor company is TechStar Solutions", v['company'] == 'TechStar Solutions')
    check("Visitor email is meera.k@techstar.com", v['email'] == 'meera.k@techstar.com')
    check("Visitor state is planned", v['state'] == 'planned')
    check("Visitor station is Main Lobby", 'Main Lobby' in str(v['station_id']))
    check("Visitor has host assigned", len(v['host_ids']) >= 1)

# ============================================================
# 5. Employees exist (for hosts)
# ============================================================
print("\n=== 5. Employees (Hosts) ===")
emps = models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'search_read', [[]], 
    {'fields': ['name', 'job_title']})
emp_names = [e['name'] for e in emps]
check("Amit Patel exists as employee", 'Amit Patel' in emp_names)
check("Ananya Reddy exists as employee", 'Ananya Reddy' in emp_names)
check("Neha Gupta exists as employee", 'Neha Gupta' in emp_names)

# ============================================================
# 6. Visitor state selections match blog
# ============================================================
print("\n=== 6. Visitor State Selections ===")
vfields = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.visitor', 'fields_get', [['state']], {'attributes': ['selection']})
state_vals = [s[0] for s in vfields['state']['selection']]
check("Planned state exists", 'planned' in state_vals)
check("Checked-In state exists", 'checked_in' in state_vals)
check("Checked-Out state exists", 'checked_out' in state_vals)
check("Cancelled state exists", 'canceled' in state_vals)

# ============================================================
# 7. Theme selections match blog
# ============================================================
print("\n=== 7. Theme Selections ===")
tfields = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.frontdesk', 'fields_get', [['theme']], {'attributes': ['selection']})
theme_vals = [t[0] for t in tfields['theme']['selection']]
check("Light theme exists", 'light' in theme_vals)
check("Dark theme exists", 'dark' in theme_vals)

# ============================================================
# 8. Authentication field selections
# ============================================================
print("\n=== 8. Authentication Selections ===")
afields = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.frontdesk', 'fields_get', 
    [['ask_email', 'ask_phone', 'ask_company']], {'attributes': ['selection']})
for fname in ['ask_email', 'ask_phone', 'ask_company']:
    vals = [s[0] for s in afields[fname]['selection']]
    check(f"{fname} has 'required' option", 'required' in vals)
    check(f"{fname} has 'optional' option", 'optional' in vals)

# ============================================================
# Summary
# ============================================================
print(f"\n{'=' * 60}")
print(f"VERIFICATION SUMMARY: {passed} passed, {failed} failed out of {passed + failed} checks")
print(f"{'=' * 60}")
if failed == 0:
    print("🎉 ALL CHECKS PASSED - Blog is verified correct!")
else:
    print(f"⚠️  {failed} check(s) need attention.")
