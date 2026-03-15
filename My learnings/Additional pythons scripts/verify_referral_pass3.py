"""
PASS 3: Get actual data from all referral models with correct field names.
"""
import xmlrpc.client

URL = 'https://demo-tech.odoo.com'
DB = 'demo-tech'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)
print(f"Authenticated as UID={uid}\n")

# ============================================================
print("=" * 70)
print("1. ONBOARDING SLIDES (correct fields: text, sequence, company_id)")
print("=" * 70)
onboarding = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.onboarding', 'search_read',
    [[]], {'fields': ['text', 'sequence', 'company_id'], 'order': 'sequence'})
print(f"  Total slides: {len(onboarding)}")
for idx, slide in enumerate(onboarding):
    print(f"  Slide {idx+1} (seq={slide['sequence']}): {slide['text'][:120] if slide['text'] else '(empty)'}...")
    print(f"     Company: {slide.get('company_id', 'All')}")

# ============================================================
print("\n" + "=" * 70)
print("2. LEVELS (correct fields: name, points)")
print("=" * 70)
levels = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.level', 'search_read',
    [[]], {'fields': ['name', 'points'], 'order': 'points'})
print(f"  Total levels: {len(levels)}")
for lv in levels:
    print(f"  Level '{lv['name']}': {lv['points']} points required")

# ============================================================
print("\n" + "=" * 70)
print("3. REWARDS (all data)")
print("=" * 70)
rewards = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.reward', 'search_read',
    [[]], {'fields': ['name', 'cost', 'company_id', 'gift_manager_id', 'description', 'awarded_employees']})
print(f"  Total rewards: {len(rewards)}")
for rw in rewards:
    print(f"  Reward '{rw['name']}': Cost={rw['cost']} pts, "
          f"Gift Responsible={rw.get('gift_manager_id', 'N/A')}, "
          f"Company={rw.get('company_id', 'N/A')}, "
          f"Awarded={rw.get('awarded_employees', 0)}")

# ============================================================
print("\n" + "=" * 70)
print("4. ALERTS (all data)")
print("=" * 70)
alerts = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.alert', 'search_read',
    [[]], {'fields': ['name', 'date_from', 'date_to', 'company_id', 'onclick', 'url']})
print(f"  Total alerts: {len(alerts)}")
for al in alerts:
    print(f"  Alert: '{al['name']}', From={al['date_from']}, To={al['date_to']}, "
          f"OnClick={al['onclick']}, URL={al.get('url', 'N/A')}")

# ============================================================
print("\n" + "=" * 70)
print("5. FRIENDS (all data)")
print("=" * 70)
friends = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.friend', 'search_read',
    [[]], {'fields': ['name', 'position']})
print(f"  Total friends: {len(friends)}")
for fr in friends:
    print(f"  Friend '{fr['name']}': Position={fr['position']}")

# ============================================================
print("\n" + "=" * 70)
print("6. REFERRAL POINTS ENTRIES")
print("=" * 70)
points = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.points', 'search_read',
    [[]], {'fields': ['applicant_id', 'applicant_name', 'stage_id', 'points', 'ref_user_id', 'sequence_stage']})
print(f"  Total point entries: {len(points)}")
for pt in points:
    print(f"  Applicant: {pt.get('applicant_name', pt.get('applicant_id'))}, "
          f"Stage: {pt.get('stage_id')}, Points: {pt['points']}, "
          f"User: {pt.get('ref_user_id')}, SeqStage: {pt.get('sequence_stage')}")

# ============================================================
print("\n" + "=" * 70)
print("7. APPLICANTS WITH REFERRAL DATA (correct field: ref_user_id)")
print("=" * 70)
# All active applicants
applicants = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
    [[]], {'fields': ['partner_name', 'stage_id', 'job_id', 'ref_user_id', 
                       'referral_state', 'source_id', 'medium_id', 'priority']})
print(f"  Active applicants: {len(applicants)}")
for app in applicants:
    ref = app.get('ref_user_id', False)
    print(f"  '{app['partner_name']}': Stage={app.get('stage_id')}, "
          f"Job={app.get('job_id')}, RefBy={ref}, "
          f"RefState={app.get('referral_state')}, "
          f"Source={app.get('source_id')}, Medium={app.get('medium_id')}, "
          f"Priority={app.get('priority')}")

# Archived applicants
archived = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
    [[['active', '=', False]]], 
    {'fields': ['partner_name', 'stage_id', 'job_id', 'ref_user_id', 'referral_state']})
print(f"\n  Archived applicants: {len(archived)}")
for app in archived:
    ref = app.get('ref_user_id', False)
    print(f"  '{app['partner_name']}': Stage={app.get('stage_id')}, RefBy={ref}")

# ============================================================
print("\n" + "=" * 70)
print("8. RECRUITMENT STAGES — DETAILED POINTS")
print("=" * 70)
stages = models.execute_kw(DB, uid, PASSWORD, 'hr.recruitment.stage', 'search_read',
    [[]], {'order': 'sequence', 'fields': ['name', 'sequence', 'points']})
total_pts = 0
for s in stages:
    pts = s.get('points', 0)
    total_pts += pts
    print(f"  Stage '{s['name']}' (seq {s['sequence']}): {pts} points")
print(f"  TOTAL points if hired: {total_pts}")

# ============================================================
print("\n" + "=" * 70)
print("9. CURRENT USER DETAILS")
print("=" * 70)
user = models.execute_kw(DB, uid, PASSWORD, 'res.users', 'read', [uid],
    {'fields': ['name', 'login', 'company_id']})
if user:
    print(f"  Name: {user[0]['name']}")
    print(f"  Login: {user[0]['login']}")
    print(f"  Company: {user[0]['company_id']}")

print("\n" + "=" * 70)
print("VERIFICATION PASS 3 COMPLETE")
print("=" * 70)
