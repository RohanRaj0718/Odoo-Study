const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, LevelFormat
} = require("docx");

// ─── Shared style config (matches infintor.com blog CSS) ───
const FONT = "Poppins";
const PAGE_WIDTH = 12240;
const MARGINS = { top: 1440, right: 1440, bottom: 1440, left: 1440 };
const TITLE_COLOR = "000000";
const HEADING_COLOR = "000000";
const BODY_COLOR = "000000";
const AUTHOR_COLOR = "000000";
const ACCENT_BG = "F2F2F2";     // CTA background — light gray

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const tblBorder = { style: BorderStyle.SINGLE, size: 1, color: "000000" };
const tblBorders = { top: tblBorder, bottom: tblBorder, left: tblBorder, right: tblBorder };

function makeDoc(title, author, date, sections) {
  return new Document({
    styles: {
      default: { document: { run: { font: FONT, size: 25, color: BODY_COLOR } } },
      paragraphStyles: [
        {
          id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 58, font: FONT, color: TITLE_COLOR },
          paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 }
        },
        {
          id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 48, font: FONT, color: HEADING_COLOR },
          paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 }
        },
        {
          id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 30, font: FONT, color: HEADING_COLOR },
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
          children: [new TextRun({ text: title, size: 58, font: FONT, color: TITLE_COLOR })]
        }),
        new Paragraph({
          spacing: { after: 400 },
          children: [new TextRun({ text: `${author}  |  ${date}`, size: 22, font: FONT, color: AUTHOR_COLOR })]
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
      runs.push(new TextRun({ text: part.slice(2, -2), bold: true, font: FONT, size: 25, color: BODY_COLOR }));
    } else {
      runs.push(new TextRun({ text: part, font: FONT, size: 25, color: BODY_COLOR }));
    }
  }
  return new Paragraph({ spacing: { after: 160 }, children: runs });
}

function bullet(text) {
  const runs = [];
  const parts = text.split(/(\*\*[^*]+\*\*)/);
  for (const part of parts) {
    if (part.startsWith("**") && part.endsWith("**")) {
      runs.push(new TextRun({ text: part.slice(2, -2), bold: true, font: FONT, size: 25, color: HEADING_COLOR }));
    } else {
      runs.push(new TextRun({ text: part, font: FONT, size: 25, color: HEADING_COLOR }));
    }
  }
  return new Paragraph({ numbering: { reference: "bullets", level: 0 }, spacing: { after: 80 }, children: runs });
}

function imgPlaceholder(desc) {
  return new Paragraph({
    spacing: { before: 120, after: 200 },
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: `[Image: ${desc}]`, font: FONT, size: 20, color: "999999", italics: true })]
  });
}

function makeTable(headers, rows, colWidths) {
  const headerCells = headers.map((h, i) => new TableCell({
    borders: tblBorders,
    width: { size: colWidths[i], type: WidthType.DXA },
    shading: { fill: HEADING_COLOR, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, font: FONT, size: 22, color: "FFFFFF" })] })]
  }));
  const dataRows = rows.map(row => new TableRow({
    children: row.map((cell, i) => new TableCell({
      borders: tblBorders,
      width: { size: colWidths[i], type: WidthType.DXA },
      margins: { top: 60, bottom: 60, left: 120, right: 120 },
      children: [new Paragraph({ children: [new TextRun({ text: cell, font: FONT, size: 22, color: HEADING_COLOR })] })]
    }))
  }));
  return new Table({
    width: { size: colWidths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
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
      children: [new TextRun({ text: `${num}. ${question}`, bold: true, font: FONT, size: 25, color: HEADING_COLOR })]
    }),
    p(answer)
  ];
}

function cta(text) {
  return new Paragraph({
    spacing: { before: 300, after: 200 },
    shading: { fill: ACCENT_BG, type: ShadingType.CLEAR },
    children: [new TextRun({ text, font: FONT, size: 25, italics: true, color: TITLE_COLOR })]
  });
}

