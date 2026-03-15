"""
PASS 2: Get remaining referral data — fix field names from errors, discover actual fields.
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
print("1. DISCOVER FIELDS ON hr.referral.onboarding")
print("=" * 70)
try:
    fields = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.onboarding', 'fields_get',
        [], {'attributes': ['string', 'type']})
    for fname, fdata in sorted(fields.items()):
        print(f"  {fname}: {fdata.get('string')} ({fdata.get('type')})")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================
print("\n" + "=" * 70)
print("2. DISCOVER FIELDS ON hr.referral.level")
print("=" * 70)
try:
    fields = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.level', 'fields_get',
        [], {'attributes': ['string', 'type']})
    for fname, fdata in sorted(fields.items()):
        print(f"  {fname}: {fdata.get('string')} ({fdata.get('type')})")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================
print("\n" + "=" * 70)
print("3. DISCOVER REFERRAL FIELDS ON hr.applicant")
print("=" * 70)
try:
    fields = models.execute_kw(DB, uid, PASSWORD, 'hr.applicant', 'fields_get',
        [], {'attributes': ['string', 'type']})
    ref_fields = {k: v for k, v in fields.items() if 'refer' in k.lower() or 'ref_' in k.lower() or 'referral' in v.get('string', '').lower()}
    for fname, fdata in sorted(ref_fields.items()):
        print(f"  {fname}: {fdata.get('string')} ({fdata.get('type')})")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================
print("\n" + "=" * 70)
print("4. DISCOVER FIELDS ON hr.referral.reward")
print("=" * 70)
try:
    fields = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.reward', 'fields_get',
        [], {'attributes': ['string', 'type']})
    for fname, fdata in sorted(fields.items()):
        print(f"  {fname}: {fdata.get('string')} ({fdata.get('type')})")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================
print("\n" + "=" * 70)
print("5. DISCOVER FIELDS ON hr.referral.alert")
print("=" * 70)
try:
    fields = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.alert', 'fields_get',
        [], {'attributes': ['string', 'type']})
    for fname, fdata in sorted(fields.items()):
        print(f"  {fname}: {fdata.get('string')} ({fdata.get('type')})")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================
print("\n" + "=" * 70)
print("6. DISCOVER FIELDS ON hr.referral.points")
print("=" * 70)
try:
    fields = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.points', 'fields_get',
        [], {'attributes': ['string', 'type']})
    for fname, fdata in sorted(fields.items()):
        print(f"  {fname}: {fdata.get('string')} ({fdata.get('type')})")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================
print("\n" + "=" * 70)
print("7. ALL REFERRAL-RELATED MODELS")
print("=" * 70)
try:
    ref_models = models.execute_kw(DB, uid, PASSWORD, 'ir.model', 'search_read',
        [[['model', 'like', 'hr.referral']]],
        {'fields': ['model', 'name']})
    for rm in ref_models:
        print(f"  {rm['model']} — {rm['name']}")
except Exception as e:
    print(f"  Error: {e}")

# ============================================================
print("\n" + "=" * 70)
print("8. DISCOVER FIELDS ON hr.referral.friend")
print("=" * 70)
try:
    fields = models.execute_kw(DB, uid, PASSWORD, 'hr.referral.friend', 'fields_get',
        [], {'attributes': ['string', 'type']})
    for fname, fdata in sorted(fields.items()):
        print(f"  {fname}: {fdata.get('string')} ({fdata.get('type')})")
except Exception as e:
    print(f"  Error: {e}")
