#!/usr/bin/env python3
"""
Deep investigation of the 3 Referral reports on demo-tech.odoo.com:
1. Referral Analysis (hr.referral.report)
2. Points Report (hr.referral.points.report)  
3. Rewards Report (hr.referral.reward.report)

Also check the underlying data models thoroughly.
"""

import xmlrpc.client
import json

URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

def pretty(obj):
    return json.dumps(obj, indent=2, default=str)

def main():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(DB, USERNAME, PASSWORD, {})
    print(f"Authenticated: UID={uid}")
    
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)

    def search_read(model, domain=[], fields=[], limit=0, order=''):
        kw = {'fields': fields}
        if limit: kw['limit'] = limit
        if order: kw['order'] = order
        return models.execute_kw(DB, uid, PASSWORD, model, 'search_read', [domain], kw)

    def search_count(model, domain=[]):
        return models.execute_kw(DB, uid, PASSWORD, model, 'search_count', [domain])

    def fields_get(model, attrs=['string','type','help','selection']):
        return models.execute_kw(DB, uid, PASSWORD, model, 'fields_get', [], {'attributes': attrs})

    # ═══════════════════════════════════════════════════════════════
    # REPORT 1: REFERRAL ANALYSIS (hr.referral.report)
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("REPORT 1: REFERRAL ANALYSIS — hr.referral.report")
    print("=" * 70)

    # Fields
    print("\n--- Fields on hr.referral.report ---")
    rf = fields_get('hr.referral.report')
    for fname, fdata in sorted(rf.items()):
        if fname.startswith('__') or fname in ('id','display_name','create_uid','write_uid','create_date','write_date'):
            continue
        sel = ''
        if fdata.get('selection'):
            sel = f" | Selections: {fdata['selection']}"
        print(f"  {fname:30s} | {fdata['string']:30s} | {fdata['type']}{sel}")

    # All records
    print("\n--- All records in hr.referral.report ---")
    try:
        rr_count = search_count('hr.referral.report')
        print(f"Total records: {rr_count}")
        rr_records = search_read('hr.referral.report', [], [])
        for r in rr_records:
            print(f"\n  Record ID={r['id']}:")
            for k, v in r.items():
                if k not in ('id', 'display_name', '__last_update'):
                    print(f"    {k}: {v}")
    except Exception as e:
        print(f"Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # REPORT 2: POINTS REPORT (hr.referral.points.report)
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("REPORT 2: POINTS — hr.referral.points.report")
    print("=" * 70)

    print("\n--- Fields on hr.referral.points.report ---")
    try:
        pf = fields_get('hr.referral.points.report')
        for fname, fdata in sorted(pf.items()):
            if fname.startswith('__') or fname in ('id','display_name','create_uid','write_uid','create_date','write_date'):
                continue
            sel = ''
            if fdata.get('selection'):
                sel = f" | Selections: {fdata['selection']}"
            print(f"  {fname:30s} | {fdata['string']:30s} | {fdata['type']}{sel}")
    except Exception as e:
        print(f"Error getting fields: {e}")

    print("\n--- All records in hr.referral.points.report ---")
    try:
        pp_count = search_count('hr.referral.points.report')
        print(f"Total records: {pp_count}")
        pp_records = search_read('hr.referral.points.report', [], [])
        for r in pp_records:
            print(f"\n  Record ID={r['id']}:")
            for k, v in r.items():
                if k not in ('id', 'display_name', '__last_update'):
                    print(f"    {k}: {v}")
    except Exception as e:
        print(f"Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # REPORT 3: REWARDS REPORT (hr.referral.reward.report)
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("REPORT 3: REWARDS — hr.referral.reward.report")
    print("=" * 70)

    print("\n--- Fields on hr.referral.reward.report ---")
    try:
        wf = fields_get('hr.referral.reward.report')
        for fname, fdata in sorted(wf.items()):
            if fname.startswith('__') or fname in ('id','display_name','create_uid','write_uid','create_date','write_date'):
                continue
            sel = ''
            if fdata.get('selection'):
                sel = f" | Selections: {fdata['selection']}"
            print(f"  {fname:30s} | {fdata['string']:30s} | {fdata['type']}{sel}")
    except Exception as e:
        print(f"Error getting fields: {e}")

    print("\n--- All records in hr.referral.reward.report ---")
    try:
        wr_count = search_count('hr.referral.reward.report')
        print(f"Total records: {wr_count}")
        wr_records = search_read('hr.referral.reward.report', [], [])
        for r in wr_records:
            print(f"\n  Record ID={r['id']}:")
            for k, v in r.items():
                if k not in ('id', 'display_name', '__last_update'):
                    print(f"    {k}: {v}")
    except Exception as e:
        print(f"Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # ALSO CHECK: hr.referral.points (raw data behind reports)
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("RAW DATA: hr.referral.points")
    print("=" * 70)
    try:
        pts_count = search_count('hr.referral.points')
        print(f"Total point entries: {pts_count}")
        if pts_count > 0:
            pts = search_read('hr.referral.points', [], [])
            for p in pts:
                print(f"\n  Point Entry ID={p['id']}:")
                for k, v in p.items():
                    if k not in ('id', 'display_name', '__last_update'):
                        print(f"    {k}: {v}")
    except Exception as e:
        print(f"Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # CHECK: Referral-related fields on hr.applicant
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("APPLICANT REFERRAL FIELDS")
    print("=" * 70)
    af = fields_get('hr.applicant')
    ref_fields = {k: v for k, v in af.items() if 'ref' in k.lower() or 'source' in k.lower() or 'medium' in k.lower()}
    for fname, fdata in sorted(ref_fields.items()):
        print(f"  {fname:30s} | {fdata['string']:30s} | {fdata['type']}")

    # Check source/medium on applicants
    print("\n--- Applicant source/medium data ---")
    apps = search_read('hr.applicant', [], 
                        ['partner_name','stage_id','source_id','medium_id','ref_user_id'], limit=20)
    for a in apps:
        print(f"  {a.get('partner_name','N/A'):25s} | Stage: {a.get('stage_id','N/A')} | Source: {a.get('source_id','N/A')} | Medium: {a.get('medium_id','N/A')} | Ref User: {a.get('ref_user_id','N/A')}")

    # Check archived too
    print("\n--- Archived applicants source/medium ---")
    arch = search_read('hr.applicant', [('active','=',False)],
                        ['partner_name','stage_id','source_id','medium_id','ref_user_id'])
    for a in arch:
        print(f"  {a.get('partner_name','N/A'):25s} | Stage: {a.get('stage_id','N/A')} | Source: {a.get('source_id','N/A')} | Medium: {a.get('medium_id','N/A')} | Ref User: {a.get('ref_user_id','N/A')}")

    # ═══════════════════════════════════════════════════════════════
    # CHECK: utm.source and utm.medium for referral tracking
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("UTM SOURCES & MEDIUMS")
    print("=" * 70)
    try:
        sources = search_read('utm.source', [], ['name'])
        print(f"UTM Sources ({len(sources)}):")
        for s in sources:
            print(f"  ID={s['id']} | {s['name']}")
    except Exception as e:
        print(f"Error: {e}")

    try:
        mediums = search_read('utm.medium', [], ['name'])
        print(f"\nUTM Mediums ({len(mediums)}):")
        for m in mediums:
            print(f"  ID={m['id']} | {m['name']}")
    except Exception as e:
        print(f"Error: {e}")

    # ═══════════════════════════════════════════════════════════════
    # CHECK: Any reward purchase/redemption records
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("REWARD DETAILS")
    print("=" * 70)
    rewards = search_read('hr.referral.reward', [], [])
    print(f"Total rewards: {len(rewards)}")
    for rw in rewards:
        print(f"\n  Reward ID={rw['id']}:")
        for k, v in rw.items():
            if k not in ('id','display_name','__last_update') and not k.startswith('image') and not k.startswith('photo'):
                print(f"    {k}: {v}")

    print("\n" + "=" * 70)
    print("INVESTIGATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
