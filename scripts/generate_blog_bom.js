const fs = require("fs");
const path = require("path");
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
// BOM BLOG: How to Configure Bill of Materials (BOM) in Odoo
// ═══════════════════════════════════════════════════════════════
const bomBlogSections = [
  // --- SEO Metadata ---
  p("**SEO Title:** How to Configure Bill of Materials in Odoo 19"),
  p("**Meta Description:** Learn how to configure a Bill of Materials (BOM) in Odoo 19 — components, operations, kits, multi-level BOMs, and by-products explained step by step."),
  p("**URL Slug:** /how-to-configure-bill-of-materials-bom-odoo-19"),
  p("**Primary Keyword:** Bill of Materials in Odoo 19"),
  p("**Supporting Keywords:** BOM configuration Odoo, Odoo Manufacturing module, kit BOM Odoo, multi-level BOM, Odoo work orders, Odoo 19 manufacturing, BOM types Odoo, by-products Odoo, Odoo ERP manufacturing"),
  spacer(),

  // --- Introduction ---
  p("Every manufactured product starts with a recipe — a structured list of raw materials, quantities, and production steps that tells the shop floor exactly what to do. In Odoo 19, this recipe is called a **Bill of Materials (BOM)**."),
  p("A well-configured BOM determines how Odoo generates manufacturing orders, calculates product costs, schedules work centers, and triggers procurement for missing components. Get the BOM right, and your entire production workflow operates with precision. Get it wrong, and your manufacturing orders will be incomplete, your costings inaccurate, and your delivery timelines unreliable."),
  p("This article walks through the exact steps to configure a Bill of Materials in Odoo 19, covering components, operations, BOM types, multi-level structures, and by-products."),
  imgPlaceholder("BOM configuration screen in Odoo 19 Manufacturing module showing components tab"),

  // --- Understanding BOM Types ---
  h2("Understanding BOM Types in Odoo 19"),
  p("Before creating a BOM, it is important to understand the three BOM types available in Odoo 19. Each serves a distinctly different business purpose."),
  p("**Manufacture this Product** is the standard BOM type. When a manufacturing order is confirmed for the product, Odoo references this BOM to determine which components to consume and which operations to execute. The finished product is then added to inventory upon completion."),
  p("**Kit** works entirely differently. A Kit BOM does not trigger a manufacturing order at all. Instead, when the product is sold and a delivery order is created, Odoo automatically breaks the kit into its individual components for shipping. On the sales order, the customer sees a single line item. On the delivery order, each component appears separately. This is particularly useful for businesses that sell unassembled furniture, bundled product sets, or promotional packages."),
  p("**Subcontracting** designates that the product is manufactured by an external vendor. Odoo tracks the components sent to the subcontractor and the finished goods received back, managing the entire workflow through purchase orders and receipts."),
  spacer(),
  makeTable(
    ["BOM Type", "Triggers MO?", "Best For"],
    [
      ["Manufacture this Product", "Yes", "Standard in-house manufacturing"],
      ["Kit", "No", "Bundled products, unassembled sets sold to customers"],
      ["Subcontracting", "Yes (at vendor)", "Production outsourced to external manufacturers"],
    ],
    [3120, 3120, 3120]
  ),
  spacer(),

  // --- Creating a BOM ---
  h2("Creating a Bill of Materials"),
  p("To create a new BOM, navigate to the Manufacturing module and follow this path:"),
  nav("Manufacturing → Products → Bills of Materials → New"),
  p("Alternatively, open any product form — accessible through the Sales, Inventory, or Manufacturing apps — and click the **Bill of Materials** smart button at the top of the page. This is often the faster approach when you are already working on a specific product."),
  p("On the BOM form:"),
  bullet("**Product** — identifies what this BOM produces"),
  bullet("**Quantity** — specifies how many units of the finished product this BOM yields"),
  bullet("**BoM Type** — determines the BOM's behaviour (Manufacture, Kit, or Subcontracting)"),
  imgPlaceholder("New BOM form in Odoo 19 with Product, Quantity, and BoM Type fields highlighted"),

  // --- Adding Components ---
  h2("Adding Components"),
  p("The **Components** tab is where you define the raw materials and sub-components required for production."),
  p("Click **Add a line**, then select an existing product from the drop-down or type a name to create a new component on the fly. Specify the required quantity and unit of measure for each line."),
  p("Beyond the basics, Odoo offers several optional columns that can be activated by clicking the **settings adjust icon** at the top-right of the Components tab:"),
  bullet("**Apply on Variants** — Assign specific components to specific product variants. When left blank, the component is used across all variants. This is valuable for businesses manufacturing products in multiple sizes, colours, or materials from a single BOM."),
  bullet("**Consumed in Operation** — Specify which manufacturing operation uses each component. This directly impacts Odoo's manufacturing readiness calculations."),
  bullet("**Manual Consumption** — When ticked, operators must manually confirm that the component was consumed during production. If they do not, Odoo triggers a consumption warning and blocks the operation until the quantity is verified."),
  imgPlaceholder("Components tab with Apply on Variants and Consumed in Operation columns visible"),

  // --- Configuring Operations ---
  h2("Configuring Operations"),
  p("Operations define the production steps that the shop floor follows when manufacturing the product."),
  p("**Important:** The Operations tab only appears after enabling the **Work Orders** feature. Navigate to:"),
  nav("Manufacturing → Configuration → Settings → Operations section → tick Work Orders"),
  p("Once enabled, go to the **Operations** tab on the BOM and click **Add a line**. This opens the **Create Operations** pop-up with the following fields:"),
  bullet("**Operation** — the name of the production step (e.g., \"Cut\", \"Assemble\", \"Paint\")"),
  bullet("**Work Center** — the physical location where the operation is performed"),
  bullet("**Apply on Variants** — restrict the operation to specific product variants, or leave blank to apply it to all"),
  bullet("**Duration Computation** — choose between **Compute based on tracked time** (Odoo estimates duration from past work orders) or **Set duration manually** (you enter a fixed default duration)"),
  bullet("**Default Duration** — the estimated time for the operation, used for planning and scheduling"),
  p("Each operation also includes a **Work Sheet** tab where you can attach detailed instructions as a PDF, link a public Google Slide, or type instructions directly into a text field."),
  p("After filling out the form, click **Save & Close** — or **Save & New** to add another operation in sequence."),
  imgPlaceholder("Create Operations pop-up in Odoo 19 with operation name, work center, and duration fields"),

  // --- Miscellaneous Tab ---
  h2("Configuring the Miscellaneous Tab"),
  p("The **Miscellaneous** tab contains additional settings that control procurement, cost tracking, and component consumption:"),
  bullet("**Manufacturing Readiness** — Choose between \"When components for the 1st operation are available\" or \"When all components are available.\" The first option allows operators to begin production as soon as the initial operation's materials are in stock, even if later components are still pending."),
  bullet("**Flexible Consumption** — Controls whether operators may deviate from the BOM quantities. Options include **Blocked** (strict adherence required), **Allowed**, and **Allowed with Warning**."),
  bullet("**Routing** — Select a specific warehouse's manufacturing operation type if the product is manufactured in multiple locations."),
  bullet("**Manufacturing Lead Time** — the number of days required to complete a manufacturing order from confirmation."),
  bullet("**Days to Prepare Manufacturing Order** — the number of days needed to replenish components or manufacture sub-assemblies before production begins."),
  imgPlaceholder("Miscellaneous tab on a BOM in Odoo 19 showing Manufacturing Readiness and Flexible Consumption"),

  // --- By-Products ---
  h2("Adding By-Products"),
  p("Some manufacturing processes produce residual materials alongside the main product. Odoo handles these through the **By-Products** feature."),
  p("To enable it, navigate to:"),
  nav("Manufacturing → Configuration → Settings → Operations section → tick By-Products"),
  p("Once enabled, a **By-products** tab appears on the BOM. Click **Add a line** and specify the by-product name, quantity, unit of measure, and optionally the operation in which it is produced."),
  p("For example, a winery producing Red Wine might configure \"Mush\" as a by-product generated during the \"Grind Grapes\" operation. Odoo tracks the by-product quantities separately in inventory."),
  imgPlaceholder("By-products tab on a BOM showing Mush as a by-product of the Grind Grapes operation"),

  // --- Multi-Level BOMs ---
  h2("Multi-Level BOMs for Complex Products"),
  p("When a manufactured product contains components that are themselves manufactured — sub-assemblies — Odoo supports **multi-level BOMs**."),
  p("The process works by nesting BOMs within other BOMs. A custom keyboard, for example, might have a top-level BOM listing key caps, switches, a keyboard plate, and a printed circuit board (PCB). The PCB, in turn, has its own BOM containing transistors, resistors, and capacitors."),
  p("The recommended approach is to build multi-level BOMs from the bottom up. Start by creating the lowest-level component BOMs (the PCB), then include those products as components in the higher-level BOM (the keyboard). When a manufacturing order is confirmed for the keyboard, Odoo identifies that the PCB also requires manufacturing and — with proper replenishment rules in place — automatically generates the necessary sub-manufacturing orders."),
  p("For production planning with multi-level BOMs, create **reordering rules** for sublevel products with minimum and maximum quantities both set to zero. This ensures Odoo triggers manufacturing exactly when demand arises, without maintaining excess stock."),
  imgPlaceholder("Multi-level BOM structure in Odoo 19 showing a keyboard BOM containing a PCB sub-assembly"),

  // --- FAQs ---
  h2("Frequently Asked Questions"),
  ...faqItem(1, "What is a Bill of Materials (BOM) in Odoo 19?", "A BOM is a structured document that defines the components, quantities, and operations required to manufacture a product. Odoo uses the BOM to generate manufacturing orders, calculate costs, and manage production workflows."),
  ...faqItem(2, "What are the different types of BOMs available in Odoo?", "Odoo 19 offers three BOM types: Manufacture this Product (standard manufacturing), Kit (breaks into components at delivery, no manufacturing order), and Subcontracting (production handled by an external vendor)."),
  ...faqItem(3, "How do I add manufacturing operations to a BOM?", "First, enable the Work Orders feature under Manufacturing \u2192 Configuration \u2192 Settings. Then, on the BOM form, go to the Operations tab, click Add a line, and configure the operation name, work center, and duration."),
  ...faqItem(4, "What is a multi-level BOM and when should I use it?", "A multi-level BOM nests one BOM inside another — used when your finished product contains components that are themselves manufactured. Build from the bottom level up and set reordering rules on sub-assembly products for automated procurement."),
  ...faqItem(5, "How does Odoo calculate the cost of a manufactured product using a BOM?", "Odoo automatically calculates the total cost based on the purchase prices of all components listed in the BOM, plus the cost of operations (work center hourly rates multiplied by operation duration)."),
  ...faqItem(6, "What is the difference between a Kit BOM and a Manufacturing BOM?", "A Manufacturing BOM triggers a manufacturing order — components are consumed and a finished product is produced. A Kit BOM does not trigger any manufacturing. Instead, when the kit is sold, Odoo breaks it into individual components on the delivery order. The customer sees one product; the warehouse ships separate parts."),

  // --- Conclusion ---
  h2("Conclusion"),
  p("A correctly configured Bill of Materials is the foundation of every production workflow in Odoo 19. It determines what gets consumed, how operations are sequenced, what costs are calculated, and how procurement is triggered across your supply chain. Whether you are manufacturing a single product, selling unassembled kits, or managing complex sub-assemblies across multiple levels, the BOM is where it all begins."),
  p("For businesses looking to implement Odoo's Manufacturing module or optimise their existing BOM configurations, working with an experienced Odoo implementation partner ensures the setup aligns with your actual shop floor processes from day one."),

  cta("Infintor Solutions is an Official Odoo Partner in India. Looking to configure your manufacturing operations in Odoo 19? Connect with our Odoo consultants for expert guidance on BOM setup, production planning, and MRP implementation. \u2192 infintor.com/contactus"),
];


// ═══════════════════════════════════════════
// Generate DOCX
// ═══════════════════════════════════════════
const OUT_PATH = path.join(__dirname, "..", "My learnings", "Blogs InDevelopment", "BLOG_BOM_Configuration_Odoo_19.docx");

async function main() {
  const doc = makeDoc(
    "How to Configure Bill of Materials (BOM) in Odoo",
    "Rohan Raj  |  Infintor Solutions",
    "Mar 24, 2026",
    bomBlogSections
  );
  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync(OUT_PATH, buf);
  console.log(`Created: ${OUT_PATH}  (${(buf.length / 1024).toFixed(0)} KB)`);
}

main().catch(err => { console.error(err); process.exit(1); });
