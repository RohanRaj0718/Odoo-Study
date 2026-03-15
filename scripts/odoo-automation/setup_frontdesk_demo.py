import xmlrpc.client

URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
print(f"Authenticated: uid={uid}")

models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

# ============================================================
# 1. Check existing stations
# ============================================================
print("\n=== Existing Stations ===")
stations = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.frontdesk', 'search_read', [[]], 
    {'fields': ['name', 'host_selection', 'authenticate_guest', 'theme', 'self_check_in', 
                'drink_offer', 'kiosk_url', 'drink_ids', 'responsible_ids', 'host_ids',
                'ask_email', 'ask_phone', 'ask_company', 'notify_email', 'notify_sms', 'notify_discuss']})
for s in stations:
    print(f"  Station: {s}")
if not stations:
    print("  No stations found.")

# ============================================================
# 2. Check existing drinks
# ============================================================
print("\n=== Existing Drinks ===")
drinks = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.drink', 'search_read', [[]], 
    {'fields': ['name', 'sequence', 'notify_user_ids']})
for d in drinks:
    print(f"  Drink: {d}")

# ============================================================
# 3. Check existing visitors
# ============================================================
print("\n=== Existing Visitors ===")
visitors = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.visitor', 'search_read', [[]], 
    {'fields': ['name', 'company', 'email', 'phone', 'host_ids', 'station_id', 'state', 'check_in', 'check_out', 'drink_ids']})
for v in visitors:
    print(f"  Visitor: {v}")
if not visitors:
    print("  No visitors found.")

# ============================================================
# 4. Create Station: Main Lobby
# ============================================================
print("\n=== Creating Station: Main Lobby ===")
try:
    # Get employee IDs for hosts
    emps = models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'search_read', [[]], {'fields': ['name']})
    emp_ids = [e['id'] for e in emps]
    # Use first 3 employees as hosts
    host_ids = emp_ids[:3] if len(emp_ids) >= 3 else emp_ids
    
    # Get drink IDs
    drink_ids_list = [d['id'] for d in drinks]
    
    station1_id = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.frontdesk', 'create', [{
        'name': 'Main Lobby',
        'responsible_ids': [(6, 0, [uid])],
        'host_selection': True,
        'host_ids': [(6, 0, host_ids)],
        'authenticate_guest': True,
        'ask_email': 'required',
        'ask_phone': 'optional',
        'ask_company': 'required',
        'theme': 'light',
        'self_check_in': False,
        'drink_offer': True,
        'drink_ids': [(6, 0, drink_ids_list)],
        'notify_email': True,
        'notify_discuss': True,
        'notify_sms': False,
    }])
    print(f"  Created Main Lobby station: id={station1_id}")
except Exception as e:
    print(f"  Error creating Main Lobby: {e}")

# ============================================================
# 5. Create Station: Conference Room Entrance
# ============================================================
print("\n=== Creating Station: Conference Room Entrance ===")
try:
    station2_id = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.frontdesk', 'create', [{
        'name': 'Conference Room Entrance',
        'responsible_ids': [(6, 0, [uid])],
        'host_selection': True,
        'host_ids': [(6, 0, host_ids[1:3] if len(host_ids) >= 3 else host_ids)],
        'authenticate_guest': True,
        'ask_email': 'optional',
        'ask_phone': 'optional',
        'ask_company': 'optional',
        'theme': 'dark',
        'self_check_in': True,
        'drink_offer': True,
        'drink_ids': [(6, 0, drink_ids_list)],
        'notify_email': False,
        'notify_discuss': True,
        'notify_sms': False,
    }])
    print(f"  Created Conference Room Entrance station: id={station2_id}")
except Exception as e:
    print(f"  Error creating Conference Room Entrance: {e}")

# ============================================================
# 6. Create additional drinks: Coffee, Tea, Juice
# ============================================================
print("\n=== Creating additional drinks ===")
new_drinks = [
    {'name': 'Coffee', 'notify_user_ids': [(6, 0, [uid])], 'sequence': 3},
    {'name': 'Tea', 'notify_user_ids': [(6, 0, [uid])], 'sequence': 4},
    {'name': 'Fresh Juice', 'notify_user_ids': [(6, 0, [uid])], 'sequence': 5},
]
for drink in new_drinks:
    try:
        drink_id = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.drink', 'create', [drink])
        print(f"  Created drink '{drink['name']}': id={drink_id}")
    except Exception as e:
        print(f"  Error creating drink '{drink['name']}': {e}")

# ============================================================
# 7. Create Planned Visitor
# ============================================================
print("\n=== Creating Planned Visitor ===")
try:
    # Use station1_id if it was created
    planned_visitor_id = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.visitor', 'create', [{
        'name': 'Meera Krishnan',
        'company': 'TechStar Solutions',
        'email': 'meera.k@techstar.com',
        'phone': '+91 9876543210',
        'station_id': station1_id,
        'host_ids': [(6, 0, [host_ids[0]])],
    }])
    print(f"  Created planned visitor: id={planned_visitor_id}")
except Exception as e:
    print(f"  Error creating planned visitor: {e}")

# ============================================================
# 8. Verify all data
# ============================================================
print("\n=== Final Verification ===")
print("\nStations:")
stations = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.frontdesk', 'search_read', [[]], 
    {'fields': ['name', 'host_selection', 'theme', 'drink_offer', 'self_check_in', 'authenticate_guest', 'kiosk_url']})
for s in stations:
    print(f"  {s['name']} (id={s['id']}): theme={s['theme']}, host_sel={s['host_selection']}, drinks={s['drink_offer']}, qr={s['self_check_in']}, auth={s['authenticate_guest']}")
    print(f"    Kiosk URL: {s.get('kiosk_url', 'N/A')}")

print("\nDrinks:")
drinks = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.drink', 'search_read', [[]], 
    {'fields': ['name', 'sequence']})
for d in drinks:
    print(f"  {d['name']} (seq={d['sequence']})")

print("\nVisitors:")
visitors = models.execute_kw(DB, uid, PASSWORD, 'frontdesk.visitor', 'search_read', [[]], 
    {'fields': ['name', 'company', 'station_id', 'state', 'host_ids']})
for v in visitors:
    print(f"  {v['name']} - {v['company']} @ {v['station_id']} - state={v['state']}")

print("\n✅ Demo data setup complete!")