// ═══════════════════════════════════════════════════════════════
// SEO BLOG 1: Product Discounts Using Pricelists
// ═══════════════════════════════════════════════════════════════
const seoBlog1Sections = [
  p("To set up product discounts in Odoo 19, we use the **Pricelists** option available under the Sales module. Pricelists let businesses define structured discount rules that apply automatically on sales orders \u2014 eliminating manual price adjustments and ensuring consistent pricing. This guide walks through the complete setup of **product discounts in Odoo 19**, from enabling the Pricelists feature to verifying the discount on a live quotation."),

  h2("Enabling Pricelists and Discounts"),
  p("Go to **Sales \u2192 Configuration \u2192 Settings** and scroll to the **Pricing** section."),
  p("Enable the **Pricelists** checkbox \u2014 described as \u201cSet multiple prices per product, automated discounts, etc.\u201d This unlocks the menu at **Sales \u2192 Products \u2192 Pricelists**. Also enable the **Discounts** checkbox \u2014 described as \u201cGrant discounts on sales order lines.\u201d This adds a **Disc.%** column to sales order lines."),
  p("Click **Save**."),
  imgPlaceholder("Pricelists and Discounts checkboxes enabled under Pricing in Sales Settings"),

  h2("Creating a Pricelist"),
  p("Go to **Sales \u2192 Products \u2192 Pricelists \u2192 New**."),
  p("Enter a descriptive name in the title field at the top (placeholder hint: e.g. USD Retailers). Then configure:"),
  bullet("**Company**: Assign to a specific company in multi-company setups, or leave blank for all"),
  bullet("**Country Groups**: Restrict to specific regions if needed"),
  p("The currency is set automatically based on your company\u2019s default currency and shown in the breadcrumb (e.g., \u201cNew (INR)\u201d). The pricelist form has a **Rules** tab where you define pricing rules."),
  imgPlaceholder("New pricelist form with name and currency configured"),

  h2("Configuring a Price Rule"),
  p("In the **Rules** tab, click **Add a line**. Odoo opens a dialog titled \u201cCreate Pricelist Rules\u201d with the following fields:"),
  p("**Apply To**: Click Product to target a specific item, or Category to apply the rule to an entire product category. By default (when neither is clicked), the rule applies to all products."),
  p("**Price Type**: Select one of three options:"),
  spacer(),
  makeTable(
    ["Price Type", "How It Works", "Discount Visible on Quotation?"],
    [
      ["Discount", "Applies a percentage off the product\u2019s sales price", "Yes \u2014 shown in the Disc.% column"],
      ["Formula", "Calculates price using discount %, rounding, and extra fee", "No \u2014 only the adjusted unit price is shown"],
      ["Fixed Price", "Sets a flat price regardless of the sales price", "No \u2014 the fixed price replaces the unit price"],
    ],
    [2340, 4680, 2340]
  ),
  spacer(),
  p("**Discount**: When Discount is selected as the price type, enter the percentage (e.g., 10 for 10% off)."),
  p("**Min Qty**: The minimum quantity the customer must order for this rule to activate."),
  p("**Validity**: Optionally set start and end dates for seasonal or time-bound discounts."),
  p("A note at the bottom of the dialog reads: \u201cFor formula or fixed pricing, the original price isn\u2019t shown in sale orders.\u201d"),
  p("Click **Save & Close** to save the rule."),
  imgPlaceholder("Price rule dialog showing Discount type, 10%, Min Qty 2 for a product"),

  h2("Building Tiered Discounts"),
  p("Add **multiple rules** for the same product with increasing quantities to create progressive discounts:"),
  spacer(),
  makeTable(
    ["Min Qty", "Discount", "Effect"],
    [
      ["2", "10%", "Buy 2+, get 10% off"],
      ["5", "15%", "Buy 5+, get 15% off"],
      ["10", "20%", "Buy 10+, get 20% off"],
    ],
    [2340, 2340, 4680]
  ),
  spacer(),
  p("Odoo automatically picks the **highest qualifying rule**. An order of 7 units triggers the 15% discount (Min Qty 5), not the 10% one."),
  imgPlaceholder("Three tiered rules in the Rules tab for the same product"),

  h2("Assigning the Pricelist to a Customer"),
  p("Go to **Sales \u2192 Orders \u2192 Customers** and select the customer."),
  p("Open the **Sales & Purchase** tab and set the **Pricelist** field to the desired pricelist. Save the form. Every new quotation for this customer now uses this pricelist automatically."),
  p("You can also change the pricelist directly on any individual quotation using the **Pricelist** field on the form \u2014 without changing the customer\u2019s default."),
  imgPlaceholder("Customer form with pricelist assigned on the Sales & Purchase tab"),

  h2("Verifying the Discount on a Sales Order"),
  p("Go to **Sales \u2192 Orders \u2192 Quotations \u2192 New**."),
  p("Select a customer who has the pricelist assigned, add the product, and set the quantity to meet the minimum threshold. Odoo evaluates the rules and applies the discount automatically. The **Disc.%** column on the order line shows the percentage applied."),
  p("The discounted price carries through to the confirmed sales order, the invoice, and sales reports \u2014 no manual adjustment needed."),
  imgPlaceholder("Sales order with Disc.% column showing the discount auto-applied"),

  h2("Discount vs Formula"),
  spacer(),
  makeTable(
    ["Feature", "Discount", "Formula"],
    [
      ["Discount % visible to customer", "Yes", "No"],
      ["Supports rounding (Round off to field)", "No", "Yes"],
      ["Supports extra fee / margin adjustment", "No", "Yes"],
      ["Best for", "B2B pricing with transparency", "Retail pricing with presentation control"],
    ],
    [3120, 3120, 3120]
  ),
  spacer(),
  p("Use **Discount** when customers should see the percentage they\u2019re saving. Use **Formula** when you want to control the final displayed price with rounding or surcharges."),

  h2("FAQ\u2019s"),
  ...faqItem(1, "Can I apply a discount to an entire product category?", "Yes. In the price rule dialog, set Apply To to Product Category and select the category. The discount applies to every product in that category when the minimum quantity is met."),
  ...faqItem(2, "What happens if a customer orders less than the minimum quantity?", "The rule does not activate. The product is sold at its standard sales price. Odoo only triggers the rule when the order line quantity meets or exceeds the configured Min Qty."),
  ...faqItem(3, "Can different customers get different discounts?", "Yes. Create separate pricelists with different rules and assign each to the respective customer on their contact form under the Sales & Purchase tab."),

  cta("Looking to automate product discounts in Odoo 19 for your business? Connect with the experts at Infintor for a customized consultation. \u2192 infintor.com/contactus"),
];


