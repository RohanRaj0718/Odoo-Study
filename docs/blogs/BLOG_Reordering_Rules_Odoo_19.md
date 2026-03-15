# Setting Up Reordering Rules in Odoo 19

**Rohan Raj  |  Mar 9, 2026**

Running out of stock means lost sales. Overstocking ties up capital. Odoo 19's **Reordering Rules** solve both problems by automatically generating purchase or manufacturing orders when stock falls below a defined threshold — keeping inventory at the right level without manual tracking.

## Configuring the Product

Go to **Inventory App** → Products → Products → select a product

Under the **General Information** tab, set the **Product Type** to *Goods* and enable **Track Inventory**. Without these two settings, Odoo cannot monitor stock levels for the product.

If the product is purchased, open the **Purchase** tab and add at least one vendor to the vendor pricelist. If the product is manufactured, ensure a **Bill of Materials** exists (visible via the smart button at the top).

[Image: Product form with Product Type set to Goods and Track Inventory enabled]

## Creating a Reordering Rule

Go to **Inventory App** → Operations → Replenishment → **New**

Fill in the following fields:

| Field | What to Set |
|-------|------------|
| **Product** | Select the product to replenish |
| **Location** | Where stock is stored (default: WH/Stock) |
| **Min** | Minimum forecasted quantity before the rule triggers (e.g., `10`) |
| **Max** | Target quantity to replenish up to (e.g., `50`) |

When the forecasted quantity drops below **Min**, Odoo automatically creates a purchase order (for Buy route) or manufacturing order (for Manufacture route) to bring stock back up to **Max**.

[Image: Reordering rule form with Min 10 and Max 50 configured]

You can also create reordering rules directly from the product form by clicking the **Reordering Rules** smart button at the top.

## Choosing Automatic vs Manual Trigger

By default, reordering rules trigger automatically. To see or change this, click the settings icon on the Replenishment page and enable the **Trigger** column.

| Trigger | How It Works |
|---------|-------------|
| **Auto** | Purchase/manufacturing order is created automatically when forecasted stock falls below Min — either when the scheduler runs or when a sales order is confirmed |
| **Manual** | The product appears on the Replenishment dashboard as a "need" — you review it and click **Order** to generate the purchase/manufacturing order |

Use **Auto** for fast-moving products that should never run out. Use **Manual** for expensive or slow-moving items where you want to review before ordering.

[Image: Trigger column showing Auto selected on a reordering rule]

The automatic scheduler runs once daily. To trigger it immediately, enable **Developer Mode** and go to Inventory → Operations → **Run Scheduler**.

## Setting a Preferred Route

If a product has both **Buy** and **Manufacture** routes enabled, you can set a preferred route on the reordering rule. Enable the **Route** column on the Replenishment page (via the settings icon), then select the desired route from the dropdown.

If no preferred route is set, Odoo defaults to the **Buy** route first, then Manufacture.

[Image: Route column with Buy selected as preferred route]

## The 0/0/1 Rule for Make-to-Order Without Reservation

A special variation: set **Min = 0**, **Max = 0**, and **To Order = 1**. This creates a purchase or manufacturing order every time a sales order causes the forecasted quantity to drop below zero — effectively a make-to-order workflow, but without reserving the stock for a specific sales order.

[Image: Reordering rule with Min 0, Max 0, To Order 1]

## FAQ's

1. **What's the difference between Min and Max?**
**Min** is the trigger point — when forecasted stock falls below this number, replenishment kicks in. **Max** is the target — Odoo orders enough to bring stock back up to this quantity. The difference between Max and the current forecast is the quantity ordered.

2. **Can I set reordering rules for multiple products at once?**
Yes. Navigate to Inventory → Operations → Replenishment and click **New** for each product. You can create and manage all reordering rules from this single page.

3. **Does the reordering rule work with the Manufacture route?**
Yes. If the product has a Bill of Materials and the Manufacture route is enabled, the reordering rule generates a manufacturing order instead of a purchase order when triggered.

Looking to automate your inventory replenishment in Odoo 19? Connect with the experts at [Infintor](https://www.infintor.com/) for a customized consultation.
