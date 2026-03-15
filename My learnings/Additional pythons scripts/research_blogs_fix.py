"""Quick fix - get remaining data"""
import xmlrpc.client

URL = 'https://demo-tech.odoo.com'
DB = 'demo-tech'
USERNAME = 'rohan.raj@infintor.com'
PASSWORD = 'Rohanraj@1'

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

# Active applicants
print("--- Active Applicants ---")
active = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'search_read',
    [[['active', '=', True]]],
    {'fields': ['partner_name', 'job_id', 'stage_id', 'priority',
                'salary_expected', 'salary_proposed',
                'application_status', 'date_closed',
                'applicant_skill_ids', 'skill_ids']})
for a in active:
    print(f"  {a['partner_name']}")
    for k, v in sorted(a.items()):
        if k != 'partner_name':
            print(f"    {k}: {v}")

# Interview-related fields
print("\n--- Interview/Survey/Refuse Fields on hr.applicant ---")
app_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'fields_get', [],
    {'attributes': ['string', 'type']})
for fname, fdata in sorted(app_fields.items()):
    if any(x in fname.lower() for x in ['interview', 'survey', 'refuse', 'talent', 'archive', 'employee_id']):
        print(f"  {fname} ({fdata['type']}): {fdata['string']}")

# Talent pool fields check
print("\n--- Talent Pool Check ---")
try:
    tp_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.talent.pool', 'fields_get', [],
        {'attributes': ['string', 'type']})
    print(f"  hr.talent.pool exists with {len(tp_fields)} fields")
    for f, d in sorted(tp_fields.items()):
        print(f"    {f} ({d['type']}): {d['string']}")
except Exception as e:
    print(f"  hr.talent.pool error: {e}")

# Check if there's a way to add to talent pool from applicant
print("\n--- Applicant Talent Pool Fields ---")
for fname, fdata in sorted(app_fields.items()):
    if 'talent' in fname.lower() or 'pool' in fname.lower():
        print(f"  {fname} ({fdata['type']}): {fdata['string']}")

# Check what happens with refuse_date
print("\n--- Refuse-related fields ---")
for fname, fdata in sorted(app_fields.items()):
    if 'refuse' in fname.lower() or 'lost' in fname.lower():
        print(f"  {fname} ({fdata['type']}): {fdata['string']}")

# Job position fields relevant to website
print("\n--- hr.job Website Fields ---")
job_fields = models.execute_kw(DB, uid, PASSWORD, 'hr.job', 'fields_get', [],
    {'attributes': ['string', 'type']})
for fname, fdata in sorted(job_fields.items()):
    if any(x in fname.lower() for x in ['website', 'publish', 'online', 'seo', 'cover']):
        print(f"  {fname} ({fdata['type']}): {fdata['string']}")

# All hr.job fields (just key ones)
print("\n--- hr.job Key Fields ---")
for fname, fdata in sorted(job_fields.items()):
    if any(x in fname.lower() for x in ['salary', 'payment', 'degree', 'industry', 'detail', 'process', 'days', 'answer', 'offer']):
        print(f"  {fname} ({fdata['type']}): {fdata['string']}")

print("\nDONE")
