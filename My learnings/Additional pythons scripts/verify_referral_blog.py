"""
COMPREHENSIVE VERIFICATION: Cross-check every claim in the Referral App blog
against the demo-tech Odoo 19 database.

Database: https://demo-tech.odoo.com
"""
import xmlrpc.client
import json

URL = 'https://demo-tech.odoo.com'
DB = 'demo-tech'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

print("Connecting to Odoo database...")
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

if not uid:
    print("AUTHENTICATION FAILED! Check credentials.")
    exit(1)

print(f"Authenticated as UID={uid}\n")

passed = 0
failed = 0
findings = []

def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {label}")
    else:
        failed += 1
        print(f"  [FAIL] {label} — {detail}")
        findings.append(f"FAIL: {label} — {detail}")

def info(label, value):
    print(f"  [INFO] {label}: {value}")
    findings.append(f"INFO: {label}: {value}")

# ============================================================
print("=" * 70)
print("SECTION 1: MODULE INSTALLATION")
print("=" * 70)

# Check if Referrals module is installed
referral_mods = ['hr_referral', 'hr_recruitment', 'hr_employee', 'website', 'website_hr_recruitment']
installed = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', 'in', referral_mods]]],
    {'fields': ['name', 'state', 'shortdesc']})

for mod in installed:
    check(f"Module '{mod['name']}' ({mod['shortdesc']}) state",
          mod['state'] == 'installed', f"state={mod['state']}")

mod_names = [m['name'] for m in installed if m['state'] == 'installed']
check("hr_referral (Referrals) is installed", 'hr_referral' in mod_names,
      f"Installed: {mod_names}")
check("hr_recruitment (Recruitment) is installed", 'hr_recruitment' in mod_names)
check("website is installed", 'website' in mod_names)

# Also check related modules
extra_mods = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', 'like', 'referral'], ['state', '=', 'installed']]],
    {'fields': ['name', 'shortdesc']})
for m in extra_mods:
    info(f"Referral-related module installed", f"{m['name']} — {m['shortdesc']}")

# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: REFERRAL ONBOARDING SLIDES")
print("=" * 70)

try:
    onboarding = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.onboarding', 'search_read',
        [[]], {'fields': ['name', 'text', 'sequence', 'company_id'], 'order': 'sequence'})
    check("Onboarding slides exist", len(onboarding) > 0, f"Found {len(onboarding)}")
    check("4 onboarding slides", len(onboarding) == 4, f"Found {len(onboarding)}")
    for idx, slide in enumerate(onboarding):
        info(f"Slide {idx+1} text", slide.get('text', '(empty)')[:100])
        info(f"Slide {idx+1} sequence", slide.get('sequence'))
except Exception as e:
    info("Onboarding model access", f"Error: {e}")

# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: REFERRAL LEVELS")
print("=" * 70)

try:
    levels = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.level', 'search_read',
        [[]], {'fields': ['name', 'points', 'sequence'], 'order': 'sequence'})
    check("Referral levels exist", len(levels) > 0, f"Found {len(levels)}")
    info("Number of levels", len(levels))
    for lv in levels:
        info(f"Level '{lv['name']}'", f"Points required: {lv.get('points', 'N/A')}")
except Exception as e:
    info("Levels model access", f"Error: {e}")

# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: REFERRAL FRIENDS (AVATARS)")
print("=" * 70)

try:
    friends = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.friend', 'search_read',
        [[]], {'fields': ['name', 'position'], 'order': 'id'})
    check("Friend avatars exist", len(friends) > 0, f"Found {len(friends)}")
    info("Number of friend avatars", len(friends))
    for fr in friends:
        info(f"Friend '{fr['name']}'", f"Position: {fr.get('position', 'N/A')}")
except Exception as e:
    info("Friends model access", f"Error: {e}")

# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: REFERRAL REWARDS")
print("=" * 70)

try:
    rewards = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.reward', 'search_read',
        [[]], {'fields': ['name', 'cost', 'company_id', 'gift_manager_id', 'description'],
               'order': 'cost'})
    check("Rewards exist", len(rewards) > 0, f"Found {len(rewards)}")
    info("Number of rewards", len(rewards))
    for rw in rewards:
        info(f"Reward '{rw['name']}'", 
             f"Cost: {rw.get('cost', 'N/A')} pts, "
             f"Gift Responsible: {rw.get('gift_manager_id', 'N/A')}, "
             f"Company: {rw.get('company_id', 'N/A')}")
except Exception as e:
    info("Rewards model access", f"Error: {e}")

# ============================================================
print("\n" + "=" * 70)
print("SECTION 6: REFERRAL ALERTS")
print("=" * 70)

