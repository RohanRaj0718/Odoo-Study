"""Check stock.move fields in Odoo 19"""
import xmlrpc.client
URL='https://client-cient.odoo.com'; DB='client-cient'; U='rohan.raj@infintor.com'; P='Rohanraj@1'
common=xmlrpc.client.ServerProxy(URL+'/xmlrpc/2/common',allow_none=True)
uid=common.authenticate(DB,U,P,{})
models=xmlrpc.client.ServerProxy(URL+'/xmlrpc/2/object',allow_none=True)

fields = models.execute_kw(DB,uid,P,'stock.move','fields_get',[],{'attributes':['string','type','required']})
print("STOCK.MOVE FIELDS (Odoo 19):")
for fname in sorted(fields.keys()):
    f = fields[fname]
    req = ' [REQUIRED]' if f.get('required') else ''
    print(f"  {fname:40s} | {f['type']:15s} | {f['string']}{req}")
