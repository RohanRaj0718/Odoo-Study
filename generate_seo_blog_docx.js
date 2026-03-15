const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, LevelFormat, ExternalHyperlink
} = require("docx");

// ─── Shared style config ───
const FONT = "Arial";
const PAGE_WIDTH = 12240;
const MARGINS = { top: 1440, right: 1440, bottom: 1440, left: 1440 };
const CONTENT_WIDTH = PAGE_WIDTH - MARGINS.left - MARGINS.right;
const BRAND_COLOR = "1B4F72";
const ACCENT_COLOR = "D5E8F0";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

function makeDoc(title, author, date, sections) {
  return new Document({
    styles: {
      default: { document: { run: { font: FONT, size: 22 } } },
      paragraphStyles: [
        {
          id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 32, bold: true, font: FONT, color: BRAND_COLOR },
          paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 }
        },
        {
          id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 26, bold: true, font: FONT, color: BRAND_COLOR },
          paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 }
        },
        {
          id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 24, bold: true, font: FONT, color: "2C3E50" },
          paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 }
        },
      ]
    },
    numbering: {
      config: [
        {
          reference: "bullets",
          levels: [{
            level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } }
          }]
        },
        {
          reference: "numbers",
          levels: [{
            level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } }
          }]
        },
      ]
    },
    sections: [{
      properties: {
        page: {
          size: { width: PAGE_WIDTH, height: 15840 },
          margin: MARGINS
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [new TextRun({ text: "Infintor Solutions", font: FONT, size: 18, color: "888888", italics: true })]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: "Page ", font: FONT, size: 18, color: "888888" }),
              new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18, color: "888888" }),
            ]
          })]
        })
      },
      children: [
        new Paragraph({
          spacing: { after: 80 },
          children: [new TextRun({ text: title, bold: true, size: 36, font: FONT, color: BRAND_COLOR })]
        }),
        new Paragraph({
          spacing: { after: 400 },
          children: [new TextRun({ text: `${author}  |  ${date}`, size: 20, font: FONT, color: "666666" })]
        }),
        ...sections
      ]
    }]
  });
}

function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
}

function h3(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(text)] });
}

function p(text) {
  const runs = [];
  const parts = text.split(/(\*\*[^*]+\*\*)/);
  for (const part of parts) {
    if (part.startsWith("**") && part.endsWith("**")) {
      runs.push(new TextRun({ text: part.slice(2, -2), bold: true, font: FONT, size: 22 }));
    } else {
      runs.push(new TextRun({ text: part, font: FONT, size: 22 }));
    }
  }
  return new Paragraph({ spacing: { after: 160 }, children: runs });
}

function bullet(text) {
  const runs = [];
  const parts = text.split(/(\*\*[^*]+\*\*)/);
  for (const part of parts) {
    if (part.startsWith("**") && part.endsWith("**")) {
      runs.push(new TextRun({ text: part.slice(2, -2), bold: true, font: FONT, size: 22 }));
    } else {
      runs.push(new TextRun({ text: part, font: FONT, size: 22 }));
    }
  }
  return new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: runs });
}

function numItem(text) {
  const runs = [];
  const parts = text.split(/(\*\*[^*]+\*\*)/);
  for (const part of parts) {
    if (part.startsWith("**") && part.endsWith("**")) {
      runs.push(new TextRun({ text: part.slice(2, -2), bold: true, font: FONT, size: 22 }));
    } else {
      runs.push(new TextRun({ text: part, font: FONT, size: 22 }));
    }
  }
  return new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 80 }, children: runs });
}

function nav(text) {
  return new Paragraph({
    spacing: { after: 120 },
    shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
    children: [new TextRun({ text, font: FONT, size: 22, italics: true })]
  });
}

function imgPlaceholder(desc) {
  return new Paragraph({
    spacing: { before: 120, after: 200 },
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: `[Image: ${desc}]`, font: FONT, size: 20, color: "999999", italics: true })]
  });
}

function makeTable(headers, rows, colWidths) {
  const totalWidth = colWidths.reduce((a, b) => a + b, 0);
  const headerCells = headers.map((h, i) => new TableCell({
    borders,
    width: { size: colWidths[i], type: WidthType.DXA },
    shading: { fill: BRAND_COLOR, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, font: FONT, size: 20, color: "FFFFFF" })] })]
  }));
  const dataRows = rows.map(row => new TableRow({
    children: row.map((cell, i) => new TableCell({
      borders,
      width: { size: colWidths[i], type: WidthType.DXA },
      margins: { top: 60, bottom: 60, left: 120, right: 120 },
      children: [new Paragraph({ children: [new TextRun({ text: cell, font: FONT, size: 20 })] })]
    }))
  }));
  return new Table({
    width: { size: totalWidth, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [new TableRow({ children: headerCells }), ...dataRows]
  });
}

function spacer() {
  return new Paragraph({ spacing: { after: 80 }, children: [] });
}

