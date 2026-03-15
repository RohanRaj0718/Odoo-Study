import xmlrpc.client
URL='https://client-cient.odoo.com'; DB='client-cient'; U='rohan.raj@infintor.com'; P='Rohanraj@1'
common=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common',allow_none=True)
uid=common.authenticate(DB,U,P,{})
models=xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object',allow_none=True)

# Check for is_storable or tracking related fields
fields = models.execute_kw(DB,uid,P,'product.template','fields_get',[],{'attributes':['string','type']})
for k,v in sorted(fields.items()):
    s = v.get('string','')
    if 'storab' in k.lower() or 'storab' in s.lower() or k == 'is_storable' or k == 'tracking':
        print(f"  {k}: {s} ({v['type']})")

# Check a product's current fields
prods = models.execute_kw(DB,uid,P,'product.template','search_read',[[['name','=','PVC Blinds']]],{'fields':['name','type','is_storable','tracking']})
print("\nPVC Blinds product:")
for p in prods:
    print(p)
