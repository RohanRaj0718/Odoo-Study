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
// BLOG 1: Product Discounts Using Pricelists
// ═══════════════════════════════════════════
const blog1Sections = [
  p("Want to offer \"Buy 2, get 10% off\" or \"Buy 10, get 20% off\" on specific products? Odoo 19 lets you automate this through **Pricelist Price Rules** \u2014 configure the discount once, and it kicks in automatically whenever a customer meets the quantity threshold on a sales order."),

  h2("Enabling the Pricelists Feature"),
  nav("Go to Sales App \u2192 Configuration \u2192 Settings \u2192 Pricing section"),
  p("Enable the **Pricelists** checkbox and click **Save**. This unlocks the ability to create custom pricing rules that override standard product prices."),
  imgPlaceholder("Pricelists checkbox enabled under Pricing settings"),

  h2("Creating a Pricelist with Discount Rules"),
  nav("Go to Sales App \u2192 Products \u2192 Pricelists \u2192 New"),
  p("Enter a name for the pricelist (e.g., \"Product Discount \u2014 Bulk Buyers\"). Select the appropriate **Currency** and, if needed, assign a **Company** for multi-company setups."),
  p("Open the **Price Rules** tab and click **Add a line** to define your first discount rule."),
  imgPlaceholder("New pricelist form with name and currency filled in"),

  h3("Configuring a Price Rule"),
  p("Fill in the following fields on the rule form:"),
  spacer(),
  makeTable(
    ["Field", "What to Set"],
    [
      ["Apply To", "Select Product to target a specific item, or Category to cover all products in a group"],
      ["Product", "Choose the product (e.g., \"Laptop Stand\")"],
      ["Price Type", "Select Discount \u2014 this shows the discount % directly on the quotation"],
      ["Discount", "Enter the percentage (e.g., 10 for 10% off)"],
      ["Min Qty", "Set the minimum quantity to trigger the discount (e.g., 2)"],
      ["Validity Period", "Optionally set a start and end date"],
    ],
    [3120, 6240]
  ),
  spacer(),
  p("Click **Save & Close**. With this setup, any order with 2 or more units of \"Laptop Stand\" automatically gets 10% off."),
  imgPlaceholder("Price rule configured \u2014 10% discount on Laptop Stand at minimum 2 units"),

  h3("Adding Tiered Discounts"),
  p("To reward larger orders with bigger discounts, add multiple rules for the same product with increasing quantities:"),
  spacer(),
  makeTable(
    ["Min Qty", "Discount", "Meaning"],
    [
      ["2", "10%", "Buy 2+, get 10% off"],
      ["5", "15%", "Buy 5+, get 15% off"],
      ["10", "20%", "Buy 10+, get 20% off"],
    ],
    [2340, 2340, 4680]
  ),
  spacer(),
  p("Odoo automatically picks the **highest qualifying rule**. An order of 7 units triggers the 15% discount (Min Qty 5), not the 10% one."),
  imgPlaceholder("Three tiered rules in the Price Rules tab for the same product"),

  h2("Assigning the Pricelist to a Customer"),
  nav("Go to Sales App \u2192 Orders \u2192 Customers \u2192 select the customer"),
  p("Under the **Sales & Purchase** tab, set the **Pricelist** field to \"Product Discount \u2014 Bulk Buyers\" and save."),
  p("Every new quotation for this customer will automatically use this pricelist. You can also change the pricelist directly on any individual quotation without touching the customer record."),
  imgPlaceholder("Customer form with the pricelist assigned under Sales & Purchase tab"),

  h2("Verifying the Discount on a Sales Order"),
  nav("Go to Sales App \u2192 Orders \u2192 Quotations \u2192 New"),
  p("Select the customer \u2014 the pricelist auto-populates. Add the product (e.g., \"Laptop Stand\") and set the quantity to 5."),
  p("The discount applies instantly. If you have the **Discounts** setting enabled (Sales \u2192 Configuration \u2192 Settings \u2192 Pricing \u2192 Discounts), a **Disc.%** column appears on the order line showing the exact percentage."),
  imgPlaceholder("Sales order with 5 units of Laptop Stand showing 15% discount applied"),
  p("Once confirmed, the discounted price flows through to delivery and invoicing automatically \u2014 no manual adjustments needed."),

  h2("Discount vs Formula \u2014 Choosing the Right Price Type"),
  spacer(),
  makeTable(
    ["", "Discount", "Formula"],
    [
      ["Discount % visible to customer", "Yes", "No"],
      ["Rounding (e.g., prices ending in .99)", "Not supported", "Supported"],
      ["Extra fee / margin adjustment", "Not supported", "Supported"],
      ["Best for", "B2B pricing with transparency", "Retail pricing with presentation control"],
    ],
    [3120, 3120, 3120]
  ),
  spacer(),
  p("Use **Discount** when your customers should see the percentage they're saving. Use **Formula** when you want to control the final price appearance with rounding or surcharges."),

  h2("FAQ's"),
  ...faqItem(1, "Can I apply the same discount rule to an entire product category instead of one product?", "Yes. When creating the price rule, set the Apply To field to Category and select the desired category. The discount applies to every product within that category when the minimum quantity is met."),
  ...faqItem(2, "What if a customer orders less than the minimum quantity?", "The discount does not apply. Odoo only triggers the price rule when the order line quantity meets or exceeds the configured Min Qty threshold."),
  ...faqItem(3, "Can different customers get different discounts on the same product?", "Yes. Create separate pricelists with different discount rules and assign each pricelist to the respective customer on their contact form. Each customer's quotation will use their assigned pricelist."),

  cta("Looking to automate product discounts in Odoo 19 for your business? Connect with the experts at Infintor for a customized consultation. \u2192 infintor.com"),
];

