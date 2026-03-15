import xmlrpc.client
URL='https://demo-tech.odoo.com'; DB='demo-tech'; U='rohan.raj@infintor.com'; P='Rohanraj@1'
common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, U, P, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

for model_name in ['mrp.workcenter', 'mrp.bom', 'mrp.routing.workcenter']:
    print(f"\n{'='*70}\n{model_name}\n{'='*70}")
    fields = models.execute_kw(DB, uid, P, model_name, 'fields_get', [], {'attributes': ['string','type']})
    for fname, info in sorted(fields.items()):
        print(f"  {fname:45s} {info['type']:15s} {info['string']}")
