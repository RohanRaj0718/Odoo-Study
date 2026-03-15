const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, ExternalHyperlink,
  HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak, TableOfContents
} = require("docx");

// ─── Constants ───
const PAGE_WIDTH = 12240;
const MARGIN = 1440;
const CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN; // 9360

// ─── Helpers ───
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const headerBorder = { style: BorderStyle.SINGLE, size: 1, color: "1F4E79" };
const headerBorders = { top: headerBorder, bottom: headerBorder, left: headerBorder, right: headerBorder };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };

function headerCell(text, width) {
  return new TableCell({
    borders: headerBorders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: "1F4E79", type: ShadingType.CLEAR },
    margins: cellMargins,
    verticalAlign: "center",
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })],
  });
}

function cell(text, width, opts = {}) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: opts.shading ? { fill: opts.shading, type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    children: [new Paragraph({
      alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
      children: [new TextRun({ text, font: "Arial", size: 20, bold: !!opts.bold, color: opts.color || "333333" })],
    })],
  });
}

function heading1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 200 }, children: [new TextRun({ text, bold: true, font: "Arial", size: 32, color: "1F4E79" })] });
}

function heading2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 160 }, children: [new TextRun({ text, bold: true, font: "Arial", size: 26, color: "2E75B6" })] });
}

function heading3(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 120 }, children: [new TextRun({ text, bold: true, font: "Arial", size: 22, color: "404040" })] });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.afterSpacing || 160 },
    alignment: opts.alignment || AlignmentType.LEFT,
    children: Array.isArray(text)
      ? text.map(t => new TextRun(typeof t === "string" ? { text: t, font: "Arial", size: 20, color: "333333" } : { font: "Arial", size: 20, color: "333333", ...t }))
      : [new TextRun({ text, font: "Arial", size: 20, color: "333333" })],
  });
}

function bulletItem(text, ref = "bullets") {
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { after: 80 },
    children: Array.isArray(text)
      ? text.map(t => new TextRun(typeof t === "string" ? { text: t, font: "Arial", size: 20, color: "333333" } : { font: "Arial", size: 20, color: "333333", ...t }))
      : [new TextRun({ text, font: "Arial", size: 20, color: "333333" })],
  });
}

function numberedItem(text, ref = "numbers") {
  return new Paragraph({
    numbering: { reference: ref, level: 0 },
    spacing: { after: 80 },
    children: Array.isArray(text)
      ? text.map(t => new TextRun(typeof t === "string" ? { text: t, font: "Arial", size: 20, color: "333333" } : { font: "Arial", size: 20, color: "333333", ...t }))
      : [new TextRun({ text, font: "Arial", size: 20, color: "333333" })],
  });
}

function calloutBox(title, bodyLines) {
  const rows = [];
  const content = [];
  content.push(new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: title, bold: true, font: "Arial", size: 20, color: "1F4E79" })] }));
  bodyLines.forEach(line => {
    content.push(new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: line, font: "Arial", size: 19, color: "333333" })] }));
  });
  rows.push(new TableRow({
    children: [new TableCell({
      borders: { top: { style: BorderStyle.SINGLE, size: 1, color: "BDD7EE" }, bottom: { style: BorderStyle.SINGLE, size: 1, color: "BDD7EE" }, left: { style: BorderStyle.SINGLE, size: 6, color: "2E75B6" }, right: { style: BorderStyle.SINGLE, size: 1, color: "BDD7EE" } },
      width: { size: CONTENT_WIDTH, type: WidthType.DXA },
      shading: { fill: "EAF2FB", type: ShadingType.CLEAR },
      margins: { top: 120, bottom: 120, left: 200, right: 200 },
      children: content,
    })],
  }));
  return new Table({ width: { size: CONTENT_WIDTH, type: WidthType.DXA }, columnWidths: [CONTENT_WIDTH], rows });
}

function spacer() {
  return new Paragraph({ spacing: { after: 80 }, children: [new TextRun("")] });
}