// ═══════════════════════════════════════════
// BLOG 2: Reordering Rules
// ═══════════════════════════════════════════
const blog2Sections = [
  p("Running out of stock means lost sales. Overstocking ties up capital. Odoo 19's **Reordering Rules** solve both problems by automatically generating purchase or manufacturing orders when stock falls below a defined threshold \u2014 keeping inventory at the right level without manual tracking."),

  h2("Configuring the Product"),
  nav("Go to Inventory App \u2192 Products \u2192 Products \u2192 select a product"),
  p("Under the **General Information** tab, set the **Product Type** to *Goods* and enable **Track Inventory**. Without these two settings, Odoo cannot monitor stock levels for the product."),
  p("If the product is purchased, open the **Purchase** tab and add at least one vendor to the vendor pricelist. If the product is manufactured, ensure a **Bill of Materials** exists (visible via the smart button at the top)."),
  imgPlaceholder("Product form with Product Type set to Goods and Track Inventory enabled"),

  h2("Creating a Reordering Rule"),
  nav("Go to Inventory App \u2192 Operations \u2192 Replenishment \u2192 New"),
  p("Fill in the following fields:"),
  spacer(),
  makeTable(
    ["Field", "What to Set"],
    [
      ["Product", "Select the product to replenish"],
      ["Location", "Where stock is stored (default: WH/Stock)"],
      ["Min", "Minimum forecasted quantity before the rule triggers (e.g., 10)"],
      ["Max", "Target quantity to replenish up to (e.g., 50)"],
    ],
    [3120, 6240]
  ),
  spacer(),
  p("When the forecasted quantity drops below **Min**, Odoo automatically creates a purchase order (for Buy route) or manufacturing order (for Manufacture route) to bring stock back up to **Max**."),
  imgPlaceholder("Reordering rule form with Min 10 and Max 50 configured"),
  p("You can also create reordering rules directly from the product form by clicking the **Reordering Rules** smart button at the top."),

  h2("Choosing Automatic vs Manual Trigger"),
  p("By default, reordering rules trigger automatically. To see or change this, click the settings icon on the Replenishment page and enable the **Trigger** column."),
  spacer(),
  makeTable(
    ["Trigger", "How It Works"],
    [
      ["Auto", "Purchase/manufacturing order is created automatically when forecasted stock falls below Min \u2014 either when the scheduler runs or when a sales order is confirmed"],
      ["Manual", "The product appears on the Replenishment dashboard as a \"need\" \u2014 you review it and click Order to generate the purchase/manufacturing order"],
    ],
    [2340, 7020]
  ),
  spacer(),
  p("Use **Auto** for fast-moving products that should never run out. Use **Manual** for expensive or slow-moving items where you want to review before ordering."),
  imgPlaceholder("Trigger column showing Auto selected on a reordering rule"),
  p("The automatic scheduler runs once daily. To trigger it immediately, enable **Developer Mode** and go to Inventory \u2192 Operations \u2192 **Run Scheduler**."),

  h2("Setting a Preferred Route"),
  p("If a product has both **Buy** and **Manufacture** routes enabled, you can set a preferred route on the reordering rule. Enable the **Route** column on the Replenishment page (via the settings icon), then select the desired route from the dropdown."),
  p("If no preferred route is set, Odoo defaults to the **Buy** route first, then Manufacture."),
  imgPlaceholder("Route column with Buy selected as preferred route"),

  h2("The 0/0/1 Rule for Make-to-Order Without Reservation"),
  p("A special variation: set **Min = 0**, **Max = 0**, and **To Order = 1**. This creates a purchase or manufacturing order every time a sales order causes the forecasted quantity to drop below zero \u2014 effectively a make-to-order workflow, but without reserving the stock for a specific sales order."),
  imgPlaceholder("Reordering rule with Min 0, Max 0, To Order 1"),

  h2("FAQ's"),
  ...faqItem(1, "What's the difference between Min and Max?", "Min is the trigger point \u2014 when forecasted stock falls below this number, replenishment kicks in. Max is the target \u2014 Odoo orders enough to bring stock back up to this quantity. The difference between Max and the current forecast is the quantity ordered."),
  ...faqItem(2, "Can I set reordering rules for multiple products at once?", "Yes. Navigate to Inventory \u2192 Operations \u2192 Replenishment and click New for each product. You can create and manage all reordering rules from this single page."),
  ...faqItem(3, "Does the reordering rule work with the Manufacture route?", "Yes. If the product has a Bill of Materials and the Manufacture route is enabled, the reordering rule generates a manufacturing order instead of a purchase order when triggered."),

  cta("Looking to automate your inventory replenishment in Odoo 19? Connect with the experts at Infintor for a customized consultation. \u2192 infintor.com"),
];