function faqItem(num, question, answer) {
  return [
    new Paragraph({
      spacing: { before: 200, after: 80 },
      children: [new TextRun({ text: `${num}. ${question}`, bold: true, font: FONT, size: 22 })]
    }),
    p(answer)
  ];
}

function cta(text) {
  return new Paragraph({
    spacing: { before: 300, after: 200 },
    shading: { fill: ACCENT_COLOR, type: ShadingType.CLEAR },
    children: [new TextRun({ text, font: FONT, size: 22, italics: true, color: BRAND_COLOR })]
  });
}

// ═══════════════════════════════════════════════════════════════
// SEO BLOG 1: Product Discounts Using Pricelists (Deep Guide)
// ═══════════════════════════════════════════════════════════════
const seoBlog1Sections = [
  // Introduction
  p("Pricing is one of the most critical levers in any business. Whether you are running a wholesale distribution company, a retail chain, or a manufacturing unit, offering the right discount at the right time can be the difference between closing a deal and losing a customer. Yet, many businesses still rely on manual price adjustments \u2014 salespeople entering discounts from memory, inconsistent pricing across teams, and no audit trail of what discount was offered to which customer."),
  p("This is where **product discounts in Odoo 19** become essential. Odoo\u2019s Pricelist feature allows businesses to define structured discount rules that apply automatically across sales orders, eliminating manual errors and ensuring pricing consistency. Whether you need a simple \"10% off for all wholesale customers\" or a complex tiered structure like \"5% off for 10 units, 15% off for 50 units, 25% off for 100 units,\" Odoo 19 handles it through configurable price rules."),
  p("In this guide, we walk through the complete process of setting up product discounts in Odoo 19 using pricelists \u2014 from enabling the feature to verifying the discount on a live sales order. This article is intended for business analysts, ERP managers, and functional consultants who want to implement a reliable, automated pricing strategy in Odoo."),

  // What Are Pricelists
  h2("What Are Pricelists in Odoo 19?"),
  p("A **pricelist** in Odoo is a set of pricing rules that override the default sales price on a product. When a pricelist is assigned to a customer or applied to a sales order, Odoo evaluates the rules within that pricelist and adjusts product prices accordingly."),
  p("Pricelists are not limited to discounts. They can also be used to:"),
  bullet("Increase prices (markups) for certain customer segments"),
  bullet("Set fixed prices for promotional periods"),
  bullet("Apply formula-based pricing with rounding and surcharges"),
  bullet("Create time-bound pricing valid only during specific date ranges"),
  bullet("Define quantity-based tiered pricing for bulk purchases"),
  p("Odoo 19 supports pricelists across the **Sales**, **eCommerce**, and **Point of Sale** applications, making it a unified pricing engine for all sales channels."),

  h3("Key Concepts"),
  p("Before configuring pricelists, it helps to understand the three **Price Types** available in Odoo 19\u2019s pricelist rules:"),
  spacer(),
  makeTable(
    ["Price Type", "How It Works", "Discount Visible to Customer?"],
    [
      ["Discount", "Applies a percentage reduction to the product\u2019s sales price", "Yes \u2014 shown as a separate Disc.% column"],
      ["Formula", "Calculates a new price using discount %, rounding, and extra fees", "No \u2014 only the adjusted unit price is shown"],
      ["Fixed Price", "Sets a flat price regardless of the product\u2019s configured sales price", "No \u2014 the fixed price replaces the unit price"],
    ],
    [2340, 4680, 2340]
  ),
  spacer(),
  p("Understanding this distinction is critical because it affects what the customer sees on quotations and invoices."),

  // Step 1
  h2("Step 1: Enabling the Pricelists Feature"),
  p("The pricelist feature is not enabled by default in Odoo 19. To activate it:"),
  numItem("Navigate to **Sales \u2192 Configuration \u2192 Settings**"),
  numItem("Scroll to the **Pricing** section"),
  numItem("Enable the **Pricelists** checkbox"),
  numItem("Click **Save**"),
  p("Once enabled, a new menu item appears under **Sales \u2192 Products \u2192 Pricelists**, where all pricelists can be created and managed."),
  p("It is also recommended to enable the **Discounts** checkbox in the same Pricing section. This adds a **Disc.%** column to sales order lines, making the discount percentage visible when the Discount price type is used."),
  imgPlaceholder("Pricelists and Discounts settings enabled in Sales Configuration"),

  // Step 2
  h2("Step 2: Creating a New Pricelist"),
  nav("Sales \u2192 Products \u2192 Pricelists \u2192 New"),
  p("Configure the following fields on the pricelist form:"),
  bullet("**Pricelist Name**: Enter a descriptive name (e.g., \"Wholesale Discount \u2014 Electronics\" or \"Festive Season Pricing\")"),
  bullet("**Currency**: Select the applicable currency (e.g., INR for Indian operations)"),
  bullet("**Company**: In multi-company setups, assign the pricelist to a specific company. Leave blank to apply across all companies"),
  bullet("**Country Groups**: If selling internationally, assign country groups to restrict this pricelist to specific regions"),
  p("The pricelist form also contains tabs for **Price Rules**, **Recurring Prices** (for subscriptions), and **Rental Rules**. For product discounts, we will focus on the **Price Rules** tab."),
  imgPlaceholder("New pricelist form with name, currency, and company configured"),

  // Step 3
  h2("Step 3: Configuring Price Rules for Product Discounts"),
  p("Click on the **Price Rules** tab and select **Add a line** to create a new pricing rule."),

  h3("Apply To"),
  p("Choose the scope of the rule:"),
  bullet("**All Products**: The discount applies to every product in the catalog"),
  bullet("**Product Category**: The discount applies to all products within a selected category (e.g., \"Electronics\" or \"Office Supplies\")"),
  bullet("**Product**: The discount applies to a specific product only"),
  bullet("**Product Variant**: The discount applies to a specific variant (e.g., \"Laptop Stand \u2014 Black, Large\")"),
  p("For most B2B discount scenarios, selecting **Product** or **Product Category** is appropriate."),

  h3("Price Type: Discount"),
  p("Select **Discount** as the price type. Enter the discount percentage in the **Discount** field."),
  p("For example, entering 15 applies a 15% discount to the product\u2019s sales price. This discount is visible to the customer on quotations and invoices as a separate column."),
  p("To create a **markup** (price increase), enter a negative value. For instance, -20 increases the price by 20%."),

  h3("Price Type: Formula"),
  p("Select **Formula** for more advanced pricing control. The formula price type offers three sub-fields:"),
  bullet("**Discount**: Percentage discount (or negative for markup)"),
  bullet("**Round off to**: Rounds the price to the nearest multiple (e.g., 10 rounds to the nearest 10). Rounding is applied after the discount"),
  bullet("**Extra Fee**: A fixed amount added or subtracted after discount and rounding"),
  p("**Example**: To create retail pricing ending in \u20b9X99: Discount: 20 (20% off), Round off to: 100, Extra Fee: -1. Result: A \u20b95,000 product becomes \u20b94,000 (20% off) \u2192 \u20b94,000 (already a multiple of 100) \u2192 \u20b93,999."),
  p("The formula price type does **not** show the discount percentage to the customer \u2014 only the adjusted unit price appears."),

  h3("Price Type: Fixed Price"),
  p("Select **Fixed Price** to set a flat price for the product. This is useful for promotional pricing where a product is offered at a specific price point regardless of its standard sales price."),

  h3("Minimum Quantity"),
  p("The **Min Qty** field is the key to quantity-based discounts. Set the minimum number of units that must be ordered for this rule to activate. For example, setting Min Qty to 50 means the discount only applies when the customer orders 50 or more units of the product."),

  h3("Validity Period"),
  p("Optionally, set a **Start Date** and **End Date** to restrict this rule to a specific time window. This is ideal for seasonal promotions, festival sales, or limited-time offers."),
  imgPlaceholder("Completed price rule with Discount type, 15%, Min Qty 50, and validity dates"),

  // Step 4
  h2("Step 4: Building Tiered (Progressive) Discount Structures"),
  p("One of the most powerful features of Odoo 19\u2019s pricelist system is the ability to create **tiered discounts** \u2014 progressive discounts that increase with order quantity."),
  p("To set this up, add **multiple price rules** for the same product, each with a different minimum quantity:"),
  spacer(),
  makeTable(
    ["Rule", "Product", "Min Qty", "Discount", "Effect"],
    [
      ["1", "Laptop Stand", "5", "5%", "Orders of 5\u201319 units get 5% off"],
      ["2", "Laptop Stand", "20", "10%", "Orders of 20\u201349 units get 10% off"],
      ["3", "Laptop Stand", "50", "15%", "Orders of 50\u201399 units get 15% off"],
      ["4", "Laptop Stand", "100", "20%", "Orders of 100+ units get 20% off"],
    ],
    [1200, 2000, 1400, 1400, 3360]
  ),
  spacer(),
  p("When a sales order is created with a quantity of 75 units, Odoo evaluates all matching rules and applies the one with the **highest minimum quantity** that the order meets \u2014 in this case, Rule 3 (15% discount)."),
  p("This automated evaluation eliminates the need for salespeople to manually calculate which discount tier applies."),
  imgPlaceholder("Multiple tiered rules in the Price Rules tab for Laptop Stand"),

  // Step 5
  h2("Step 5: Assigning Pricelists to Customers"),
  p("A pricelist is only effective when it is linked to a customer or applied on a sales order."),
  h3("Assigning on the Customer Form"),
  numItem("Navigate to **Sales \u2192 Orders \u2192 Customers**"),
  numItem("Select the customer"),
  numItem("Open the **Sales & Purchase** tab"),
  numItem("In the **Pricelist** field, select the desired pricelist"),
  numItem("Click **Save**"),
  p("Every new quotation created for this customer will automatically use the assigned pricelist. The default pricelist is the **Public Pricelist**."),
  imgPlaceholder("Customer form with pricelist assigned in the Sales & Purchase tab"),
  h3("Changing Pricelist on a Quotation"),
  p("The pricelist can also be changed directly on any individual quotation using the **Pricelist** field at the top of the form. This allows salespeople to apply a different pricelist for a specific order without permanently changing the customer\u2019s default."),

  // Step 6
  h2("Step 6: Verifying the Discount on a Sales Order"),
  p("To verify that the product discount is working correctly:"),
  numItem("Navigate to **Sales \u2192 Orders \u2192 Quotations \u2192 New**"),
  numItem("Select a customer who has the pricelist assigned"),
  numItem("Add the product to the order lines"),
  numItem("Set the quantity to meet the minimum threshold (e.g., 50 units)"),
  p("Odoo automatically evaluates the pricelist rules and adjusts the unit price. If the **Discounts** setting is enabled, the **Disc.%** column displays the discount percentage applied."),
  p("The discounted price flows through the entire sales workflow:"),
  bullet("**Quotation** \u2192 Discount visible to customer on the printed/emailed quote"),
  bullet("**Sales Order** \u2192 Confirmed with discounted pricing"),
  bullet("**Invoice** \u2192 Generated with the same discounted amount"),
  bullet("**Reports** \u2192 Sales analytics reflect actual revenue after discounts"),
  imgPlaceholder("Sales order showing 50 units with 15% discount auto-applied and Disc.% column visible"),

  // Priority Rules
  h2("Priority Rules: How Odoo Resolves Conflicting Pricelist Rules"),
  p("When multiple rules within a pricelist could potentially match the same product, Odoo follows a specific priority hierarchy:"),
  numItem("**Product-specific rules** take precedence over product category rules"),
  numItem("Among matching rules, the rule with the **highest qualifying minimum quantity** is applied"),
  numItem("If two rules have the same priority, the one listed first in the Price Rules tab is used"),
  p("This means you can safely create both category-level discounts (e.g., 5% off all Electronics) and product-level discounts (e.g., 10% off Laptop Stands specifically), and Odoo will always apply the more specific rule."),

  // Discount vs Formula
  h2("Discount vs Formula: Choosing the Right Price Type"),
  spacer(),
  makeTable(
    ["Feature", "Discount", "Formula"],
    [
      ["Discount % visible to customer", "Yes", "No"],
      ["Supports rounding rules (e.g., .99)", "No", "Yes"],
      ["Supports extra fees or margin adjustments", "No", "Yes"],
      ["Can create markups (price increases)", "Yes (negative %)", "Yes (negative %)"],
      ["Best suited for", "B2B pricing with transparency", "Retail pricing with presentation control"],
    ],
    [3120, 3120, 3120]
  ),
  spacer(),
  p("**For B2B businesses** where customers expect to see the discount they are getting, use the **Discount** price type."),
  p("**For B2C or retail businesses** where you want to control the final displayed price with rounding and clean price points, use the **Formula** price type."),

  // Common Mistakes
  h2("Common Configuration Mistakes to Avoid"),
  numItem("**Not enabling the Discounts setting**: The discount percentage will not be visible on the sales order unless the Discounts checkbox is enabled under Sales \u2192 Configuration \u2192 Settings \u2192 Pricing."),
  numItem("**Forgetting to assign the pricelist to customers**: A pricelist that is created but not assigned to any customer will not be used."),
  numItem("**Overlapping validity periods**: If two rules for the same product have overlapping date ranges and different discounts, the first matching rule in the list is applied."),
  numItem("**Using Formula when Discount is sufficient**: If your only requirement is a visible percentage discount, Discount is simpler. Reserve Formula for rounding/extra fees."),
  numItem("**Not testing with the correct quantity**: Quantity-based rules only trigger when the order line quantity meets or exceeds the Min Qty."),

  // Conclusion
  h2("Conclusion"),
  p("Setting up **product discounts in Odoo 19** using pricelists is a structured, reliable process that replaces manual price adjustments with automated, rule-based pricing. From simple percentage discounts to complex tiered structures, Odoo\u2019s pricelist system handles the full spectrum of pricing strategies."),
  p("The key steps are: enable the Pricelists feature, create a pricelist with price rules, assign it to customers, and verify on a sales order. Once configured, the discount applies automatically across quotations, sales orders, and invoices \u2014 ensuring consistency, accuracy, and a professional customer experience."),
  p("For businesses operating in India, this is particularly valuable for managing GST-compliant pricing across multiple customer segments, regions, and product categories."),

  // FAQs
  h2("Frequently Asked Questions"),
  ...faqItem(1, "Can I apply the same discount to an entire product category?", "Yes. When creating a price rule, set the Apply To field to Product Category and select the desired category. The discount will apply to every product within that category when the order line meets the minimum quantity threshold."),
  ...faqItem(2, "What happens if a customer orders less than the minimum quantity?", "The rule does not activate. Odoo only applies the price rule when the order line quantity equals or exceeds the configured Min Qty. The product will be sold at its standard sales price."),
  ...faqItem(3, "Can different customers have different discounts on the same product?", "Yes. Create separate pricelists with different discount rules and assign each pricelist to the respective customer on their contact form under the Sales & Purchase tab."),
  ...faqItem(4, "Can I combine pricelists with loyalty programs or coupon codes?", "Yes. Pricelists handle base pricing, and Odoo\u2019s Discount & Loyalty Programs add promotional rewards on top. You can even link a loyalty program to a specific pricelist so only customers on that pricelist see the promotion."),
  ...faqItem(5, "Is the pricelist discount visible on printed quotations and invoices?", "It depends on the price type. If you use Discount, the discount percentage appears in the Disc.% column on printed quotations and invoices. If you use Formula or Fixed Price, only the adjusted unit price is shown."),

  cta("Infintor Solutions is an Official Odoo Partner in India with offices in Kochi, Qatar, Dubai, and Germany. Looking to implement automated pricing strategies in Odoo 19 for your business? Connect with our Odoo experts for a customized consultation. \u2192 infintor.com/contactus"),
];