// ─── Document ───
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "1F4E79" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Arial", color: "404040" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers2", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers3", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers4", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "bullets2", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "bullets3", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ],
  },
  sections: [
    // ─── COVER PAGE ───
    {
      properties: {
        page: {
          size: { width: PAGE_WIDTH, height: 15840 },
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
        },
      },
      children: [
        spacer(), spacer(), spacer(), spacer(), spacer(),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: "ODOO 19 KNOWLEDGE BASE", font: "Arial", size: 22, color: "2E75B6", bold: true })] }),
        spacer(),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E75B6", space: 8 } },
          children: [new TextRun({ text: "Inventory Valuation, Internal Transfers", font: "Arial", size: 44, bold: true, color: "1F4E79" })],
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 300 },
          children: [new TextRun({ text: "& Journal Entry Behavior Guide", font: "Arial", size: 44, bold: true, color: "1F4E79" })],
        }),
        spacer(),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "Odoo 18 vs Odoo 19 Architecture Changes", font: "Arial", size: 24, color: "666666" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "With Live API Test Results & Official Documentation References", font: "Arial", size: 22, color: "888888" })] }),
        spacer(), spacer(), spacer(), spacer(),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Prepared by: Rohan Raj", font: "Arial", size: 22, color: "333333" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Business Analyst Intern | Infintor Solutions", font: "Arial", size: 20, color: "666666" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Date: March 3, 2026", font: "Arial", size: 20, color: "666666" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Client Database: client-cient.odoo.com (Odoo 19 / saas-19.1+e)", font: "Arial", size: 20, color: "666666" })] }),
      ],
    },
    // ─── TOC PAGE ───
    {
      properties: {
        page: {
          size: { width: PAGE_WIDTH, height: 15840 },
          margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
        },
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "2E75B6", space: 4 } },
            children: [new TextRun({ text: "Odoo 19 — Inventory Valuation & Internal Transfers Guide", font: "Arial", size: 16, color: "999999", italics: true })],
          })],
        }),
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            border: { top: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC", space: 4 } },
            children: [
              new TextRun({ text: "Infintor Solutions | Confidential | Page ", font: "Arial", size: 16, color: "999999" }),
              new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "999999" }),
            ],
          })],
        }),
      },
      children: [
        heading1("Table of Contents"),
        new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
        new Paragraph({ children: [new PageBreak()] }),

        // ─── SECTION 1: EXECUTIVE SUMMARY ───
        heading1("1. Executive Summary"),
        para("This document covers a critical architectural change in Odoo 19 regarding how inventory valuation and journal entries work. It addresses a common question from implementers and accountants: \"Why are no journal entries created for internal transfers in Odoo 19?\""),
        para("The answer is: This is by design. Odoo 19 fundamentally changed how the Perpetual inventory valuation method works. In Odoo 18 and earlier, every stock movement (receipt, delivery, internal transfer, scrap, manufacturing, etc.) automatically created journal entries. In Odoo 19, journal entries are only created at the invoice/bill level, plus one closing entry that captures all gaps."),
        spacer(),
        calloutBox("Key Finding", [
          "Internal transfers DO NOT create journal entries in Odoo 19 — confirmed via live testing on the client database across all 4 costing methods and 2 transfer types (8 combinations total). This is official Odoo 19 behavior, not a bug or misconfiguration."
        ]),
        spacer(),

        // ─── SECTION 2: ACCOUNTING METHODS ───
        heading1("2. Accounting Methods: Periodic vs Perpetual"),
        para("Odoo supports two accounting methods for inventory valuation, configured at two levels."),
        spacer(),

        heading2("2.1 Where to Configure"),
        heading3("A) Company-Level Setting (Accounting App)"),
        para([
          { text: "Path: ", bold: true },
          { text: "Accounting \u2192 Configuration \u2192 Settings \u2192 Inventory Valuation section" },
        ]),
        bulletItem([{ text: "Periodic: ", bold: true }, { text: "Post vendor bills as expenses by nature. Update stock valuation only via closing entry. Best practice in Europe (Continental accounting)." }]),
        bulletItem([{ text: "Perpetual: ", bold: true }, { text: "Post vendor bills as assets (stock valuation). Report expenses when goods are sold (COGS). Best practice in India/USA (Anglo-Saxon accounting)." }]),
        spacer(),

        heading3("B) Product Category Level (Inventory App)"),
        para([
          { text: "Path: ", bold: true },
          { text: "Inventory \u2192 Configuration \u2192 Product Categories \u2192 [select category] \u2192 Inventory Valuation field" },
        ]),
        bulletItem([{ text: "Periodic (at closing): ", bold: true }, { text: "No automatic journal entries for stock moves. Closing entry is done manually or via the Review menu." }]),
        bulletItem([{ text: "Perpetual (at invoicing): ", bold: true }, { text: "In Odoo 19, journal entries are created at invoice/bill level only. A closing entry captures everything else." }]),
        spacer(),

        heading2("2.2 Costing Methods"),
        para("Each product category also has a Costing Method:"),

        // Costing Methods Table
        new Table({
          width: { size: CONTENT_WIDTH, type: WidthType.DXA },
          columnWidths: [2200, 7160],
          rows: [
            new TableRow({ children: [headerCell("Method", 2200), headerCell("Description", 7160)] }),
            new TableRow({ children: [
              cell("Standard Cost", 2200, { bold: true }),
              cell("Fixed unit cost, updated manually. Cost stays the same regardless of purchase price.", 7160),
            ]}),
            new TableRow({ children: [
              cell("Average Cost (AVCO)", 2200, { bold: true }),
              cell("Weighted average of all units in stock. Updates with each new purchase.", 7160),
            ]}),
            new TableRow({ children: [
              cell("FIFO", 2200, { bold: true }),
              cell("First In, First Out. Oldest inventory cost is used first when selling.", 7160),
            ]}),
          ],
        }),
        spacer(),

        calloutBox("Client Configuration", [
          "All product categories on the client database (client-cient.odoo.com) currently use Periodic + Standard Cost. With Periodic valuation, automatic journal entries for stock moves were NEVER created, even in Odoo 18. The closing entry approach was always the design for Periodic."
        ]),
        spacer(),
        new Paragraph({ children: [new PageBreak()] }),

        // ─── SECTION 3: INVENTORY vs ACCOUNTING ───
        heading1("3. Inventory App vs Accounting App"),
        para("A fundamental concept in Odoo 19 is that the Inventory app and Accounting app update at different times:"),
        spacer(),

        // Inventory vs Accounting Table
        new Table({
          width: { size: CONTENT_WIDTH, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({ children: [headerCell("Event", 3120), headerCell("Accounting", 3120), headerCell("Inventory", 3120)] }),
            new TableRow({ children: [cell("Purchase Order", 3120, { bold: true }), cell("/", 3120, { center: true }), cell("/", 3120, { center: true })] }),
            new TableRow({ children: [cell("Receipt (Goods In)", 3120, { bold: true }), cell("/", 3120, { center: true }), cell("\u2713 Updates", 3120, { center: true, color: "2E7D32" })] }),
            new TableRow({ children: [cell("Vendor Bill", 3120, { bold: true }), cell("\u2713 Updates", 3120, { center: true, color: "2E7D32" }), cell("/", 3120, { center: true })] }),
            new TableRow({ children: [cell("Sales Order", 3120, { bold: true }), cell("/", 3120, { center: true }), cell("/", 3120, { center: true })] }),
            new TableRow({ children: [cell("Delivery (Goods Out)", 3120, { bold: true }), cell("/", 3120, { center: true }), cell("\u2713 Updates", 3120, { center: true, color: "2E7D32" })] }),
            new TableRow({ children: [cell("Customer Invoice", 3120, { bold: true }), cell("\u2713 Updates", 3120, { center: true, color: "2E7D32" }), cell("/", 3120, { center: true })] }),
            new TableRow({ children: [cell("Closing Entry", 3120, { bold: true }), cell("\u2713 Updates", 3120, { center: true, color: "2E7D32" }), cell("/", 3120, { center: true })] }),
          ],
        }),
        spacer(),
        para("The gap between what Inventory records and what Accounting records is bridged by the Closing Entry."),
        spacer(),
        new Paragraph({ children: [new PageBreak()] }),

        // ─── SECTION 4: ODOO 18 vs 19 ───
        heading1("4. Odoo 18 vs Odoo 19: What Changed"),
        para("This is the most critical section. Odoo 19 made a fundamental architectural change to how Perpetual inventory valuation works."),
        spacer(),

        heading2("4.1 The Old Way (Odoo 18 and Earlier)"),
        para("In Odoo 18, the Perpetual (Automated) inventory valuation method created a journal entry for every single stock move. This included:"),
        bulletItem("Receipts (goods received from vendor)"),
        bulletItem("Deliveries (goods shipped to customer)"),
        bulletItem("Internal transfers (between warehouses/locations)"),
        bulletItem("Scrap (damaged/expired goods written off)"),
        bulletItem("Manufacturing \u2014 consuming raw materials"),
        bulletItem("Manufacturing \u2014 producing finished goods"),
        bulletItem("Inventory adjustments (physical count corrections)"),
        bulletItem("Customer returns"),
        bulletItem("Vendor returns"),
        bulletItem("Dropship (direct vendor-to-customer)"),
        spacer(),
        para([
          { text: "Official Odoo 18 docs stated: ", italics: true },
          { text: "\"each new stock move layer (SVL), that is created during inventory valuation updates, generates a journal entry.\"", bold: true, italics: true },
        ]),
        spacer(),

        heading2("4.2 The New Way (Odoo 19)"),
        para([
          { text: "Official Odoo 19 docs state: " },
          { text: "\"Before Odoo 19, the Perpetual accounting method was implemented by posting real-time accounting entries at each stock movement. That created a lot of journal items in accounting, which was an issue for performance, general ledger clarity and auditability.\"", bold: true, italics: true },
        ]),
        spacer(),
        para("In Odoo 19, NONE of these stock moves create per-move journal entries anymore. Journal entries are now created only at:"),
        numberedItem([{ text: "Invoice/Bill level ", bold: true }, { text: "(customer invoice or vendor bill)" }]),
        numberedItem([{ text: "One closing entry ", bold: true }, { text: "(captures everything else \u2014 scrap, manufacturing, transfers, adjustments, etc.)" }]),
        spacer(),

        heading2("4.3 Comparison Table (from Official Docs)"),
        // Comparison Table
        new Table({
          width: { size: CONTENT_WIDTH, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({ children: [headerCell("Feature", 3120), headerCell("Odoo 18", 3120), headerCell("Odoo 19", 3120)] }),
            new TableRow({ children: [cell("Periodic Continental", 3120, { bold: true }), cell("Manual closing", 3120, { center: true }), cell("Automated closing", 3120, { center: true, color: "2E7D32" })] }),
            new TableRow({ children: [cell("Periodic Anglo-Saxon", 3120, { bold: true }), cell("Not supported", 3120, { center: true, color: "C62828" }), cell("Fully supported", 3120, { center: true, color: "2E7D32" })] }),
            new TableRow({ children: [cell("Perpetual Continental", 3120, { bold: true }), cell("Manual closing", 3120, { center: true }), cell("\u2713 Automated", 3120, { center: true, color: "2E7D32" })] }),
            new TableRow({ children: [cell("Perpetual Anglo-Saxon", 3120, { bold: true }), cell("Manual closing", 3120, { center: true }), cell("\u2713 Automated", 3120, { center: true, color: "2E7D32" })] }),
            new TableRow({ children: [cell("Perpetual Entries", 3120, { bold: true, shading: "FFF9C4" }), cell("Invoices + every moves", 3120, { center: true, bold: true, shading: "FFF9C4" }), cell("Invoices + one closing", 3120, { center: true, bold: true, shading: "FFF9C4", color: "2E7D32" })] }),
            new TableRow({ children: [cell("Performance", 3120, { bold: true }), cell("Slower", 3120, { center: true, color: "C62828" }), cell("Faster", 3120, { center: true, color: "2E7D32" })] }),
            new TableRow({ children: [cell("General Ledger", 3120, { bold: true }), cell("More journal entries", 3120, { center: true }), cell("Fewer journal entries", 3120, { center: true, color: "2E7D32" })] }),
            new TableRow({ children: [cell("Bills to Receive", 3120, { bold: true }), cell("\u2717 Not supported", 3120, { center: true, color: "C62828" }), cell("\u2713 Supported", 3120, { center: true, color: "2E7D32" })] }),
            new TableRow({ children: [cell("Invoices to Issue", 3120, { bold: true }), cell("\u2717 Not supported", 3120, { center: true, color: "C62828" }), cell("\u2713 Supported", 3120, { center: true, color: "2E7D32" })] }),
            new TableRow({ children: [cell("Deferred Revenues", 3120, { bold: true }), cell("\u2717 Not supported", 3120, { center: true, color: "C62828" }), cell("\u2713 Supported", 3120, { center: true, color: "2E7D32" })] }),
            new TableRow({ children: [cell("Prepaid Expenses", 3120, { bold: true }), cell("\u2717 Not supported", 3120, { center: true, color: "C62828" }), cell("\u2713 Supported", 3120, { center: true, color: "2E7D32" })] }),
          ],
        }),
        spacer(),
        new Paragraph({ children: [new PageBreak()] }),

        // ─── SECTION 5: ALL STOCK MOVE TYPES ───
        heading1("5. All Stock Move Types & Their JE Behavior"),
        para("This table shows every type of stock move in Odoo and whether a journal entry is created automatically:"),
        spacer(),

        new Table({
          width: { size: CONTENT_WIDTH, type: WidthType.DXA },
          columnWidths: [2500, 2800, 2030, 2030],
          rows: [
            new TableRow({ children: [headerCell("Stock Move Type", 2500), headerCell("Description", 2800), headerCell("JE in Odoo 18\n(Perpetual)", 2030), headerCell("JE in Odoo 19", 2030)] }),
            new TableRow({ children: [cell("Receipt (Purchase)", 2500, { bold: true }), cell("Goods received from vendor", 2800), cell("\u2713 Yes", 2030, { center: true, color: "2E7D32" }), cell("\u2717 No (at bill)", 2030, { center: true, color: "C62828" })] }),
            new TableRow({ children: [cell("Delivery (Sales)", 2500, { bold: true }), cell("Goods shipped to customer", 2800), cell("\u2713 Yes", 2030, { center: true, color: "2E7D32" }), cell("\u2717 No (at invoice)", 2030, { center: true, color: "C62828" })] }),
            new TableRow({ children: [cell("Internal Transfer", 2500, { bold: true, shading: "FFF9C4" }), cell("Between warehouses/locations", 2800, { shading: "FFF9C4" }), cell("\u2713 Yes", 2030, { center: true, color: "2E7D32", shading: "FFF9C4" }), cell("\u2717 No (closing)", 2030, { center: true, color: "C62828", shading: "FFF9C4" })] }),
            new TableRow({ children: [cell("Scrap", 2500, { bold: true }), cell("Damaged/expired goods written off", 2800), cell("\u2713 Yes", 2030, { center: true, color: "2E7D32" }), cell("\u2717 No (closing)", 2030, { center: true, color: "C62828" })] }),
            new TableRow({ children: [cell("Mfg \u2014 Consume", 2500, { bold: true }), cell("Raw materials consumed", 2800), cell("\u2713 Yes", 2030, { center: true, color: "2E7D32" }), cell("\u2717 No (closing)", 2030, { center: true, color: "C62828" })] }),
            new TableRow({ children: [cell("Mfg \u2014 Produce", 2500, { bold: true }), cell("Finished goods produced", 2800), cell("\u2713 Yes", 2030, { center: true, color: "2E7D32" }), cell("\u2717 No (closing)", 2030, { center: true, color: "C62828" })] }),
            new TableRow({ children: [cell("Inventory Adjustment", 2500, { bold: true }), cell("Physical count corrections (+/-)", 2800), cell("\u2713 Yes", 2030, { center: true, color: "2E7D32" }), cell("\u2717 No (closing)", 2030, { center: true, color: "C62828" })] }),
            new TableRow({ children: [cell("Customer Return", 2500, { bold: true }), cell("Customer returns goods back", 2800), cell("\u2713 Yes", 2030, { center: true, color: "2E7D32" }), cell("\u2717 No (closing)", 2030, { center: true, color: "C62828" })] }),
            new TableRow({ children: [cell("Vendor Return", 2500, { bold: true }), cell("Sending goods back to vendor", 2800), cell("\u2713 Yes", 2030, { center: true, color: "2E7D32" }), cell("\u2717 No (closing)", 2030, { center: true, color: "C62828" })] }),
            new TableRow({ children: [cell("Dropship", 2500, { bold: true }), cell("Direct vendor-to-customer", 2800), cell("\u2713 Yes", 2030, { center: true, color: "2E7D32" }), cell("\u2717 No (closing)", 2030, { center: true, color: "C62828" })] }),
          ],
        }),
        spacer(),
        para([
          { text: "Important: ", bold: true, color: "C62828" },
          { text: "All of the above only applies to Perpetual (Automated) inventory valuation. For Periodic valuation, automatic journal entries for stock moves were NEVER created in any Odoo version." },
        ]),
        spacer(),
        new Paragraph({ children: [new PageBreak()] }),

        // ─── SECTION 6: CLOSING ENTRY ───
        heading1("6. The Closing Entry: What It Is & How to Do It"),
        spacer(),

        heading2("6.1 What is the Closing Entry?"),
        para("The closing entry is a single journal entry that bridges the gap between:"),
        bulletItem([{ text: "What the Inventory app says ", bold: true }, { text: "your stock is worth (based on receipts, deliveries, transfers, scrap, etc.)" }], "bullets2"),
        bulletItem([{ text: "What the Accounting app has recorded ", bold: true }, { text: "(based on invoices and bills)" }], "bullets2"),
        spacer(),
        para("Think of it as a reconciliation between inventory value and accounting value."),
        spacer(),

        heading2("6.2 What the Closing Entry Captures"),
        new Table({
          width: { size: CONTENT_WIDTH, type: WidthType.DXA },
          columnWidths: [3500, 5860],
          rows: [
            new TableRow({ children: [headerCell("Gap Type", 3500), headerCell("Meaning", 5860)] }),
            new TableRow({ children: [cell("Bills to Receive", 3500, { bold: true }), cell("Goods received but vendor bill not yet received", 5860)] }),
            new TableRow({ children: [cell("Invoices to Issue", 3500, { bold: true }), cell("Goods delivered but customer not yet invoiced", 5860)] }),
            new TableRow({ children: [cell("Billed Not Received", 3500, { bold: true }), cell("Vendor billed you but goods have not arrived", 5860)] }),
            new TableRow({ children: [cell("Invoiced Not Delivered", 3500, { bold: true }), cell("Customer invoiced but goods not yet shipped", 5860)] }),
            new TableRow({ children: [cell("Deferred Revenues", 3500, { bold: true }), cell("Revenue received in advance of delivery", 5860)] }),
            new TableRow({ children: [cell("Prepaid Expenses", 3500, { bold: true }), cell("Expenses paid in advance of receiving goods", 5860)] }),
            new TableRow({ children: [cell("Scrap / Adjustments / Transfers", 3500, { bold: true }), cell("Any inventory value changes not tied to an invoice or bill", 5860)] }),
          ],
        }),
        spacer(),

        heading2("6.3 How to Generate the Closing Entry in Odoo 19"),
        spacer(),
        heading3("Step 1: Navigate to Inventory Valuation Review"),
        para([{ text: "Path: ", bold: true }, { text: "Accounting \u2192 Review \u2192 Inventory Valuation" }]),
        para("This screen shows the difference between the accounting stock value and the current inventory value recorded by incoming moves with remaining quantity."),
        spacer(),

        heading3("Step 2: Generate the Entry"),
        para([{ text: "Click the ", bold: false }, { text: "\"Generate Entry\"", bold: true }, { text: " button. This creates a draft journal entry that accounts for the difference between inventory value and accounting value." }]),
        spacer(),

        heading3("Step 3: Review and Post"),
        para("Review the draft journal entry, verify the amounts, and then post it. Once posted, the accounting records are in sync with inventory."),
        spacer(),

        heading3("Step 4 (Optional): Accrual Entries"),
        para([{ text: "Path: ", bold: true }, { text: "Accounting \u2192 Review" }]),
        para("Check these sub-menus for more granular accruals:"),
        bulletItem("Bill To Receive", "bullets3"),
        bulletItem("Invoices To Be Issued", "bullets3"),
        bulletItem("Billed Not Received", "bullets3"),
        bulletItem("Invoiced Not Delivered", "bullets3"),
        para("Select the relevant lines and click \"Create Accrual Entries\"."),
        spacer(),

        heading2("6.4 How Often to Do It"),
        new Table({
          width: { size: CONTENT_WIDTH, type: WidthType.DXA },
          columnWidths: [3120, 6240],
          rows: [
            new TableRow({ children: [headerCell("Company Size", 3120), headerCell("Recommended Frequency", 6240)] }),
            new TableRow({ children: [cell("SMEs", 3120, { bold: true }), cell("Once a year (at year-end closing)", 6240)] }),
            new TableRow({ children: [cell("Larger companies", 3120, { bold: true }), cell("Once a month (monthly closing)", 6240)] }),
          ],
        }),
        spacer(),
        calloutBox("Odoo 19 Improvement", [
          "In Odoo 18, closing was MANUAL only. In Odoo 19, it is AUTOMATED \u2014 Odoo can generate the closing entry for you from the Accounting \u2192 Review \u2192 Inventory Valuation screen."
        ]),
        spacer(),
        new Paragraph({ children: [new PageBreak()] }),

        // ─── SECTION 7: LIVE TEST RESULTS ───
        heading1("7. Live API Test Results"),
        para("We conducted comprehensive testing on the live client database (client-cient.odoo.com, Odoo 19 / saas-19.1+e) using XML-RPC API to verify the journal entry behavior for internal transfers."),
        spacer(),

        heading2("7.1 Test Configuration"),
        para("Four test product categories were created to cover all costing method + valuation method combinations:"),

        new Table({
          width: { size: CONTENT_WIDTH, type: WidthType.DXA },
          columnWidths: [1200, 3000, 2580, 2580],
          rows: [
            new TableRow({ children: [headerCell("Cat ID", 1200), headerCell("Name", 3000), headerCell("Valuation", 2580), headerCell("Costing", 2580)] }),
            new TableRow({ children: [cell("37", 1200, { center: true }), cell("TEST-Periodic-Std", 3000), cell("Periodic", 2580, { center: true }), cell("Standard", 2580, { center: true })] }),
            new TableRow({ children: [cell("38", 1200, { center: true }), cell("TEST-Perpetual-Std", 3000), cell("Perpetual", 2580, { center: true }), cell("Standard", 2580, { center: true })] }),
            new TableRow({ children: [cell("39", 1200, { center: true }), cell("TEST-Perpetual-AVCO", 3000), cell("Perpetual", 2580, { center: true }), cell("AVCO", 2580, { center: true })] }),
            new TableRow({ children: [cell("40", 1200, { center: true }), cell("TEST-Perpetual-FIFO", 3000), cell("Perpetual", 2580, { center: true }), cell("FIFO", 2580, { center: true })] }),
          ],
        }),
        spacer(),

        para("Four test storable products were created (IDs 109\u2013112), one for each category. Initial stock of 100 units was set via inventory adjustment."),
        spacer(),

        heading2("7.2 Test Execution"),
        para("8 internal transfers were executed (4 costing configs \u00d7 2 transfer types):"),
        bulletItem("Intra-company: KG main warehouse \u2192 Devika branch warehouse (within same parent company)"),
        bulletItem("Inter-company: KG warehouse \u2192 KFURN warehouse (separate standalone company)"),
        spacer(),

        heading2("7.3 Results"),
        spacer(),
        calloutBox("Result: ZERO Journal Entries Created", [
          "Before transfers: 65 total journal entries in database",
          "After all 8 transfers completed: 65 total journal entries (no change)",
          "Stock Journal (STJ) entries before: 0 | After: 0",
          "Stock moves linked to journal entries before: 0 | After: 0",
          "",
          "All 8 transfers completed successfully (state = 'done'), inventory quantities updated correctly, but ZERO journal entries were generated."
        ]),
        spacer(),
        new Paragraph({ children: [new PageBreak()] }),

        // ─── SECTION 8: VISUAL FLOW COMPARISON ───
        heading1("8. Visual Flow: Odoo 18 vs Odoo 19"),
        spacer(),

        heading2("8.1 Odoo 18 Flow (Perpetual Valuation)"),
        para("Every stock move triggered an automatic journal entry:"),
        spacer(),
        new Table({
          width: { size: CONTENT_WIDTH, type: WidthType.DXA },
          columnWidths: [4680, 4680],
          rows: [
            new TableRow({ children: [headerCell("Event", 4680), headerCell("Journal Entry?", 4680)] }),
            new TableRow({ children: [cell("Receipt (goods in)", 4680), cell("\u2713 JE created automatically", 4680, { color: "2E7D32", bold: true })] }),
            new TableRow({ children: [cell("Delivery (goods out)", 4680), cell("\u2713 JE created automatically", 4680, { color: "2E7D32", bold: true })] }),
            new TableRow({ children: [cell("Internal Transfer", 4680), cell("\u2713 JE created automatically", 4680, { color: "2E7D32", bold: true })] }),
            new TableRow({ children: [cell("Scrap", 4680), cell("\u2713 JE created automatically", 4680, { color: "2E7D32", bold: true })] }),
            new TableRow({ children: [cell("Manufacturing", 4680), cell("\u2713 JE created automatically", 4680, { color: "2E7D32", bold: true })] }),
            new TableRow({ children: [cell("Invoice / Bill", 4680), cell("\u2713 JE created automatically", 4680, { color: "2E7D32", bold: true })] }),
            new TableRow({ children: [cell("TOTAL RESULT:", 4680, { bold: true, shading: "F5F5F5" }), cell("MANY journal entries (slower, cluttered ledger)", 4680, { bold: true, color: "C62828", shading: "F5F5F5" })] }),
          ],
        }),
        spacer(),

        heading2("8.2 Odoo 19 Flow (Perpetual Valuation)"),
        para("Only invoices/bills and the closing entry create journal entries:"),
        spacer(),
        new Table({
          width: { size: CONTENT_WIDTH, type: WidthType.DXA },
          columnWidths: [4680, 4680],
          rows: [
            new TableRow({ children: [headerCell("Event", 4680), headerCell("Journal Entry?", 4680)] }),
            new TableRow({ children: [cell("Receipt (goods in)", 4680), cell("\u2717 NO journal entry", 4680, { color: "C62828" })] }),
            new TableRow({ children: [cell("Delivery (goods out)", 4680), cell("\u2717 NO journal entry", 4680, { color: "C62828" })] }),
            new TableRow({ children: [cell("Internal Transfer", 4680), cell("\u2717 NO journal entry", 4680, { color: "C62828" })] }),
            new TableRow({ children: [cell("Scrap", 4680), cell("\u2717 NO journal entry", 4680, { color: "C62828" })] }),
            new TableRow({ children: [cell("Manufacturing", 4680), cell("\u2717 NO journal entry", 4680, { color: "C62828" })] }),
            new TableRow({ children: [cell("Invoice / Bill", 4680, { shading: "E8F5E9" }), cell("\u2713 JE created at invoice/bill level", 4680, { color: "2E7D32", bold: true, shading: "E8F5E9" })] }),
            new TableRow({ children: [cell("Closing Entry", 4680, { shading: "E8F5E9" }), cell("\u2713 ONE JE capturing all gaps", 4680, { color: "2E7D32", bold: true, shading: "E8F5E9" })] }),
            new TableRow({ children: [cell("TOTAL RESULT:", 4680, { bold: true, shading: "F5F5F5" }), cell("FEWER entries (faster, cleaner ledger)", 4680, { bold: true, color: "2E7D32", shading: "F5F5F5" })] }),
          ],
        }),
        spacer(),
        new Paragraph({ children: [new PageBreak()] }),

        // ─── SECTION 9: OFFICIAL SOURCES ───
        heading1("9. Official Source References"),
        para("The following official Odoo documentation sources confirm the findings in this document:"),
        spacer(),

        heading2("9.1 Odoo 19 \u2014 Valuation Cheat Sheet"),
        para([
          { text: "URL: " },
        ]),
        new Paragraph({
          spacing: { after: 80 },
          children: [new ExternalHyperlink({
            children: [new TextRun({ text: "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/inventory_valuation/cheat_sheet.html", style: "Hyperlink", font: "Arial", size: 19 })],
            link: "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/inventory_valuation/cheat_sheet.html",
          })],
        }),
        para([{ text: "Key section: ", bold: true }, { text: "\"Changes in Odoo 19\" (at the bottom of the page)" }]),
        para([{ text: "Direct anchor link: " }]),
        new Paragraph({
          spacing: { after: 160 },
          children: [new ExternalHyperlink({
            children: [new TextRun({ text: "https://www.odoo.com/documentation/19.0/.../cheat_sheet.html#changes-in-odoo-19", style: "Hyperlink", font: "Arial", size: 19 })],
            link: "https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/inventory_valuation/cheat_sheet.html#changes-in-odoo-19",
          })],
        }),
        spacer(),
        para([{ text: "Key quotes from this page:", bold: true }]),
        calloutBox("Quote 1", [
          "\"Before Odoo 19, the Perpetual accounting method was implemented by posting real-time accounting entries at each stock movement. That created a lot of journal items in accounting, which was an issue for performance, general ledger clarity and auditability.\""
        ]),
        spacer(),
        calloutBox("Quote 2 (Comparison Table)", [
          "Perpetual Entries: Odoo 18 = \"Invoices + every moves\" \u2192 Odoo 19 = \"Invoices + one closing\""
        ]),
        spacer(),

        heading2("9.2 Odoo 18 \u2014 Automatic Inventory Valuation Configuration"),
        para([
          { text: "URL: " },
        ]),
        new Paragraph({
          spacing: { after: 80 },
          children: [new ExternalHyperlink({
            children: [new TextRun({ text: "https://www.odoo.com/documentation/18.0/.../inventory_valuation_config.html", style: "Hyperlink", font: "Arial", size: 19 })],
            link: "https://www.odoo.com/documentation/18.0/applications/inventory_and_mrp/inventory/product_management/inventory_valuation/inventory_valuation_config.html",
          })],
        }),
        spacer(),
        para([{ text: "Key quotes from this page:", bold: true }]),
        calloutBox("Quote 3", [
          "\"perpetual (automatic) inventory valuation creates real-time journal entries in the Accounting app whenever stock enters or leaves the company's warehouse.\""
        ]),
        spacer(),
        calloutBox("Quote 4", [
          "\"each new stock move layer (SVL), that is created during inventory valuation updates, generates a journal entry.\""
        ]),
        spacer(),
        calloutBox("Quote 5", [
          "\"counterpart journal items for all incoming stock moves will be posted in this [Stock Input] account\"",
          "\"counterpart journal items for all outgoing stock moves will be posted in this [Stock Output] account\""
        ]),
        spacer(),
        new Paragraph({ children: [new PageBreak()] }),

        // ─── SECTION 10: FAQ ───
        heading1("10. Frequently Asked Questions"),
        spacer(),

        heading3("Q1: Why are no journal entries created when I do an internal transfer?"),
        para([{ text: "A: ", bold: true }, { text: "This is the expected behavior in Odoo 19. Journal entries for stock moves (including internal transfers) are no longer created automatically. The impact on accounting is captured through the Closing Entry instead. Go to Accounting \u2192 Review \u2192 Inventory Valuation \u2192 Generate Entry." }]),
        spacer(),

        heading3("Q2: Does this mean my inventory value is wrong?"),
        para([{ text: "A: ", bold: true }, { text: "No. The Inventory app still tracks values in real time. The quantities and values update correctly when you do transfers. It is only the Accounting app (journal entries) that does not update per-move anymore. The closing entry reconciles the two." }]),
        spacer(),

        heading3("Q3: Is this a bug?"),
        para([{ text: "A: ", bold: true }, { text: "No. This is an intentional architectural change by Odoo SA. The official documentation has a dedicated \"Changes in Odoo 19\" section explaining why this change was made (performance, general ledger clarity, auditability)." }]),
        spacer(),

        heading3("Q4: We are using Periodic valuation. Should we switch to Perpetual?"),
        para([{ text: "A: ", bold: true }, { text: "That depends on your accounting needs. With Periodic, you were never getting automatic JEs for stock moves anyway (in any Odoo version). Perpetual gives you JEs at the invoice/bill level + closing entry. Consult your accountant before changing valuation methods, as switching can cause discrepancies." }]),
        spacer(),

        heading3("Q5: How do I see the impact of internal transfers in accounting?"),
        para([{ text: "A: ", bold: true }, { text: "Go to Accounting \u2192 Review \u2192 Inventory Valuation. The difference shown there includes the impact of all stock moves (including internal transfers). Click \"Generate Entry\" to create the accounting entry." }]),
        spacer(),

        heading3("Q6: What was the problem with the old approach in Odoo 18?"),
        para([{ text: "A: ", bold: true }, { text: "Every stock move created journal entries, causing: (1) too many journal items cluttering the general ledger, (2) slower system performance, (3) harder auditability. A busy warehouse doing 100 transfers/day would create hundreds of journal entries that made the accounting ledger unreadable." }]),
        spacer(),
        new Paragraph({ children: [new PageBreak()] }),

        // ─── SECTION 11: SUMMARY FOR MANAGEMENT ───
        heading1("11. Summary for Management"),
        spacer(),
        calloutBox("Executive Brief", [
          "In Odoo 18, the Perpetual (Automated) valuation method created a journal entry for every stock move \u2014 receipts, deliveries, internal transfers, scrap, manufacturing, adjustments, everything.",
          "",
          "Odoo 19 changed this architecture entirely. Journal entries are now created only at the invoice/bill level, and everything else (including internal transfers) is captured in a single closing entry.",
          "",
          "This is documented in the official \"Changes in Odoo 19\" section of the Valuation Cheat Sheet on odoo.com.",
          "",
          "Our live testing on the client database confirmed this: we tested all 4 costing methods \u00d7 2 transfer types = 8 combinations, and zero journal entries were created for any internal transfer.",
          "",
          "The inventory values DO update correctly in the Inventory app. The accounting impact is captured when you run the Closing Entry from Accounting \u2192 Review \u2192 Inventory Valuation \u2192 Generate Entry.",
          "",
          "This is not a bug \u2014 it is an intentional redesign for better performance and cleaner accounting."
        ]),
        spacer(), spacer(),

        // ─── DOCUMENT INFO ───
        new Paragraph({ border: { top: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC", space: 8 } }, spacing: { before: 300, after: 60 }, children: [new TextRun({ text: "Document Information", font: "Arial", size: 18, bold: true, color: "999999" })] }),
        para([{ text: "Version: ", color: "999999", size: 18 }, { text: "1.0", color: "999999", size: 18 }]),
        para([{ text: "Author: ", color: "999999", size: 18 }, { text: "Rohan Raj, Business Analyst Intern, Infintor Solutions", color: "999999", size: 18 }]),
        para([{ text: "Date: ", color: "999999", size: 18 }, { text: "March 3, 2026", color: "999999", size: 18 }]),
        para([{ text: "Odoo Version: ", color: "999999", size: 18 }, { text: "19.0 (saas-19.1+e)", color: "999999", size: 18 }]),
        para([{ text: "Client Database: ", color: "999999", size: 18 }, { text: "client-cient.odoo.com", color: "999999", size: 18 }]),
        para([{ text: "Sources: ", color: "999999", size: 18 }, { text: "Official Odoo Documentation (19.0 & 18.0) + Live API Testing", color: "999999", size: 18 }]),
      ],
    },
  ],
});

// ─── Write ───
const OUTPUT = "c:\\Odoo Study\\My learnings\\Inventory_Valuation_Internal_Transfer_JE_Guide_Odoo19.docx";
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(OUTPUT, buffer);
  console.log(`Created: ${OUTPUT}`);
  console.log(`Size: ${(buffer.length / 1024).toFixed(1)} KB`);
}).catch(err => {
  console.error("Error:", err.message);
  process.exit(1);
});