// ═══════════════════════════════════════════
// BLOG 3: Units of Measure
// ═══════════════════════════════════════════
const blog3Sections = [
  p("Buying fabric in meters but selling it in yards? Purchasing chemicals in drums but consuming them in liters? Odoo 19's **Units of Measure (UoM)** feature handles all conversions automatically \u2014 across purchases, sales, inventory, and manufacturing \u2014 so you never have to calculate manually."),

  h2("Enabling Units of Measure"),
  nav("Go to Inventory App \u2192 Configuration \u2192 Settings \u2192 Products section"),
  p("Enable the **Units of Measure & Packagings** checkbox and click **Save**."),
  imgPlaceholder("Units of Measure & Packagings setting enabled in Inventory configuration"),

  h2("Configuring UoM on a Product"),
  nav("Go to Inventory App \u2192 Products \u2192 Products \u2192 select a product"),

  h3("Inventory Unit of Measure"),
  p("The inventory UoM defines how the product is tracked internally. Set it using the unit field next to the **Sales Price** or **Cost** fields on the product form."),
  p("For example, if you track blue fabric in *yards*, set the unit to \"yard.\" This unit is used across all internal inventory operations \u2014 stock counts, internal transfers, and warehouse reports."),
  imgPlaceholder("Product form showing inventory unit of measure set to yard"),

  h3("Purchase Unit of Measure"),
  p("Open the **Purchase** tab on the product form. In the vendor pricelist, the **Unit** column defines the unit used when purchasing from each vendor."),
  p("For example, if your vendor sells fabric in *meters*, set the purchase unit to \"m\" in the vendor line. When you create a purchase order, it shows meters. When the goods arrive, the warehouse receipt automatically converts the quantity to your inventory unit (yards)."),
  imgPlaceholder("Purchase tab showing vendor unit set to meters"),

  h3("Sales Packagings"),
  p("Open the **Sales** tab on the product form. Under **Upsell & Cross-Sell**, add packagings to the **Packagings** field. Packagings define the units the product is sold in \u2014 for example, selling paint in \"Boxes of 12 cans.\""),
  imgPlaceholder("Sales tab with packaging defined"),

  h2("How Automatic Conversion Works"),
  p("Odoo converts units automatically at every handoff:"),
  spacer(),
  makeTable(
    ["Transaction", "Unit Used", "Converts To"],
    [
      ["Purchase Order", "Purchase UoM (e.g., meters)", "\u2014"],
      ["Warehouse Receipt", "Inventory UoM (e.g., yards)", "Automatic on receipt"],
      ["Sales Order", "Sales UoM (e.g., meters)", "\u2014"],
      ["Delivery Order", "Inventory UoM (e.g., yards)", "Automatic on delivery"],
    ],
    [3120, 3120, 3120]
  ),
  spacer(),
  p("You place a purchase order for 10 meters of fabric. The warehouse receipt shows 10.94 yards (the converted quantity). No manual math needed."),
  imgPlaceholder("Purchase order in meters and warehouse receipt showing converted yards"),

  h2("Creating Custom Units of Measure"),
  nav("Go to Inventory App \u2192 Configuration \u2192 Units & Packagings \u2192 New"),
  p("Enter the unit name, then specify the conversion by entering a **Quantity** relative to a **Reference Unit**. Odoo uses this ratio for all automatic conversions."),
  p("For example, to create \"yard\" as a custom unit: set Quantity to 0.9144 and Reference Unit to m. This tells Odoo that 1 yard = 0.9144 meters."),
  imgPlaceholder("Custom UoM configuration showing yard to meter conversion"),
  p("All custom units must belong to a **UoM Category** (e.g., Length, Weight, Volume). Units within the same category can convert between each other. Units in different categories cannot."),

  h2("FAQ's"),
  ...faqItem(1, "Can I use different units for buying and selling the same product?", "Yes. Set the purchase unit in the Purchase tab vendor pricelist and the inventory unit in the Sales Price field. Odoo converts between them automatically on receipts and deliveries, as long as both units belong to the same UoM category."),
  ...faqItem(2, "What happens if I change the unit of measure on an existing product?", "Changing the UoM on a product with existing inventory can cause stock discrepancies. It's best to set the correct UoM before recording any stock movements. If a change is necessary, adjust your inventory quantities accordingly."),
  ...faqItem(3, "Can I track inventory in one unit and display a different unit on invoices?", "Yes. The sales order uses the unit specified on the order line (which can differ from the inventory unit). Invoices reflect the sales order unit, while warehouse operations use the inventory unit."),

  cta("Looking to configure multi-unit inventory management in Odoo 19? Connect with the experts at Infintor for a customized consultation. \u2192 infintor.com"),
];

// ═══════════════════════════════════════════
// Generate all 3 docx files
// ═══════════════════════════════════════════
const OUTPUT_DIR = "My learnings/Rohan_Documentation";

const blogs = [
  {
    title: "Setting Up Product Discounts Using Pricelists in Odoo 19",
    file: `${OUTPUT_DIR}/BLOG_Product_Discounts_Pricelist_Odoo_19.docx`,
    sections: blog1Sections,
  },
  {
    title: "Setting Up Reordering Rules in Odoo 19",
    file: `${OUTPUT_DIR}/BLOG_Reordering_Rules_Odoo_19.docx`,
    sections: blog2Sections,
  },
  {
    title: "How to Use Units of Measure in Odoo 19",
    file: `${OUTPUT_DIR}/BLOG_Units_of_Measure_Odoo_19.docx`,
    sections: blog3Sections,
  },
];

(async () => {
  for (const blog of blogs) {
    const doc = makeDoc(blog.title, "Rohan Raj", "Mar 9, 2026", blog.sections);
    const buffer = await Packer.toBuffer(doc);
    fs.writeFileSync(blog.file, buffer);
    console.log(`Created: ${blog.file}`);
  }
  console.log("\nAll 3 blog docx files generated successfully!");
})();