try:
    alerts = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.alert', 'search_read',
        [[]], {'fields': ['name', 'date_from', 'date_to', 'company_id', 'onclick', 'url'],
               'order': 'date_from'})
    info("Number of alerts", len(alerts))
    for al in alerts:
        info(f"Alert", f"Text: {al.get('name', '(empty)')[:80]}, "
             f"From: {al.get('date_from')}, To: {al.get('date_to')}, "
             f"OnClick: {al.get('onclick')}")
except Exception as e:
    info("Alerts model access", f"Error: {e}")

# ============================================================
print("\n" + "=" * 70)
print("SECTION 7: RECRUITMENT STAGES & REFERRAL POINTS")
print("=" * 70)

stages = models.execute_kw(DB, uid, PASSWORD, 'hr.recruitment.stage', 'search_read',
    [[]], {'order': 'sequence', 'fields': ['name', 'sequence', 'fold', 'hired_stage', 
                                            'template_id', 'points']})
info("Number of recruitment stages", len(stages))
for s in stages:
    info(f"Stage '{s['name']}'",
         f"Seq: {s.get('sequence')}, Fold: {s.get('fold')}, "
         f"Hired: {s.get('hired_stage')}, Points: {s.get('points', 'N/A')}, "
         f"Email Template: {s.get('template_id', 'None')}")

# Check blog's point claims
# Blog says: Initial Qualification=1, First Interview=20, Second Interview=9, 
#            Contract Proposal=5, Contract Signed=50
expected_points = {
    'New': 0,
    'Qualification': 1,
    'First Interview': 20,
    'Second Interview': 9,
    'Contract Proposal': 5,
    'Contract Signed': 50,
}
for s in stages:
    if s['name'] in expected_points:
        pts = s.get('points', 0)
        exp = expected_points[s['name']]
        check(f"Stage '{s['name']}' has {exp} referral points",
              pts == exp, f"Got {pts}")

# ============================================================
print("\n" + "=" * 70)
print("SECTION 8: PUBLISHED JOB POSITIONS")
print("=" * 70)

jobs = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'search_read',
    [[]], {'fields': ['name', 'department_id', 'no_of_recruitment', 'is_published',
                      'website_url', 'application_count', 'no_of_hired_employee',
                      'user_id', 'expected_employees']})
info("Total job positions", len(jobs))
for j in jobs:
    info(f"Job '{j['name']}'",
         f"Dept: {j.get('department_id', 'N/A')}, "
         f"Published: {j.get('is_published')}, "
         f"Target: {j.get('no_of_recruitment')}, "
         f"Apps: {j.get('application_count')}, "
         f"Hired: {j.get('no_of_hired_employee')}")

published_jobs = [j for j in jobs if j.get('is_published')]
info("Published job positions", len(published_jobs))
for pj in published_jobs:
    info(f"  Published: '{pj['name']}'", f"URL: {pj.get('website_url', 'N/A')}")

# ============================================================
print("\n" + "=" * 70)
print("SECTION 9: REFERRAL RECORDS")
print("=" * 70)

try:
    # Check hr.referral.points model for actual referral tracking
    ref_points = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.points', 'search_read',
        [[]], {'fields': ['applicant_id', 'stage_id', 'points', 'ref_user_id'],
               'order': 'id'})
    info("Referral point entries", len(ref_points))
    for rp in ref_points:
        info(f"  Referral point entry",
             f"Applicant: {rp.get('applicant_id')}, "
             f"Stage: {rp.get('stage_id')}, "
             f"Points: {rp.get('points')}, "
             f"User: {rp.get('ref_user_id')}")
except Exception as e:
    info("Referral points model", f"Error: {e}")

# Check applicants that have referral info
try:
    applicants = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
        [[]], {'fields': ['partner_name', 'stage_id', 'job_id', 'ref_user_ids',
                          'source_id', 'medium_id', 'priority', 'active'],
               'order': 'id'})
    info("Total applicants (active)", len(applicants))
    referred_apps = [a for a in applicants if a.get('ref_user_ids')]
    info("Referred applicants", len(referred_apps))
    for ra in referred_apps:
        info(f"  Referred: '{ra['partner_name']}'",
             f"Job: {ra.get('job_id')}, Stage: {ra.get('stage_id')}, "
             f"Medium: {ra.get('medium_id')}, Source: {ra.get('source_id')}")
except Exception as e:
    info("Applicant referral data", f"Error: {e}")

# Also check archived applicants
try:
    archived_apps = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
        [[['active', '=', False]]], 
        {'fields': ['partner_name', 'stage_id', 'job_id', 'ref_user_ids', 'active'],
         'order': 'id'})
    info("Archived applicants", len(archived_apps))
    for aa in archived_apps:
        if aa.get('ref_user_ids'):
            info(f"  Archived referred: '{aa['partner_name']}'",
                 f"Job: {aa.get('job_id')}")
except Exception as e:
    info("Archived applicant data", f"Error: {e}")