// ═══════════════════════════════════════════════════════════════
// SEO BLOG 2: Product Discount Strategies (All 3 Methods)
// ═══════════════════════════════════════════════════════════════
const seoBlog2Sections = [
  // Introduction
  p("Every business offers discounts \u2014 but not every business offers them consistently. A common pain point across SMEs and mid-market companies is the lack of a structured discounting system. Sales teams negotiate discounts verbally, enter them manually into quotations, and there is no centralized policy governing who gets what discount, on which products, and under what conditions. This leads to inconsistent pricing, margin erosion, and customer disputes."),
  p("**Product discount strategies in Odoo 19** address this challenge by providing three distinct, complementary methods for applying discounts \u2014 each designed for a different business scenario. Whether you need a quick manual override during a negotiation, an automated rule that triggers when a customer orders in bulk, or a promotional campaign with coupon codes, Odoo 19 has a dedicated tool for it."),
  p("This guide covers all three discount methods available in Odoo 19, explains when to use each one, and provides step-by-step configuration instructions. It is written for business analysts, ERP managers, and Odoo functional consultants responsible for setting up pricing strategies."),

  // Understanding the Three Methods
  h2("Understanding the Three Discount Methods in Odoo 19"),
  p("Before diving into configuration, it is important to understand the three distinct approaches Odoo 19 offers for product discounts:"),
  spacer(),
  makeTable(
    ["Method", "What It Does", "Best For"],
    [
      ["Manual Line Discounts", "Salesperson enters a discount % directly on the order line", "Quick one-off adjustments during negotiation"],
      ["Pricelists with Price Rules", "Automated rules that apply discounts based on product, category, quantity, or date", "Structured B2B pricing, tiered discounts, customer-specific pricing"],
      ["Discount & Loyalty Programs", "Coupons, promo codes, loyalty points, and buy-X-get-Y offers", "Promotional campaigns, customer retention, eCommerce offers"],
    ],
    [2340, 3510, 3510]
  ),
  spacer(),
  p("Each method operates independently but can be combined. For example, a customer can have a pricelist-based 10% discount and also use a coupon code for an additional 5% off."),

  // Method 1: Manual Discounts
  h2("Method 1: Manual Discounts on Sales Order Lines"),
  p("This is the simplest discount method in Odoo 19 \u2014 ideal for ad-hoc discounts during sales conversations where the salesperson has authority to offer a quick price reduction."),
  h3("Enabling the Feature"),
  numItem("Navigate to **Sales \u2192 Configuration \u2192 Settings**"),
  numItem("Scroll to the **Pricing** section"),
  numItem("Enable the **Discounts** checkbox"),
  numItem("Click **Save**"),
  p("This adds a **Disc.%** column to the Order Lines tab on all sales quotations and orders."),

  h3("Applying Manual Discounts"),
  p("Once the setting is enabled:"),
  numItem("Open a quotation via **Sales \u2192 Orders \u2192 Quotations**"),
  numItem("Add products to the **Order Lines** tab"),
  numItem("In the **Disc.%** column, enter the discount percentage for each line"),
  p("The total is recalculated automatically. Positive values create a discount (price decrease), while negative values create a markup (price increase)."),
  p("**Important behavior**: Positive discounts are visible to the customer on printed quotations and invoices. Negative values (markups) are hidden \u2014 instead, the unit price is silently adjusted upward."),
  imgPlaceholder("Sales order with Disc.% column showing a 10% discount on a product line"),

  h3("Using the Discount Button"),
  p("With the Discounts setting enabled, a **Discount** button appears at the bottom of every sales order. Clicking it opens three options:"),
  spacer(),
  makeTable(
    ["Option", "What It Does"],
    [
      ["On All Order Lines", "Applies the same discount % to every existing line item in the order"],
      ["Global Discount", "Adds a new product line at the bottom with a negative amount representing the total discount"],
      ["Fixed Amount", "Adds a flat monetary discount as a negative-price product line"],
    ],
    [3120, 6240]
  ),
  spacer(),
  p("**Critical limitation**: If you add or remove products **after** applying a Global Discount or Fixed Amount, the discount line does **not** automatically recalculate. You must delete the discount line and re-apply it."),
  imgPlaceholder("Discount button pop-up showing the three options with a 10% Global Discount example"),

  h3("When to Use Manual Discounts"),
  p("Manual discounts are best suited for:"),
  bullet("One-time negotiations where no standard pricing rule applies"),
  bullet("Sales teams with individual discount authority"),
  bullet("Orders where the discount varies by line item based on negotiation"),
  p("They are **not** recommended for repeatable, policy-driven pricing because they depend on the salesperson remembering to apply the correct percentage."),

  // Method 2: Pricelists
  h2("Method 2: Automated Discounts Using Pricelists"),
  p("Pricelists are Odoo 19\u2019s most powerful pricing engine. They automate discount application based on structured rules \u2014 eliminating manual intervention and ensuring consistent pricing across the entire sales team."),

  h3("Enabling Pricelists"),
  numItem("Navigate to **Sales \u2192 Configuration \u2192 Settings**"),
  numItem("In the **Pricing** section, enable the **Pricelists** checkbox"),
  numItem("Click **Save**"),
  numItem("Access pricelists via **Sales \u2192 Products \u2192 Pricelists**"),

  h3("Creating a Pricelist"),
  p("Click **New** on the Pricelists page and configure:"),
  bullet("**Pricelist Name**: Descriptive name (e.g., \"Wholesale \u2014 2026 Q1\")"),
  bullet("**Currency**: The currency for this pricelist"),
  bullet("**Company**: Specific company (for multi-company) or blank for all"),
  bullet("**Country Groups**: Restrict to specific countries if applicable"),

  h3("Configuring Price Rules"),
  p("Under the **Price Rules** tab, click **Add a line** to define a discount rule. The key fields are:"),
  p("**Apply To**: Choose Product, Product Category, All Products, or Product Variant to define the scope."),
  p("**Price Type** \u2014 Three options:"),
  bullet("**Discount**: A visible percentage discount. Entering 15 applies 15% off. The customer sees the discount on quotations and invoices."),
  bullet("**Formula**: A calculated price using discount %, rounding, and extra fees. The customer sees only the adjusted unit price, not the discount breakdown. Use this for retail-friendly pricing like \u20b9999 or \u20b91,499."),
  bullet("**Fixed Price**: A flat price that replaces the product\u2019s sales price entirely."),
  p("**Min Qty**: The minimum order quantity required to trigger this rule. This is the foundation of quantity-based pricing."),
  p("**Validity Period**: Optional start and end dates for seasonal or time-bound discounts."),
  imgPlaceholder("Price rule form with Discount type, 15% off, Min Qty 20, and a validity date range"),

  h3("Building Tiered Discounts"),
  p("Add multiple rules for the same product with escalating thresholds:"),
  spacer(),
  makeTable(
    ["Min Qty", "Discount", "Customer Impact"],
    [
      ["5", "5%", "Small orders get a modest discount"],
      ["20", "10%", "Medium orders get a stronger incentive"],
      ["50", "15%", "Large orders get the best pricing"],
      ["100", "20%", "Bulk buyers get maximum discount"],
    ],
    [2340, 2340, 4680]
  ),
  spacer(),
  p("Odoo evaluates all matching rules and selects the one with the **highest qualifying minimum quantity**. An order of 65 units triggers the 15% rule (Min Qty 50)."),
  p("**Priority rule**: Product-specific rules always take precedence over category-level rules when both could apply."),

  h3("Assigning to Customers"),
  numItem("Navigate to **Sales \u2192 Orders \u2192 Customers** \u2192 select customer"),
  numItem("Open the **Sales & Purchase** tab"),
  numItem("Set the **Pricelist** field to the desired pricelist"),
  numItem("Save"),
  p("The pricelist can also be overridden on any individual quotation without changing the customer\u2019s default."),
  imgPlaceholder("Customer form with pricelist assigned and Sales & Purchase tab visible"),

  h3("When to Use Pricelists"),
  p("Pricelists are best suited for:"),
  bullet("Standardized B2B pricing across customer segments"),
  bullet("Volume-based (quantity) discounts for wholesale or distribution"),
  bullet("Customer-specific pricing that should apply automatically on every order"),
  bullet("Time-bound promotions with defined start and end dates"),
  bullet("Retail pricing with rounding and clean price points (using Formula)"),

  // Method 3: Loyalty Programs
  h2("Method 3: Discount and Loyalty Programs"),
  p("For promotional campaigns, customer retention strategies, and eCommerce offers, Odoo 19 provides a dedicated **Discount & Loyalty Programs** module. This goes beyond standard pricing into coupon codes, loyalty points, and conditional promotions."),

  h3("Enabling the Feature"),
  numItem("Navigate to **Sales \u2192 Configuration \u2192 Settings**"),
  numItem("Under **Pricing**, enable **Discounts, Loyalty & Gift Card**"),
  numItem("Click **Save**"),
  numItem("Access programs via **Sales \u2192 Products \u2192 Discount & Loyalty**"),

  h3("Program Types"),
  p("Odoo 19 offers six program types, each designed for a specific promotional scenario:"),
  spacer(),
  makeTable(
    ["Program Type", "How It Works", "Example"],
    [
      ["Coupons", "Generate single-use codes that grant immediate discount", "\"Use code WELCOME15 for 15% off\""],
      ["Loyalty Cards", "Customers earn points on purchases, redeemable for rewards", "\"Earn 1 point per \u20b9100 spent, redeem 10 points for \u20b9200 off\""],
      ["Promotions", "Auto-applied discount when order meets conditions", "\"Get free shipping on orders above \u20b92,000\""],
      ["Discount Code", "Customer enters a code at checkout for a discount", "\"Use SAVE20 for 20% off all electronics\""],
      ["Buy X Get Y", "Buy a specified quantity, earn credits toward a reward item", "\"Buy 3 shirts, get 1 free\""],
      ["Next Order Coupons", "Coupon valid only on the customer\u2019s next order", "\"Here\u2019s 10% off your next purchase\""],
    ],
    [2340, 3510, 3510]
  ),
  spacer(),

  h3("Configuring Conditional Rules"),
  p("Under the **Rules & Rewards** tab, click **Add** next to Conditional rules to set when the program activates:"),
  bullet("**Minimum Quantity**: Number of products that must be purchased"),
  bullet("**Minimum Purchase**: Order total that must be reached (tax included or excluded)"),
  bullet("**Products**: Restrict to specific products (leave blank for all)"),
  bullet("**Categories**: Restrict to a product category"),
  bullet("**Product Tag**: Apply to products with a specific tag"),

  h3("Key Program Settings"),
  spacer(),
  makeTable(
    ["Setting", "Purpose"],
    [
      ["Start / End Date", "Validity period for the program"],
      ["Limit Usage", "Maximum number of times the program can be used"],
      ["Available On", "Sales, eCommerce, Point of Sale, or all channels"],
      ["Pricelist", "Link to specific pricelist(s) \u2014 only customers on that pricelist see the program"],
      ["Company", "Restrict to a specific company in multi-company setups"],
    ],
    [3120, 6240]
  ),
  spacer(),
  imgPlaceholder("Loyalty program configuration with conditional rules and rewards defined"),

  h3("When to Use Loyalty Programs"),
  p("Loyalty and discount programs are best suited for:"),
  bullet("eCommerce promotional campaigns with coupon codes"),
  bullet("Customer retention strategies using loyalty points"),
  bullet("Cross-sell and upsell promotions (buy X get Y)"),
  bullet("Seasonal or event-based offers with limited usage"),
  bullet("Programs that need to work across Sales, PoS, and eCommerce simultaneously"),

  // Decision Table
  h2("Choosing the Right Discount Method"),
  spacer(),
  makeTable(
    ["Business Scenario", "Recommended Method", "Why"],
    [
      ["Salesperson offers 5% off during a call", "Manual Discount", "Quick, flexible, no pre-configuration needed"],
      ["All wholesale customers get 15% off automatically", "Pricelist (Discount)", "Automated, consistent, assigned to customer"],
      ["Buy 50+ units, get 10% off", "Pricelist (Tiered Rules)", "Quantity-based automation with Min Qty thresholds"],
      ["Flat \u20b9999 promotional price on select items", "Pricelist (Fixed Price)", "Overrides sales price for a specific period"],
      ["Retail pricing ending in .99", "Pricelist (Formula)", "Rounding and extra fee control"],
      ["\"Enter code SAVE20 at checkout\"", "Discount Code Program", "Customer-driven activation via code entry"],
      ["Earn points, redeem for rewards", "Loyalty Cards Program", "Long-term customer retention"],
      ["Buy 3, Get 1 Free", "Buy X Get Y Program", "Volume incentive with reward item"],
      ["10% off on orders above \u20b95,000 (auto-applied)", "Promotion Program", "Condition-based, no code needed"],
    ],
    [3120, 3120, 3120]
  ),
  spacer(),
  p("Most businesses use a **combination** of methods. For example, a distributor might use pricelists for base B2B pricing and add a seasonal promotion using a Discount Code program."),

  // Common Mistakes
  h2("Common Mistakes to Avoid"),
  numItem("**Not enabling the correct setting**: Each method (Discounts, Pricelists, Loyalty Programs) has its own toggle under Sales \u2192 Configuration \u2192 Settings. Enable the one you need \u2014 they are independent of each other."),
  numItem("**Creating a pricelist without assigning it**: A pricelist that is not assigned to any customer will not be used. The default Public Pricelist applies instead."),
  numItem("**Adding products after Global Discount**: The Global Discount line does not auto-update when order lines change. Delete and re-apply the discount after modifications."),
  numItem("**Confusing Discount and Formula price types**: Use Discount for transparent B2B pricing. Use Formula only when you need rounding, extra fees, or want to hide the discount percentage from the customer."),
  numItem("**Not testing at the right quantity**: Quantity-based pricelist rules require the order line quantity to meet or exceed the Min Qty. Always test with the exact threshold quantities."),

  // Conclusion
  h2("Conclusion"),
  p("Odoo 19 provides a complete toolkit for implementing **product discount strategies** across any business model. Manual discounts offer flexibility for one-off negotiations, pricelists deliver automated rule-based pricing for consistent B2B operations, and loyalty programs power promotional campaigns across all sales channels."),
  p("The key to success is choosing the right method for each pricing scenario and configuring it correctly from the start. With proper setup, your pricing runs on autopilot \u2014 accurate, consistent, and scalable across your entire sales organization."),
  p("For Indian businesses handling GST-compliant pricing across multiple states, customer segments, and product lines, Odoo 19\u2019s pricelist system is particularly valuable as it ensures the correct discount is applied before tax computation, maintaining compliance throughout the invoicing process."),

  // FAQs
  h2("Frequently Asked Questions"),
  ...faqItem(1, "Can I combine pricelists with loyalty programs on the same order?", "Yes. Pricelists handle the base pricing (e.g., 10% off for wholesale customers), and loyalty programs add additional rewards on top (e.g., a coupon code for \u20b9500 off). Both can be active on the same sales order. You can even link a loyalty program to a specific pricelist so only customers on that pricelist see the promotion."),
  ...faqItem(2, "Is the discount visible to customers on printed quotations?", "It depends on the method. Manual line discounts (Disc.%) are always visible. Pricelist discounts using the Discount price type are visible as a Disc.% column. Pricelist discounts using Formula or Fixed Price types show only the adjusted unit price. Loyalty program rewards appear as separate reward lines on the order."),
  ...faqItem(3, "Can I restrict a discount to a specific time period?", "Yes. Pricelist price rules have a Validity Period field where you can set start and end dates. Loyalty and discount programs also have Start Date and End Date fields. Manual discounts do not have time restrictions \u2014 they apply whenever the salesperson enters them."),
  ...faqItem(4, "What is the difference between a Global Discount and a line-level discount?", "A line-level discount applies a percentage directly to each individual product line. A Global Discount (accessed via the Discount button) adds a new line at the bottom of the order with a negative amount that represents the cumulative discount across all lines."),
  ...faqItem(5, "Can I use product discounts in Odoo 19 for eCommerce and Point of Sale?", "Yes. Pricelists work across Sales, eCommerce, and Point of Sale. Discount and Loyalty Programs can be configured to be available on specific channels using the Available On field. Manual line discounts are specific to the Sales app and quotation/order forms."),

  cta("Infintor Solutions is an Official Odoo Partner in India specializing in end-to-end Odoo ERP implementation. Need help setting up discount strategies for your business? Contact our Odoo consultants for a free initial assessment. \u2192 infintor.com/contactus"),
];


// ═══════════════════════════════════════════
// Generate both DOCX files
// ═══════════════════════════════════════════
const OUT_DIR = "My learnings/Rohan_Documentation";

async function main() {
  const blogs = [
    {
      title: "How to Set Up Product Discounts in Odoo 19 Using Pricelists",
      file: `${OUT_DIR}/BLOG_SEO_Product_Discounts_Pricelist_Odoo_19.docx`,
      sections: seoBlog1Sections,
    },
    {
      title: "Product Discount Strategies in Odoo 19: A Complete Configuration Guide",
      file: `${OUT_DIR}/BLOG_SEO_Product_Discount_Strategies_Odoo_19.docx`,
      sections: seoBlog2Sections,
    },
  ];

  for (const blog of blogs) {
    const doc = makeDoc(blog.title, "Rohan Raj  |  Infintor Solutions", "Mar 9, 2026", blog.sections);
    const buf = await Packer.toBuffer(doc);
    fs.writeFileSync(blog.file, buf);
    console.log(`Created: ${blog.file}  (${(buf.length / 1024).toFixed(0)} KB)`);
  }
}

main().catch(err => { console.error(err); process.exit(1); });