// ═══════════════════════════════════════════════════════════════
// SEO BLOG 2: 3 Ways to Apply Product Discounts
// ═══════════════════════════════════════════════════════════════
const seoBlog2Sections = [
  p("Odoo 19 offers three distinct methods for applying discounts on sales orders \u2014 each suited to a different business scenario. This guide covers manual discounts, pricelists, and promotions so you can choose the right approach for your pricing needs."),

  // Method 1
  h2("Method 1: Manual Line Discounts"),
  p("This is the simplest option \u2014 the salesperson types a discount directly on the order line."),
  h3("Setup"),
  p("Go to **Sales \u2192 Configuration \u2192 Settings \u2192 Pricing** and enable the **Discounts** checkbox (\u201cGrant discounts on sales order lines\u201d). Click **Save**."),
  p("This adds a **Disc.%** column to every quotation and sales order."),
  h3("How to Apply"),
  p("Go to **Sales \u2192 Orders \u2192 Quotations \u2192 New**. Add products, then enter the discount percentage in the **Disc.%** column for each line. The total recalculates automatically."),
  imgPlaceholder("Order line showing Disc.% column with 10% entered"),

  h3("The Discount Button"),
  p("A **Discount** button also appears at the bottom of the sales order. Clicking it opens a dialog with three options:"),
  spacer(),
  makeTable(
    ["Option", "What It Does"],
    [
      ["On All Order Lines", "Applies the same % to every line"],
      ["Global Discount", "Adds a negative-amount line representing the total discount"],
      ["Fixed Amount", "Adds a flat monetary deduction as a new line"],
    ],
    [3120, 6240]
  ),
  spacer(),
  p("**Note**: If you add or remove products after applying a Global Discount or Fixed Amount, the discount line does **not** recalculate automatically \u2014 delete it and re-apply."),
  p("**Best for**: One-off negotiations where no standard pricing rule exists."),

  // Method 2
  h2("Method 2: Automated Discounts with Pricelists"),
  p("Pricelists apply discounts automatically based on rules \u2014 no manual entry needed."),
  h3("Setup"),
  p("Go to **Sales \u2192 Configuration \u2192 Settings \u2192 Pricing** and enable the **Pricelists** checkbox (\u201cSet multiple prices per product, automated discounts, etc.\u201d). Click **Save**."),
  h3("Creating a Pricelist"),
  p("Go to **Sales \u2192 Products \u2192 Pricelists \u2192 New**. Enter a descriptive name, and optionally restrict by company or country group. The currency is set automatically based on your company."),
  h3("Adding Price Rules"),
  p("In the **Rules** tab, click **Add a line**. The dialog has these key fields:"),
  bullet("**Apply To**: Click Product to target a specific item, or Category for a product group (defaults to all products when neither is selected)"),
  bullet("**Price Type**: Discount (visible %), Formula (calculated price with rounding), or Fixed Price (flat override)"),
  bullet("**Min Qty**: Minimum quantity to trigger the rule"),
  bullet("**Validity**: Optional date range"),
  p("For **tiered quantity discounts**, add multiple rules for the same product:"),
  spacer(),
  makeTable(
    ["Min Qty", "Discount", "Effect"],
    [
      ["2", "10%", "Small orders"],
      ["5", "15%", "Medium orders"],
      ["10", "20%", "Bulk orders"],
    ],
    [2340, 2340, 4680]
  ),
  spacer(),
  p("Odoo picks the highest qualifying rule. An order of 7 units gets 15% (Min Qty 5)."),
  h3("Assigning to Customers"),
  p("Go to **Sales \u2192 Orders \u2192 Customers**, open the customer, go to the **Sales & Purchase** tab, and set the **Pricelist** field. Every new quotation for this customer uses the assigned pricelist automatically."),
  p("**Best for**: Standardized B2B pricing, wholesale tiers, and customer-specific automated discounts."),

  // Method 3
  h2("Method 3: Promotions & Loyalty Programs"),
  p("For coupon codes, loyalty rewards, and conditional offers, Odoo 19 provides a dedicated promotions engine."),
  h3("Setup"),
  p("Go to **Sales \u2192 Configuration \u2192 Settings \u2192 Pricing** and enable **Promotions, Loyalty & Gift Card** (\u201cManage Promotions, Coupons, Loyalty cards, Gift cards & eWallet\u201d). Click **Save**."),
  p("This unlocks **Sales \u2192 Products \u2192 Discount & Loyalty** where you can create programs."),
  h3("Program Types"),
  spacer(),
  makeTable(
    ["Type", "Example"],
    [
      ["Coupons", "Single-use code: \u201cWELCOME15 for 15% off\u201d"],
      ["Loyalty Cards", "Earn points per purchase, redeem for rewards"],
      ["Promotions", "Auto-applied: \u201cFree shipping on orders above \u20b92,000\u201d"],
      ["Discount Code", "Customer enters code at checkout"],
      ["Buy X Get Y", "\u201cBuy 3 shirts, get 1 free\u201d"],
      ["Next Order Coupons", "\u201c10% off your next purchase\u201d"],
    ],
    [3120, 6240]
  ),
  spacer(),
  p("Each program has conditional rules (minimum quantity, minimum purchase amount, specific products or categories) and rewards (percentage discount, fixed amount, free product, or free shipping)."),
  p("**Best for**: eCommerce campaigns, customer retention, and time-limited promotional offers."),

  // Comparison
  h2("Which Method Should You Use?"),
  spacer(),
  makeTable(
    ["Scenario", "Method"],
    [
      ["Quick 5% off during a sales call", "Manual Discount"],
      ["All wholesale customers get 15% off", "Pricelist (Discount)"],
      ["Buy 50+ units, get 10% off", "Pricelist (Tiered Rules)"],
      ["\u201cUse code SAVE20 at checkout\u201d", "Discount Code Program"],
      ["Earn loyalty points on every order", "Loyalty Cards Program"],
    ],
    [4680, 4680]
  ),
  spacer(),
  p("These methods work independently and can be **combined** on the same order. A customer can have a pricelist-based discount and also apply a coupon code \u2014 both stack."),

  // FAQs
  h2("FAQ\u2019s"),
  ...faqItem(1, "Is the discount visible to customers on printed quotations?", "Manual Disc.% and pricelist Discount-type rules show the discount in the Disc.% column. Formula and Fixed Price rules show only the adjusted unit price. Loyalty rewards appear as separate reward lines."),
  ...faqItem(2, "Can I restrict a discount to a specific time period?", "Yes. Pricelist rules have a Validity field for start and end dates. Promotions and loyalty programs also have date fields. Manual discounts have no time restriction."),
  ...faqItem(3, "Can I use the same discount across Sales, eCommerce, and Point of Sale?", "Pricelists work across all channels. Promotions and loyalty programs have an \u201cAvailable On\u201d field to select specific channels. Manual Disc.% discounts are only available on sales order forms."),

  cta("Want to implement product discount strategies in Odoo 19 the right way? Talk to the Odoo experts at Infintor for a tailored setup. \u2192 infintor.com/contactus"),
];


// ═══════════════════════════════════════════
// Generate both DOCX files
// ═══════════════════════════════════════════
const OUT_DIR = "My learnings/Rohan_Documentation";

async function main() {
  const blogs = [
    {
      title: "How to Set Up Product Discounts in Odoo 19",
      file: `${OUT_DIR}/BLOG_SEO_Product_Discounts_Odoo_19_v3.docx`,
      sections: seoBlog1Sections,
    },
    {
      title: "3 Ways to Apply Product Discounts in Odoo 19",
      file: `${OUT_DIR}/BLOG_SEO_3_Discount_Methods_Odoo_19_v4.docx`,
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
