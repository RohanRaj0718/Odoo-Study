const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak, LevelFormat } = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const headerBorder = { style: BorderStyle.SINGLE, size: 1, color: "1B4F72" };
const headerBorders = { top: headerBorder, bottom: headerBorder, left: headerBorder, right: headerBorder };
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };

function headerCell(text, width) {
  return new TableCell({
    borders: headerBorders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: "1B4F72", type: ShadingType.CLEAR },
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
  });
}

function dataCell(text, width, highlight) {
  return new TableCell({
    borders, width: { size: width, type: WidthType.DXA },
    shading: highlight ? { fill: "EBF5FB", type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    children: [new Paragraph({ children: [new TextRun({ text, font: "Arial", size: 20 })] })]
  });
}

function heading(text, level) {
  return new Paragraph({ heading: level, spacing: { before: 300, after: 200 },
    children: [new TextRun({ text, bold: true, font: "Arial" })]
  });
}

function para(text, opts) {
  return new Paragraph({ spacing: { after: 120 },
    children: [new TextRun({ text, font: "Arial", size: 22, ...opts })]
  });
}

function bulletItem(text, ref) {
  return new Paragraph({ numbering: { reference: ref || "bullets", level: 0 }, spacing: { after: 80 },
    children: [new TextRun({ text, font: "Arial", size: 22 })]
  });
}

// Build document
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "1B4F72" },
        paragraph: { spacing: { before: 360, after: 240 } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2E86C1" },
        paragraph: { spacing: { before: 240, after: 180 } } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "1A5276" },
        paragraph: { spacing: { before: 200, after: 120 } } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1080, bottom: 1440, left: 1080 }
      }
    },
    headers: {
      default: new Header({ children: [
        new Paragraph({ alignment: AlignmentType.RIGHT, border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "1B4F72" } },
          children: [new TextRun({ text: "Infintor Solutions  |  Co Orbit Odoo 19 Configuration Report", font: "Arial", size: 16, color: "888888", italics: true })]
        })
      ]})
    },
    footers: {
      default: new Footer({ children: [
        new Paragraph({ alignment: AlignmentType.CENTER, border: { top: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" } },
          children: [new TextRun({ text: "Page ", font: "Arial", size: 18, color: "888888" }), new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 18, color: "888888" })]
        })
      ]})
    },
    children: [
      // TITLE PAGE
      new Paragraph({ spacing: { before: 3000 } }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
        children: [new TextRun({ text: "Co Orbit", font: "Arial", size: 52, bold: true, color: "1B4F72" })]
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
        children: [new TextRun({ text: "Odoo 19 Coworking Database", font: "Arial", size: 36, color: "2E86C1" })]
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
        children: [new TextRun({ text: "Verified Configuration Report", font: "Arial", size: 32, color: "5DADE2" })]
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
        border: { top: { style: BorderStyle.SINGLE, size: 6, color: "1B4F72" } }
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
        children: [new TextRun({ text: "Prepared by: Rohan Raj", font: "Arial", size: 24 })]
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
        children: [new TextRun({ text: "Business Analyst Intern, Infintor Solutions", font: "Arial", size: 22, color: "555555" })]
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
        children: [new TextRun({ text: "Date: 23 March 2026", font: "Arial", size: 22, color: "555555" })]
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
        children: [new TextRun({ text: "Database: coworking2.odoo.com", font: "Arial", size: 22, color: "555555" })]
      }),

      // PAGE BREAK
      new Paragraph({ children: [new PageBreak()] }),

      // SECTION 1
      heading("1. Database Overview", HeadingLevel.HEADING_1),
      para("The Coworking Industry pre-configured database was selected as the ideal starting point for Co Orbit. Two additional apps (Inventory and Rental) were manually installed, and Lots & Serial Numbers tracking was enabled."),
      para("Total Installed Apps: 25", { bold: true }),

      // Installed Apps Table
      heading("Installed Apps Summary", HeadingLevel.HEADING_2),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [600, 2400, 7080],
        rows: [
          new TableRow({ children: [headerCell("#", 600), headerCell("App", 2400), headerCell("Co Orbit Purpose", 7080)] }),
          ...([
            ["1", "CRM", "Lead capture from WhatsApp, Instagram, Website"],
            ["2", "Sales", "Quotations for memberships, cabin rentals"],
            ["3", "Subscriptions", "Recurring monthly/yearly billing automation"],
            ["4", "Rental (New)", "Cabin/desk availability tracking with Gantt view"],
            ["5", "Inventory (New)", "Serial number tracking for physical spaces"],
            ["6", "Appointments", "Meeting room & shared desk booking (website)"],
            ["7", "Helpdesk", "Member maintenance/issue tickets with SLA"],
            ["8", "Website", "Promote spaces, events, online booking"],
            ["9", "Email Marketing", "Newsletters and promotional campaigns"],
            ["10", "Events", "Community networking sessions, workshops"],
            ["11", "Planning", "Staff shift scheduling (reception, housekeeping)"],
            ["12", "Sign", "Digital contract/agreement signing"],
            ["13", "Invoicing", "Invoice generation and payment tracking"],
            ["14", "Project", "Renovation & maintenance project tracking"],
          ]).map((row, i) => new TableRow({
            children: [dataCell(row[0], 600, i%2===0), dataCell(row[1], 2400, i%2===0), dataCell(row[2], 7080, i%2===0)]
          }))
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // SECTION 2
      heading("2. Rental App \u2014 Deep Dive", HeadingLevel.HEADING_1),
      
      heading("2.1 Menu Structure", HeadingLevel.HEADING_2),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [2000, 3000, 5080],
        rows: [
          new TableRow({ children: [headerCell("Menu", 2000), headerCell("Sub-menus", 3000), headerCell("Purpose", 5080)] }),
          ...([
            ["Orders", "Orders, Customers, Pickup, Return", "Full rental lifecycle management"],
            ["Schedule", "Gantt View", "Visual timeline of all rentals"],
            ["Products", "Products, Pricelists", "Define rentable items with pricing"],
            ["Reporting", "\u2014", "Revenue reports, occupancy analytics"],
            ["Configuration", "Settings, Rental Periods", "Global rental configuration"],
          ]).map((row, i) => new TableRow({
            children: [dataCell(row[0], 2000, i%2===0), dataCell(row[1], 3000, i%2===0), dataCell(row[2], 5080, i%2===0)]
          }))
        ]
      }),

      heading("2.2 Product Configuration \u2014 10-Seater Cabin (Verified)", HeadingLevel.HEADING_2),
      bulletItem("Product Name: 10-Seater Cabin"),
      bulletItem("Product Type: Goods (required for serial number tracking)"),
      bulletItem("Tracking: By Unique Serial Number"),
      bulletItem("Sales Price: \u20B9 50,000.00 per rental period"),
      bulletItem("Can Be Rented: Yes (auto-enabled in Rental app)"),

      heading("2.3 Serial Numbers Created", HeadingLevel.HEADING_2),
      bulletItem("Cabin-01 \u2192 Rented to Azure Interior (S00005)"),
      bulletItem("Cabin-02 \u2192 Available"),
      bulletItem("Cabin-03 \u2192 Available"),

      heading("2.4 Rental Order Workflow (Verified End-to-End)", HeadingLevel.HEADING_2),
      para("Test Order: S00005", { bold: true }),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [800, 4000, 5280],
        rows: [
          new TableRow({ children: [headerCell("Step", 800), headerCell("Action", 4000), headerCell("Result", 5280)] }),
          ...([
            ["1", "Create New Rental Order", "Quotation created"],
            ["2", "Set Customer to Azure Interior", "Customer assigned"],
            ["3", "Add 10-Seater Cabin product", "Product added to order lines"],
            ["4", "Set period: 23/03 \u2192 23/04/2026", "31-day rental period set"],
            ["5", "Confirm Order", "Status \u2192 Sales Order"],
            ["6", "Click Pickup", "Pickup wizard opens"],
            ["7", "Select Serial: Cabin-01", "Cabin-01 assigned to order"],
            ["8", "Validate Pickup", "Status \u2192 Picked-up"],
            ["9", "Total Amount", "\u20B9 50,000.00"],
            ["10", "Create Invoice", "Available for immediate billing"],
          ]).map((row, i) => new TableRow({
            children: [dataCell(row[0], 800, i%2===0), dataCell(row[1], 4000, i%2===0), dataCell(row[2], 5280, i%2===0)]
          }))
        ]
      }),

      heading("2.5 Gantt Schedule View", HeadingLevel.HEADING_2),
      para("The Schedule view displays a timeline Gantt chart showing all active and upcoming rentals. Each product row shows occupancy bars with customer names and order numbers. This is the exact availability dashboard Co Orbit needs to see which cabins are free or occupied."),

      new Paragraph({ children: [new PageBreak()] }),

      // SECTION 3
      heading("3. Subscriptions App", HeadingLevel.HEADING_1),
      para("Pre-configured with Monthly and Yearly recurring plans. Ideal for long-term cabin leases and recurring membership billing."),
      bulletItem("Monthly Plan: Auto-generates invoices every month"),
      bulletItem("Yearly Plan: Auto-generates invoices every year"),
      bulletItem("Demo subscriptions active: Second Company (Monthly, \u20B92,000) and Fourth Company (Yearly, \u20B91,000)"),
      
      heading("Important Discovery", HeadingLevel.HEADING_2),
      para("A product cannot be both a Rental and Subscription product simultaneously in Odoo 19. Recommended architecture:", { bold: true }),
      bulletItem("Short-term cabin rental (daily/weekly) \u2192 Rental App"),
      bulletItem("Long-term cabin lease (monthly recurring) \u2192 Subscriptions App"),
      bulletItem("Meeting room booking (hourly) \u2192 Appointments App"),
      bulletItem("Hot desk / day pass \u2192 Sales or Rental App"),

      // SECTION 4
      heading("4. Appointments App", HeadingLevel.HEADING_1),
      para("Pre-configured with three appointment types for coworking operations:"),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [2500, 1500, 3080, 3000],
        rows: [
          new TableRow({ children: [headerCell("Type", 2500), headerCell("Duration", 1500), headerCell("Resources", 3080), headerCell("Status", 3000)] }),
          ...([
            ["Shared Desk", "8 hours", "Seat 3, Seat 4, +2 more", "Published"],
            ["Free Tour", "1 hour", "Staff member", "Published"],
            ["Meeting Room", "1 hour", "Meeting Room 3, 4, +2 more", "Published"],
          ]).map((row, i) => new TableRow({
            children: [dataCell(row[0], 2500, i%2===0), dataCell(row[1], 1500, i%2===0), dataCell(row[2], 3080, i%2===0), dataCell(row[3], 3000, i%2===0)]
          }))
        ]
      }),
      para("For Co Orbit: Change Meeting Room duration to 30 minutes, add per-booking pricing, and publish on website for self-service."),

      // SECTION 5
      heading("5. Helpdesk App", HeadingLevel.HEADING_1),
      para("Pre-configured with a support team (WeWork WeCare) with SLA tracking. Dashboard shows ticket volume, priority distribution, and performance metrics."),
      bulletItem("Open Tickets: 10 | High Priority: 3 | Urgent: 2"),
      bulletItem("SLA Success Rate: 50% (demo data)"),
      bulletItem("For Co Orbit: Rename to 'Co Orbit Support', add categories (AC, WiFi, Housekeeping, Parking)"),

      new Paragraph({ children: [new PageBreak()] }),

      // SECTION 6
      heading("6. No-Code vs. Customization Matrix", HeadingLevel.HEADING_1),
      heading("Works Out of the Box", HeadingLevel.HEADING_2),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [4000, 4080, 2000],
        rows: [
          new TableRow({ children: [headerCell("Requirement", 4000), headerCell("Odoo Solution", 4080), headerCell("Custom?", 2000)] }),
          ...([
            ["Track cabin occupancy", "Rental + Serial Numbers", "No"],
            ["Gantt availability chart", "Rental \u2192 Schedule", "No"],
            ["Monthly recurring invoicing", "Subscriptions", "No"],
            ["Meeting room self-booking", "Appointments + Website", "No"],
            ["Lead management", "CRM + Website", "No"],
            ["Maintenance tickets", "Helpdesk", "No"],
            ["Digital contracts", "Sign", "No"],
            ["Staff scheduling", "Planning", "No"],
          ]).map((row, i) => new TableRow({
            children: [dataCell(row[0], 4000, i%2===0), dataCell(row[1], 4080, i%2===0), dataCell(row[2], 2000, i%2===0)]
          }))
        ]
      }),

      heading("Requires Customization", HeadingLevel.HEADING_2),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [3500, 3580, 3000],
        rows: [
          new TableRow({ children: [headerCell("Requirement", 3500), headerCell("Solution", 3580), headerCell("Type", 3000)] }),
          ...([
            ["2D Floor Plan visual map", "Custom web widget", "Custom Code"],
            ["Floor/Building fields", "Add fields to products", "Odoo Studio"],
            ["Meeting room credit wallet", "Credit tracking module", "Studio + Code"],
            ["Move-in \u2260 billing start", "Override invoice trigger", "Odoo Studio"],
            ["Access control integration", "API integration", "Custom Code"],
          ]).map((row, i) => new TableRow({
            children: [dataCell(row[0], 3500, i%2===0), dataCell(row[1], 3580, i%2===0), dataCell(row[2], 3000, i%2===0)]
          }))
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // SECTION 7
      heading("7. Key Takeaways for Client Pitch", HeadingLevel.HEADING_1),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 100 },
        children: [new TextRun({ text: "Zero-code availability dashboard: ", font: "Arial", size: 22, bold: true }),
                   new TextRun({ text: "Rental Schedule Gantt chart shows exactly which cabin is free or occupied.", font: "Arial", size: 22 })]
      }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 100 },
        children: [new TextRun({ text: "Individual unit tracking: ", font: "Arial", size: 22, bold: true }),
                   new TextRun({ text: "Each cabin has a unique serial number. You know who is in Cabin-01 vs Cabin-03.", font: "Arial", size: 22 })]
      }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 100 },
        children: [new TextRun({ text: "Automated monthly billing: ", font: "Arial", size: 22, bold: true }),
                   new TextRun({ text: "Subscriptions auto-generates invoices. No manual creation.", font: "Arial", size: 22 })]
      }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 100 },
        children: [new TextRun({ text: "Self-service booking: ", font: "Arial", size: 22, bold: true }),
                   new TextRun({ text: "Members book meeting rooms and shared desks from the website.", font: "Arial", size: 22 })]
      }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 100 },
        children: [new TextRun({ text: "Integrated support: ", font: "Arial", size: 22, bold: true }),
                   new TextRun({ text: "Helpdesk with SLA tracking replaces manual WhatsApp complaint management.", font: "Arial", size: 22 })]
      }),
      new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 100 },
        children: [new TextRun({ text: "Everything in one system: ", font: "Arial", size: 22, bold: true }),
                   new TextRun({ text: "CRM \u2192 Sales \u2192 Rental \u2192 Invoicing \u2192 Helpdesk. No more switching between Engage and Excel.", font: "Arial", size: 22 })]
      }),

      new Paragraph({ spacing: { before: 600 }, border: { top: { style: BorderStyle.SINGLE, size: 4, color: "1B4F72" } } }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 },
        children: [new TextRun({ text: "End of Report", font: "Arial", size: 20, color: "888888", italics: true })]
      }),
    ]
  }]
});

const outputPath = "c:/Odoo Study/My learnings/Blogs InDevelopment/CoOrbit_Rental_Verification_Report.docx";
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputPath, buffer);
  console.log("DOCX generated: " + outputPath);
}).catch(err => console.error("Error:", err));
