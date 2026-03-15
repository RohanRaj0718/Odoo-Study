"""
Discover Odoo 19 field names for models that failed.
"""
import xmlrpc.client
import sys

URL = "https://demo-tech.odoo.com"
DB = "demo-tech"
USERNAME = "rohan.raj@infintor.com"
PASSWORD = "Rohanraj@1"

common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', allow_none=True)
uid = common.authenticate(DB, USERNAME, PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', allow_none=True)

def get_fields(model, filter_str=None):
    """Get fields for a model."""
    try:
        fields = models.execute_kw(DB, uid, PASSWORD, model, 'fields_get', [],
            {'attributes': ['string', 'type', 'required', 'selection']})
        results = []
        for fname, info in sorted(fields.items()):
            if filter_str and filter_str.lower() not in fname.lower() and filter_str.lower() not in info.get('string', '').lower():
                continue
            sel = ""
            if info.get('selection'):
                sel = f" SELECTION={info['selection']}"
            req = " [REQUIRED]" if info.get('required') else ""
            results.append(f"  {fname:40s} | {info['type']:12s} | {info.get('string','')}{req}{sel}")
        return results
    except Exception as e:
        return [f"  ERROR: {e}"]

# 1. Product template - find the correct 'type' field values
print("=" * 90)
print("PRODUCT.TEMPLATE - type field and related")
print("=" * 90)
for line in get_fields('product.template', 'type'):
    print(line)

print("\n" + "=" * 90)
print("PRODUCT.TEMPLATE - all storable/product related")
print("=" * 90)
for line in get_fields('product.template', 'stor'):
    print(line)

# 2. Work Center - find the correct capacity field
print("\n" + "=" * 90)
print("MRP.WORKCENTER - capacity and cost fields")
print("=" * 90)
for line in get_fields('mrp.workcenter', 'capac'):
    print(line)
for line in get_fields('mrp.workcenter', 'cost'):
    print(line)
for line in get_fields('mrp.workcenter', 'time'):
    print(line)

# 3. Maintenance equipment - find the correct period field
print("\n" + "=" * 90)
print("MAINTENANCE.EQUIPMENT - period/frequency fields")
print("=" * 90)
for line in get_fields('maintenance.equipment', 'period'):
    print(line)
for line in get_fields('maintenance.equipment', 'frequen'):
    print(line)
for line in get_fields('maintenance.equipment', 'prevent'):
    print(line)
for line in get_fields('maintenance.equipment', 'maint'):
    print(line)

# 4. Check product type selection values specifically
print("\n" + "=" * 90)
print("PRODUCT.TEMPLATE.TYPE selection values")
print("=" * 90)
try:
    fields = models.execute_kw(DB, uid, PASSWORD, 'product.template', 'fields_get', [],
        {'attributes': ['string', 'type', 'selection']})
    type_field = fields.get('type', {})
    print(f"  Field 'type': {type_field.get('string')}")
    print(f"  Selection values: {type_field.get('selection')}")
except Exception as e:
    print(f"  ERROR: {e}")

# 5. Check all required fields for mrp.workcenter
print("\n" + "=" * 90)
print("MRP.WORKCENTER - ALL FIELDS")
print("=" * 90)
for line in get_fields('mrp.workcenter'):
    print(line)

# 6. Check maintenance.equipment ALL fields
print("\n" + "=" * 90)
print("MAINTENANCE.EQUIPMENT - ALL FIELDS")
print("=" * 90)
for line in get_fields('maintenance.equipment'):
    print(line)

# 7. Check mrp.routing.workcenter (operations) fields
print("\n" + "=" * 90)
print("MRP.ROUTING.WORKCENTER - ALL FIELDS")
print("=" * 90)
try:
    for line in get_fields('mrp.routing.workcenter'):
        print(line)
except:
    print("  Model may not exist - checking mrp.operation")
    try:
        for line in get_fields('mrp.operation'):
            print(line)
    except:
        print("  Neither mrp.routing.workcenter nor mrp.operation found")

# 8. Quality point fields
print("\n" + "=" * 90)
print("QUALITY.POINT - key fields")
print("=" * 90)
try:
    for line in get_fields('quality.point'):
        print(line)
except Exception as e:
    print(f"  ERROR: {e}")

