#!/usr/bin/env python3
"""
Pass 2: Fix job positions query and get additional details from client-cient.odoo.com.
"""

import xmlrpc.client
import json

URL = "https://client-cient.odoo.com"
DB = "client-cient"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

def main():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)

    def search_read(model, domain=[], fields=[], limit=0):
        kw = {'fields': fields}
        if limit:
            kw['limit'] = limit
        return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], kw)

    def fields_get(model, attrs=['string','type']):
        return models.execute_kw(DB, uid, PASSWORD, model, 'fields_get', [], {'attributes': attrs})

    # ── 1. hr.job fields ──
    print("=" * 70)
    print("JOB POSITION FIELDS")
    print("=" * 70)
    jf = fields_get('hr.job')
    relevant = ['name','department_id','company_id','website_published','no_of_recruitment',
                'no_of_hired_employee','application_count','is_published','state',
                'expected_employees','no_of_employee']
    for f in relevant:
        if f in jf:
            print(f"  {f:30s} | {jf[f]['string']:30s} | {jf[f]['type']}")
        else:
            print(f"  {f:30s} | NOT FOUND")

    # ── 2. Job positions (without state) ──
    print("\n" + "=" * 70)
    print("JOB POSITIONS (corrected query)")
    print("=" * 70)
    jobs = search_read('hr.job', [], ['name','department_id','company_id','website_published',
                                       'no_of_recruitment','no_of_hired_employee',
                                       'application_count','is_published'])
    print(f"Total job positions: {len(jobs)}")
    for j in jobs:
        pub = j.get('website_published') or j.get('is_published', False)
        print(f"  {j['name']:40s}")
        print(f"    Dept: {j.get('department_id', 'N/A')}")
        print(f"    Company: {j.get('company_id', 'N/A')}")
        print(f"    Published: {pub}")
        print(f"    Target: {j.get('no_of_recruitment', 0)}")
        print(f"    Applications: {j.get('application_count', 0)}")
        print(f"    Hired: {j.get('no_of_hired_employee', 0)}")
        print()

    # ── 3. Recruitment stages with sequence details ──
    print("=" * 70)
    print("RECRUITMENT STAGES (detailed)")
    print("=" * 70)
    stages = search_read('hr.recruitment.stage', [], ['name','sequence','points','fold',
                                                        'hired_stage','template_id'])
    stages.sort(key=lambda x: x.get('sequence', 0))
    for st in stages:
        print(f"  ID={st['id']} | Seq={st.get('sequence',0)} | {st['name']:25s} | Points={st.get('points',0)} | Fold={st.get('fold',False)} | Hired={st.get('hired_stage',False)}")

    # ── 4. Applicant details with more fields ──
    print("\n" + "=" * 70)
    print("APPLICANT DETAILS (extended)")
    print("=" * 70)
    # Check what fields exist
    af = fields_get('hr.applicant')
    check_fields = ['partner_name','stage_id','job_id','priority','ref_user_id',
                     'user_id','department_id','kanban_state','emp_id','date_closed',
                     'create_date','active','refuse_reason_id','applicant_properties']
    for f in check_fields:
        if f in af:
            print(f"  Field: {f:30s} | {af[f]['string']:25s} | {af[f]['type']}")

    # All applicants with extended data
    print("\n  --- Active Applicants ---")
    applicants = search_read('hr.applicant', [('active','=',True)],
                              ['partner_name','stage_id','job_id','priority',
                               'ref_user_id','user_id','department_id','kanban_state',
                               'emp_id','date_closed','create_date'])
    for a in applicants:
        print(f"\n  Name: {a.get('partner_name','N/A')}")
        print(f"    Stage: {a.get('stage_id', 'N/A')}")
        print(f"    Job: {a.get('job_id', 'N/A')}")
        print(f"    Priority: {a.get('priority', 'N/A')}")
        print(f"    Referred By: {a.get('ref_user_id', 'None')}")
        print(f"    Recruiter: {a.get('user_id', 'N/A')}")
        print(f"    Department: {a.get('department_id', 'N/A')}")
        print(f"    Employee Created: {a.get('emp_id', 'None')}")
        print(f"    Created: {a.get('create_date', 'N/A')}")

    print("\n  --- Archived Applicants ---")
    archived = search_read('hr.applicant', [('active','=',False)],
                            ['partner_name','stage_id','job_id','priority',
                             'ref_user_id','create_date'])
    for a in archived:
        print(f"\n  Name: {a.get('partner_name','N/A')}")
        print(f"    Stage: {a.get('stage_id', 'N/A')}")
        print(f"    Job: {a.get('job_id', 'N/A')}")
        print(f"    Priority: {a.get('priority', 'N/A')}")

    # ── 5. All companies with details ──
    print("\n" + "=" * 70)
    print("COMPANIES (detailed)")
    print("=" * 70)
    companies = search_read('res.company', [], ['name','parent_id','street','city','country_id'])
    for c in companies:
        print(f"  ID={c['id']} | {c['name']}")
        print(f"    Parent: {c.get('parent_id', 'None')}")
        print(f"    Location: {c.get('street', '')}, {c.get('city', '')}, {c.get('country_id', '')}")

    print("\n" + "=" * 70)
    print("PASS 2 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