# ============================================================
print("\n" + "=" * 70)
print("SECTION 10: COMPANY INFORMATION")
print("=" * 70)

companies = models.execute_kw(DB, uid, PASSWORD, 'res.company', 'search_read',
    [[]], {'fields': ['name']})
for c in companies:
    info("Company", c['name'])

# ============================================================
print("\n" + "=" * 70)
print("SECTION 11: DEPARTMENTS")
print("=" * 70)

depts = models.execute_kw(DB, uid, PASSWORD, 'hr.department', 'search_read',
    [[]], {'fields': ['name', 'company_id', 'parent_id', 'manager_id']})
info("Total departments", len(depts))
for d in depts:
    info(f"Department '{d['name']}'",
         f"Company: {d.get('company_id', 'N/A')}, "
         f"Parent: {d.get('parent_id', 'None')}, "
         f"Manager: {d.get('manager_id', 'None')}")

# ============================================================
print("\n" + "=" * 70)
print("SECTION 12: EMPLOYEES")
print("=" * 70)

employees = models.execute_kw(DB, uid, PASSWORD, 'hr.employee', 'search_read',
    [[]], {'fields': ['name', 'department_id', 'job_id', 'job_title', 'company_id'],
           'order': 'name'})
info("Total employees", len(employees))
for emp in employees:
    info(f"Employee '{emp['name']}'",
         f"Dept: {emp.get('department_id', 'N/A')}, "
         f"Job: {emp.get('job_id', 'N/A')}, "
         f"Title: {emp.get('job_title', 'N/A')}")

# ============================================================
print("\n" + "=" * 70)
print("SECTION 13: USER WHO LOGGED IN (CURRENT USER)")
print("=" * 70)

current_user = models.execute_kw(DB, uid, PASSWORD, 'res.users', 'read', [uid],
    {'fields': ['name', 'login', 'company_id', 'groups_id']})
if current_user:
    cu = current_user[0]
    info("Current user", f"{cu['name']} ({cu['login']})")
    info("Current user company", cu.get('company_id'))

# ============================================================
print("\n" + "=" * 70)
print("SECTION 14: SETTINGS CHECK — REFERRAL/RECRUITMENT FEATURES")
print("=" * 70)

# Check if survey module installed (for interview survey feature)
survey_mod = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', '=', 'hr_recruitment_survey']]],
    {'fields': ['name', 'state']})
if survey_mod:
    info("HR Recruitment Survey module", survey_mod[0]['state'])

# Check website_hr_recruitment for online posting
web_recruit = models.execute_kw(DB, uid, PASSWORD, 'ir.module.module', 'search_read',
    [[['name', '=', 'website_hr_recruitment']]],
    {'fields': ['name', 'state']})
if web_recruit:
    info("Website HR Recruitment module", web_recruit[0]['state'])

# ============================================================
print("\n" + "=" * 70)
print("SECTION 15: REFERRAL-SPECIFIC FIELDS ON MODELS")
print("=" * 70)

# Check what referral-related fields exist on hr.applicant
try:
    app_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'fields_get',
        [], {'attributes': ['string', 'type']})
    ref_fields = {k: v for k, v in app_fields.items() if 'refer' in k.lower() or 'ref_' in k.lower()}
    info("Referral-related fields on hr.applicant", len(ref_fields))
    for fname, fdata in ref_fields.items():
        info(f"  Field '{fname}'", f"{fdata.get('string')} ({fdata.get('type')})")
except Exception as e:
    info("Applicant referral fields", f"Error: {e}")

# Check what models exist related to referral
try:
    ref_models = models.execute_kw(DB, uid, PASSWORD, 'ir.model', 'search_read',
        [[['model', 'like', 'hr.referral']]],
        {'fields': ['model', 'name']})
    info("Referral-related models", len(ref_models))
    for rm in ref_models:
        info(f"  Model", f"{rm['model']} — {rm['name']}")
except Exception as e:
    info("Referral models", f"Error: {e}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print(f"VERIFICATION COMPLETE: {passed} PASSED, {failed} FAILED out of {passed + failed} checks")
print("=" * 70)

if findings:
    print(f"\nTotal findings logged: {len(findings)}")
    # Save findings to a file for easy review
    with open(r"c:\Odoo Study\referral_blog_verification_results.txt", 'w', encoding='utf-8') as f:
        f.write("REFERRAL APP BLOG VERIFICATION RESULTS\n")
        f.write(f"Database: {URL}\n")
        f.write(f"Date: March 1, 2026\n")
        f.write("=" * 70 + "\n\n")
        for finding in findings:
            f.write(finding + "\n")
        f.write(f"\n{'=' * 70}\n")
        f.write(f"SUMMARY: {passed} PASSED, {failed} FAILED out of {passed + failed} checks\n")
    print("Results saved to: c:\\Odoo Study\\referral_blog_verification_results.txt")
