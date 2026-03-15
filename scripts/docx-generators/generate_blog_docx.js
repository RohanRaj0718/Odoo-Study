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
const CONTENT_WIDTH = PAGE_WIDTH - MARGINS.left - MARGINS.right; // 9360
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
        // Title
        new Paragraph({
          spacing: { after: 80 },
          children: [new TextRun({ text: title, bold: true, size: 36, font: FONT, color: BRAND_COLOR })]
        }),
        // Author + Date
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

function p(text, opts = {}) {
  const runs = [];
  // Simple bold support: **text**
  const parts = text.split(/(\*\*[^*]+\*\*)/);
  for (const part of parts) {
    if (part.startsWith("**") && part.endsWith("**")) {
      runs.push(new TextRun({ text: part.slice(2, -2), bold: true, font: FONT, size: 22 }));
    } else {
      runs.push(new TextRun({ text: part, font: FONT, size: 22, ...opts }));
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

// ═══════════════════════════════════════════
// BLOG V1
// ═══════════════════════════════════════════
const v1Sections = [
  p("Offering discounts based on order quantity is a common pricing strategy that encourages bulk purchases and increases order value. In Odoo 19, this can be fully automated using **Pricelists** with price rules — once configured, the correct discount is applied automatically whenever a customer meets the minimum quantity threshold on a sales order."),

  h2("Enabling Pricelists"),
  nav("Go to Sales App → Configuration → Settings → Pricing section"),
  p("Enable the **Pricelists** checkbox and click **Save**."),
  p("Once saved, pricelists can be accessed from Sales App → Products → Pricelists."),
  imgPlaceholder("Pricelist setting enabled in Sales configuration"),

  h2("Creating a Pricelist with Quantity-Based Rules"),
  nav("Go to Sales App → Products → Pricelists → New"),
  p("Enter a name for the pricelist (e.g., \"Bulk Purchase Discount\"). Under the **Rules** tab, click **Add a line** to create a new rule."),
  p("Configure the rule as follows:"),
  bullet("**Apply On**: Select Product or Category depending on whether the discount applies to a specific product or an entire product category"),
  bullet("**Price Type**: Select Discount to show the discount percentage to the customer, or Formula to apply it without displaying the percentage"),
  bullet("**Discount**: Enter the discount percentage (e.g., 10)"),
  bullet("**Min Qty**: Set the minimum quantity required to trigger this discount (e.g., 50)"),
  bullet("**Start Date / End Date**: Optionally set a date range for the rule"),
  imgPlaceholder("Price rule configured with 10% discount for minimum 50 units"),
  p("To create progressive (tiered) discounts, add multiple lines for the same product with different minimum quantities:"),
  spacer(),
  makeTable(["Min Qty", "Discount"], [["10", "5%"], ["50", "10%"], ["100", "15%"]], [4680, 4680]),
  spacer(),
  p("Odoo automatically applies the highest applicable discount based on the quantity entered in the sales order."),
  imgPlaceholder("Multiple price rules showing tiered discount structure"),

  h2("Assigning the Pricelist to a Customer"),
  nav("Go to Sales App → Orders → Customers → Select the customer"),
  p("Under the **Sales & Purchase** tab, set the **Pricelist** field to the newly created pricelist (e.g., \"Bulk Purchase Discount\") and save."),
  p("Every future quotation for this customer will automatically use this pricelist."),
  imgPlaceholder("Pricelist field on customer form"),

  h2("Verifying the Discount on a Sales Order"),
  nav("Go to Sales App → Orders → Quotations → New"),
  p("Select the customer with the assigned pricelist. Add a product and set the quantity to meet the minimum threshold (e.g., 50 units). Odoo automatically applies the configured discount."),
  p("If the **Discounts** setting is enabled (Sales → Configuration → Settings → Pricing → Discounts), the discount percentage appears in the **Discount (%)** column on the order line, giving the customer full visibility."),
  imgPlaceholder("Sales order showing auto-applied discount on order line"),
  p("Quantity-based discounts through pricelists eliminate the need for manual price adjustments, ensure consistent pricing across the sales team, and give customers a clear incentive to order in larger volumes."),

  h2("Discount vs Formula — Which Price Type to Use?"),
  spacer(),
  makeTable(
    ["Feature", "Discount", "Formula"],
    [
      ["Discount visible to customer", "Yes", "No"],
      ["Supports rounding rules", "No", "Yes"],
      ["Supports extra fees/margins", "No", "Yes"],
      ["Best for", "Transparent B2B pricing", "Retail or computed pricing"],
    ],
    [3120, 3120, 3120]
  ),
  spacer(),

  h2("FAQ's"),
  ...faqItem(1, "Can I apply quantity-based discounts to an entire product category?", "Yes. When creating a price rule, select Category in the Apply On field instead of Product. The discount will apply to all products within that category."),
  ...faqItem(2, "What happens if a customer orders less than the minimum quantity?", "The discount is not applied. Odoo only triggers the price rule when the order line quantity meets or exceeds the configured minimum."),
  ...faqItem(3, "Can I have different pricelists for different customers?", "Yes. Each customer can have a unique pricelist assigned on their contact form under the Sales & Purchase tab. If no pricelist is assigned, the default Public Pricelist is applied."),

  cta("Looking to automate your pricing strategy in Odoo 19? Connect with the experts at Infintor for a customized consultation. → infintor.com"),
];

// ═══════════════════════════════════════════
// BLOG V2
// ═══════════════════════════════════════════
const v2Sections = [
  p("Businesses that sell in bulk often offer tiered discounts — the more a customer orders, the better the price. In Odoo 19, the **Pricelist** feature automates this entirely, applying the right discount the moment a quantity threshold is met on a sales order."),

  h2("Enabling the Pricelist Feature"),
  nav("Go to Sales App → Configuration → Settings"),
  p("Under the **Pricing** section, enable **Pricelists** and click **Save**."),
  imgPlaceholder("Pricelists checkbox enabled in Sales settings"),

  h2("Setting Up Quantity-Based Discount Rules"),
  nav("Go to Sales App → Products → Pricelists → New"),
  p("Name the pricelist (e.g., \"Volume Discount\"). Navigate to the **Rules** tab and click **Add a line**."),
  p("In the rule form, configure the following:"),
  bullet("**Apply On**: Choose Product to target a specific item, or Category to cover an entire product group"),
  bullet("**Price Type**: Choose Discount (percentage shown to customer) or Formula (discount applied but hidden from customer)"),
  bullet("**Discount**: Enter the percentage (e.g., 10 for 10% off)"),
  bullet("**Min Qty**: Enter the quantity threshold that triggers this rule (e.g., 25 units)"),
  imgPlaceholder("Price rule form with discount and minimum quantity configured"),

  h3("Creating Tiered Discounts"),
  p("Add multiple rules for the same product with increasing quantities and discounts:"),
  spacer(),
  makeTable(
    ["Min Qty", "Discount", "Resulting Price (if Sales Price = ₹1,000)"],
    [["10", "5%", "₹950"], ["50", "10%", "₹900"], ["100", "20%", "₹800"]],
    [2000, 2000, 5360]
  ),
  spacer(),
  p("When a customer orders 60 units, Odoo automatically picks the 10% rule (Min Qty 50) since it is the highest threshold met."),
  imgPlaceholder("Three price rules showing tiered discount levels"),

  h2("Applying the Pricelist to Customers"),
  p("There are two ways to apply a pricelist:"),
  p("**Option 1 — Assign to a customer permanently:**"),
  nav("Go to Sales App → Orders → Customers → Select customer → Sales & Purchase tab → Set the Pricelist field"),
  p("All future quotations for this customer will use this pricelist by default."),
  p("**Option 2 — Apply on a specific quotation:**"),
  nav("Go to Sales App → Orders → Quotations → New or select an existing quotation"),
  p("Change the **Pricelist** field directly on the quotation. This overrides the customer's default pricelist for that order only."),
  imgPlaceholder("Pricelist field on quotation form"),

  h2("Testing the Discount"),
  p("Create a new quotation for a customer with the assigned pricelist. Add the product and enter a quantity that meets a threshold (e.g., 50 units)."),
  p("Odoo auto-applies the matching discount. If the **Discounts** setting is also enabled (Sales → Configuration → Settings → Pricing → Discounts), the **Discount (%)** column appears on the order line, making the discount transparent to the customer."),
  imgPlaceholder("Quotation with auto-applied 10% discount visible in Disc.% column"),
  p("Configuring quantity-based discounts through pricelists removes manual effort, guarantees pricing consistency, and encourages customers to place larger orders — all without any custom development."),

  h2("FAQ's"),
  ...faqItem(1, "What is the difference between Discount and Formula price types?", "The Discount type shows the discount percentage directly to the customer on the quotation. The Formula type applies the price reduction without displaying it — useful when you want to adjust pricing discreetly."),
  ...faqItem(2, "Can I set a validity period for a discount rule?", "Yes. Each price rule has a Start Date and End Date field where you can define the period. The rule will only apply to quotations created within that range."),
  ...faqItem(3, "Will the discount apply if I don't assign the pricelist to the customer?", "No. The pricelist must either be assigned to the customer's contact form or manually selected on the quotation. Without it, Odoo uses the default Public Pricelist."),

  cta("Looking to automate your pricing and discount strategy in Odoo 19? Connect with the experts at Infintor for a customized consultation. → infintor.com"),
];

// ═══════════════════════════════════════════
// BLOG V3
// ═══════════════════════════════════════════
const v3Sections = [
  p("When customers buy more, they expect better pricing. Manually adjusting prices on every large order is error-prone and inconsistent. Odoo 19 solves this with **Pricelists** — define your discount rules once, and the system applies them automatically on every qualifying sales order."),

  h2("Activating Pricelists"),
  nav("Go to Sales App → Configuration → Settings → Pricing"),
  p("Enable **Pricelists**, then click **Save**."),
  imgPlaceholder("Pricelists option enabled in Pricing settings"),

  h2("Configuring the Discount Rules"),
  nav("Go to Sales App → Products → Pricelists → New"),
  p("Enter a name (e.g., \"Wholesale Pricing\") and open the **Rules** tab. Click **Add a line** to define a rule:"),
  bullet("**Apply On**: Product (for a specific item) or Category (for all items in a group)"),
  bullet("**Price Type**: Discount — applies a percentage discount, visible to the customer on the quotation"),
  bullet("**Discount %**: The percentage to reduce (e.g., 15)"),
  bullet("**Min Qty**: The minimum order quantity that activates this rule (e.g., 100)"),
  p("Click **Save & Close**."),
  imgPlaceholder("Completed price rule showing 15% discount at minimum 100 units"),
  p("For tiered pricing, repeat the step with different thresholds:"),
  spacer(),
  makeTable(
    ["Rule", "Min Qty", "Discount"],
    [["1", "20", "5%"], ["2", "50", "10%"], ["3", "100", "15%"]],
    [1560, 3900, 3900]
  ),
  spacer(),
  p("Odoo evaluates all matching rules and picks the one with the highest minimum quantity that the order meets. For example, an order of 75 units triggers the 10% discount (Rule 2)."),
  imgPlaceholder("Three tiered rules in the Price Rules tab"),

  h2("Linking the Pricelist to a Customer"),
  nav("Go to Sales App → Orders → Customers → Select customer"),
  p("In the **Sales & Purchase** tab, set the **Pricelist** field to \"Wholesale Pricing\" and save. This becomes the default pricelist for all future orders from this customer."),
  p("Alternatively, the pricelist can be changed directly on any individual quotation without modifying the customer record."),
  imgPlaceholder("Customer form with pricelist assigned"),

  h2("Creating a Sales Order to Verify"),
  nav("Go to Sales App → Orders → Quotations → New"),
  p("1. Select the customer (pricelist is auto-applied)"),
  p("2. Add the product"),
  p("3. Set quantity to 100"),
  p("The unit price updates automatically to reflect the 15% discount. To make the discount percentage visible as a separate column, enable **Discounts** under Sales → Configuration → Settings → Pricing."),
  imgPlaceholder("Sales order with discount auto-applied showing adjusted unit price"),
  p("Once confirmed, the sales order carries the discounted price through to invoicing — no manual intervention needed at any stage."),

  h2("When to Use Discount vs Formula"),
  spacer(),
  makeTable(
    ["", "Discount", "Formula"],
    [
      ["Customer sees the %", "Yes", "No"],
      ["Rounding (e.g., prices ending in .99)", "Not supported", "Supported"],
      ["Extra fee / margin adjustment", "Not supported", "Supported"],
      ["Use case", "B2B transparency", "Retail-ready pricing"],
    ],
    [3120, 3120, 3120]
  ),
  spacer(),
  p("Choose **Discount** when your customers expect to see the percentage reduction. Choose **Formula** when you want to control the final price appearance with rounding and surcharges."),

  h2("FAQ's"),
  ...faqItem(1, "Does the discount apply automatically or do I need to select it each time?", "Once a pricelist is assigned to a customer, it applies automatically to every new quotation for that customer. No manual selection is needed."),
  ...faqItem(2, "Can I apply quantity discounts to all products at once?", "Yes. In the price rule, set the Apply On field to All Products. The discount will apply to every product on the order that meets the minimum quantity."),
  ...faqItem(3, "What happens when a product matches rules from two different pricelists?", "Only one pricelist is active per quotation. The system uses the pricelist assigned to the customer, or the one manually selected on the quotation. Rules within that single pricelist are then evaluated by minimum quantity."),

  cta("Looking to set up automated pricing in Odoo 19 for your business? Connect with the experts at Infintor for a customized consultation. → infintor.com"),
];

// ═══════════════════════════════════════════
// Generate all three
// ═══════════════════════════════════════════
async function generate() {
  const configs = [
    { sections: v1Sections, file: "BLOG_Quantity_Based_Discounts_Odoo_19_V1.docx" },
    { sections: v2Sections, file: "BLOG_Quantity_Based_Discounts_Odoo_19_V2.docx" },
    { sections: v3Sections, file: "BLOG_Quantity_Based_Discounts_Odoo_19_V3.docx" },
  ];

  for (const cfg of configs) {
    const doc = makeDoc(
      "How to Automate Quantity-Based Discounts in Odoo 19",
      "Rohan Raj",
      "Mar 5, 2026",
      cfg.sections
    );
    const buffer = await Packer.toBuffer(doc);
    fs.writeFileSync(cfg.file, buffer);
    console.log(`Created: ${cfg.file}`);
  }
}

generate().catch(err => { console.error(err); process.exit(1); });
