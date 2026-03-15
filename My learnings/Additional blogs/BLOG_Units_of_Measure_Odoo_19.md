# How to Use Units of Measure in Odoo 19

**Rohan Raj  |  Mar 9, 2026**

Buying fabric in meters but selling it in yards? Purchasing chemicals in drums but consuming them in liters? Odoo 19's **Units of Measure (UoM)** feature handles all conversions automatically — across purchases, sales, inventory, and manufacturing — so you never have to calculate manually.

## Enabling Units of Measure

Go to **Inventory App** → Configuration → Settings → Products section

Enable the **Units of Measure & Packagings** checkbox and click **Save**.

[Image: Units of Measure & Packagings setting enabled in Inventory configuration]

## Configuring UoM on a Product

Go to **Inventory App** → Products → Products → select a product

### Inventory Unit of Measure

The inventory UoM defines how the product is tracked internally. Set it using the unit field next to the **Sales Price** or **Cost** fields on the product form.

For example, if you track blue fabric in *yards*, set the unit to "yard." This unit is used across all internal inventory operations — stock counts, internal transfers, and warehouse reports.

[Image: Product form showing inventory unit of measure set to yard]

### Purchase Unit of Measure

Open the **Purchase** tab on the product form. In the vendor pricelist, the **Unit** column defines the unit used when purchasing from each vendor.

For example, if your vendor sells fabric in *meters*, set the purchase unit to "m" in the vendor line. When you create a purchase order, it shows meters. When the goods arrive, the warehouse receipt automatically converts the quantity to your inventory unit (yards).

[Image: Purchase tab showing vendor unit set to meters]

### Sales Packagings

Open the **Sales** tab on the product form. Under **Upsell & Cross-Sell**, add packagings to the **Packagings** field. Packagings define the units the product is sold in — for example, selling paint in "Boxes of 12 cans."

[Image: Sales tab with packaging defined]

## How Automatic Conversion Works

Odoo converts units automatically at every handoff:

| Transaction | Unit Used | Converts To |
|-------------|-----------|-------------|
| **Purchase Order** | Purchase UoM (e.g., meters) | — |
| **Warehouse Receipt** | Inventory UoM (e.g., yards) | Automatic on receipt |
| **Sales Order** | Sales UoM (e.g., meters) | — |
| **Delivery Order** | Inventory UoM (e.g., yards) | Automatic on delivery |

You place a purchase order for 10 meters of fabric. The warehouse receipt shows 10.94 yards (the converted quantity). No manual math needed.

[Image: Purchase order in meters and warehouse receipt showing converted yards]

## Creating Custom Units of Measure

Go to **Inventory App** → Configuration → Units & Packagings → **New**

Enter the unit name, then specify the conversion by entering a **Quantity** relative to a **Reference Unit**. Odoo uses this ratio for all automatic conversions.

For example, to create "yard" as a custom unit: set Quantity to `0.9144` and Reference Unit to `m`. This tells Odoo that 1 yard = 0.9144 meters.

[Image: Custom UoM configuration showing yard to meter conversion]

All custom units must belong to a **UoM Category** (e.g., Length, Weight, Volume). Units within the same category can convert between each other. Units in different categories cannot.

## FAQ's

1. **Can I use different units for buying and selling the same product?**
Yes. Set the purchase unit in the **Purchase** tab vendor pricelist and the inventory unit in the **Sales Price** field. Odoo converts between them automatically on receipts and deliveries, as long as both units belong to the same UoM category.

2. **What happens if I change the unit of measure on an existing product?**
Changing the UoM on a product with existing inventory can cause stock discrepancies. It's best to set the correct UoM before recording any stock movements. If a change is necessary, adjust your inventory quantities accordingly.

3. **Can I track inventory in one unit and display a different unit on invoices?**
Yes. The sales order uses the unit specified on the order line (which can differ from the inventory unit). Invoices reflect the sales order unit, while warehouse operations use the inventory unit.

Looking to configure multi-unit inventory management in Odoo 19? Connect with the experts at [Infintor](https://www.infintor.com/) for a customized consultation.
