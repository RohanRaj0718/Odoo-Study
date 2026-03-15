#!/usr/bin/env python3
"""
Comprehensive verification of Referral App blog claims against
the client-cient.odoo.com database.
"""

import xmlrpc.client
import json
import sys

URL = "https://client-cient.odoo.com"
# Try same credentials first
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

def pretty(obj):
    return json.dumps(obj, indent=2, default=str)

def main():
    # ── 1. Authenticate & discover DB ──
    print("=" * 70)
    print("STEP 1: Authentication")
    print("=" * 70)

    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
    ver = common.version()
    print(f"Server version: {ver.get('server_version', 'unknown')}")

    # Try to list databases
    db_proxy = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/db", allow_none=True)
    try:
        dbs = db_proxy.list()
        print(f"Available databases: {dbs}")
    except Exception as e:
        print(f"Cannot list databases (access denied): {e}")
        # Guess DB name from URL
        dbs = ["client-cient"]
        print(f"Guessing DB name: {dbs}")

    # Try each DB
    uid = None
    db_name = None
    for db in dbs:
        try:
            uid = common.authenticate(db, USERNAME, PASSWORD, {})
            if uid:
                db_name = db
                print(f"Authenticated! DB={db_name}, UID={uid}")
                break
        except Exception as e:
            print(f"  DB '{db}' auth failed: {e}")

    if not uid:
        print("FATAL: Could not authenticate with any database.")
        sys.exit(1)

    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)

    def search_read(model, domain=[], fields=[], limit=0):
        kw = {'fields': fields}
        if limit:
            kw['limit'] = limit
        return models.execute_kw(db_name, uid, PASSWORD, model, 'search_read', [domain], kw)

    def search_count(model, domain=[]):
        return models.execute_kw(db_name, uid, PASSWORD, model, 'search_count', [domain])

    def fields_get(model, attrs=['string','type','required']):
        return models.execute_kw(db_name, uid, PASSWORD, model, 'fields_get', [], {'attributes': attrs})

    # ── 2. Current user & company ──
    print("\n" + "=" * 70)
    print("STEP 2: Current User & Company")
    print("=" * 70)
    user = search_read('res.users', [('id','=',uid)], ['name','login','company_id','company_ids'])
    if user:
        u = user[0]
        print(f"User: {u['name']} ({u['login']})")
        print(f"Current Company: {u['company_id']}")
        print(f"Allowed Companies: {u['company_ids']}")

    # ── 3. Installed modules ──
    print("\n" + "=" * 70)
    print("STEP 3: Installed Modules (Referral-related)")
    print("=" * 70)
    modules_to_check = ['hr_referral', 'hr_recruitment', 'website', 'website_hr_recruitment', 'hr']
    for mod in modules_to_check:
        recs = search_read('ir.module.module', [('name','=',mod)], ['name','shortdesc','state'])
        if recs:
            r = recs[0]
            print(f"  {r['name']:30s} | {r['shortdesc']:40s} | {r['state']}")
        else:
            print(f"  {mod:30s} | NOT FOUND")

    # ── 4. Onboarding slides ──
    print("\n" + "=" * 70)
    print("STEP 4: Onboarding Slides")
    print("=" * 70)
    try:
        slides = search_read('hr.referral.onboarding', [], ['text','sequence','company_id','image'])
        print(f"Total slides: {len(slides)}")
        for s in slides:
            print(f"  ID={s['id']} | Seq={s.get('sequence','N/A')} | Company={s.get('company_id', 'None')}")
            print(f"    Text: {s.get('text','(no text)')[:120]}")
    except Exception as e:
        print(f"Error reading onboarding: {e}")

    # ── 5. Levels ──
    print("\n" + "=" * 70)
    print("STEP 5: Referral Levels")
    print("=" * 70)
    try:
        levels = search_read('hr.referral.level', [], ['name','points','image'])
        levels.sort(key=lambda x: x.get('points', 0))
        print(f"Total levels: {len(levels)}")
        for lv in levels:
            print(f"  {lv['name']:20s} | Points: {lv['points']}")
    except Exception as e:
        print(f"Error reading levels: {e}")

    # ── 6. Rewards ──
    print("\n" + "=" * 70)
    print("STEP 6: Rewards")
    print("=" * 70)
    try:
        rewards = search_read('hr.referral.reward', [], ['name','cost','company_id','gift_manager_id','description'])
        print(f"Total rewards: {len(rewards)}")
        for rw in rewards:
            print(f"  Name: {rw['name']}")
            print(f"    Cost: {rw['cost']} pts")
            print(f"    Company: {rw.get('company_id', 'N/A')}")
            print(f"    Gift Responsible: {rw.get('gift_manager_id', 'N/A')}")
            print(f"    Description: {rw.get('description', 'N/A')}")
    except Exception as e:
        print(f"Error reading rewards: {e}")

    # ── 7. Alerts ──
    print("\n" + "=" * 70)
    print("STEP 7: Alerts")
    print("=" * 70)
    try:
        alerts = search_read('hr.referral.alert', [], ['name','date_from','date_to','company_id','onclick','url'])
        print(f"Total alerts: {len(alerts)}")
        for al in alerts:
            print(f"  Alert: {al.get('name','N/A')}")
            print(f"    Dates: {al.get('date_from')} to {al.get('date_to')}")
            print(f"    OnClick: {al.get('onclick','N/A')}")
    except Exception as e:
        print(f"Error reading alerts: {e}")

    # ── 8. Friend Avatars ──
    print("\n" + "=" * 70)
    print("STEP 8: Friend Avatars")
    print("=" * 70)
    try:
        friends = search_read('hr.referral.friend', [], ['name','position'])
        print(f"Total friends: {len(friends)}")
        for fr in friends:
            print(f"  {fr['name']:20s} | Position: {fr.get('position', 'N/A')}")
    except Exception as e:
        print(f"Error reading friends: {e}")

    # ── 9. Recruitment Stages & Points ──
    print("\n" + "=" * 70)
    print("STEP 9: Recruitment Stages & Referral Points")
    print("=" * 70)
    try:
        stages = search_read('hr.recruitment.stage', [], ['name','sequence','points'])
        stages.sort(key=lambda x: x.get('sequence', 0))
        total_pts = 0
        for st in stages:
            pts = st.get('points', 0)
            total_pts += pts
            print(f"  Seq={st.get('sequence',0):3d} | {st['name']:30s} | Points: {pts}")
        print(f"  {'':3s}   {'TOTAL':30s} | Points: {total_pts}")
    except Exception as e:
        print(f"Error reading stages: {e}")

    # ── 10. Departments ──
    print("\n" + "=" * 70)
    print("STEP 10: Departments")
    print("=" * 70)
    try:
        depts = search_read('hr.department', [], ['name','company_id','parent_id'])
        print(f"Total departments: {len(depts)}")
        for d in depts:
            print(f"  {d['name']:30s} | Company: {d.get('company_id', 'N/A')}")
    except Exception as e:
        print(f"Error reading departments: {e}")

    # ── 11. Job Positions ──
    print("\n" + "=" * 70)
    print("STEP 11: Job Positions")
    print("=" * 70)
    try:
        jobs = search_read('hr.job', [], ['name','department_id','company_id','website_published',
                                           'no_of_recruitment','no_of_hired_employee',
                                           'application_count','state'])
        print(f"Total job positions: {len(jobs)}")
        for j in jobs:
            pub = "YES" if j.get('website_published') else "NO"
            print(f"  {j['name']:40s} | Dept: {j.get('department_id', ['','N/A'])} | Published: {pub}")
            print(f"    Target: {j.get('no_of_recruitment', 0)} | Apps: {j.get('application_count', 0)} | Hired: {j.get('no_of_hired_employee', 0)}")
    except Exception as e:
        print(f"Error reading jobs: {e}")

    # ── 12. Applicants (active) ──
    print("\n" + "=" * 70)
    print("STEP 12: Applicants (Active)")
    print("=" * 70)
    try:
        applicants = search_read('hr.applicant', [('active','=',True)],
                                  ['partner_name','stage_id','job_id','priority',
                                   'ref_user_id','user_id','department_id','kanban_state'])
        print(f"Total active applicants: {len(applicants)}")
        for a in applicants:
            print(f"  {a.get('partner_name','N/A'):25s} | Stage: {a.get('stage_id', 'N/A')}")
            print(f"    Job: {a.get('job_id', 'N/A')} | Priority: {a.get('priority', 'N/A')}")
            print(f"    Referred By: {a.get('ref_user_id', 'None')} | Recruiter: {a.get('user_id', 'N/A')}")
    except Exception as e:
        print(f"Error reading active applicants: {e}")

    # ── 13. Applicants (archived) ──
    print("\n" + "=" * 70)
    print("STEP 13: Applicants (Archived)")
    print("=" * 70)
    try:
        archived = search_read('hr.applicant', [('active','=',False)],
                                ['partner_name','stage_id','job_id','priority','ref_user_id'])
        print(f"Total archived applicants: {len(archived)}")
        for a in archived:
            print(f"  {a.get('partner_name','N/A'):25s} | Stage: {a.get('stage_id', 'N/A')}")
            print(f"    Job: {a.get('job_id', 'N/A')} | Priority: {a.get('priority', 'N/A')}")
    except Exception as e:
        print(f"Error reading archived applicants: {e}")

    # ── 14. Referral Points entries ──
    print("\n" + "=" * 70)
    print("STEP 14: Referral Point Entries")
    print("=" * 70)
    try:
        pts = search_read('hr.referral.points', [], ['applicant_id','stage_id','points','ref_user_id'])
        print(f"Total point entries: {len(pts)}")
        for p in pts:
            print(f"  Applicant: {p.get('applicant_id','N/A')} | Stage: {p.get('stage_id','N/A')} | Points: {p.get('points',0)}")
    except Exception as e:
        print(f"Error reading points: {e}")

    # ── 15. Employees ──
    print("\n" + "=" * 70)
    print("STEP 15: Employees")
    print("=" * 70)
    try:
        emps = search_read('hr.employee', [], ['name','department_id','job_id','company_id'], limit=50)
        print(f"Total employees (up to 50): {len(emps)}")
        for e in emps:
            print(f"  {e['name']:30s} | Dept: {e.get('department_id','N/A')} | Job: {e.get('job_id','N/A')}")
    except Exception as e:
        print(f"Error reading employees: {e}")

    # ── 16. Companies ──
    print("\n" + "=" * 70)
    print("STEP 16: Companies")
    print("=" * 70)
    try:
        companies = search_read('res.company', [], ['name','parent_id'])
        print(f"Total companies: {len(companies)}")
        for c in companies:
            print(f"  ID={c['id']} | {c['name']} | Parent: {c.get('parent_id', 'None')}")
    except Exception as e:
        print(f"Error reading companies: {e}")

    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
