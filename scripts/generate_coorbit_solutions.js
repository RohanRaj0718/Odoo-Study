const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
        ShadingType, PageNumber, PageBreak, LevelFormat } = require('docx');
const fs = require('fs');

// ─── STYLE HELPERS ────────────────────────────────────────────────
const B = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
const borders = { top: B, bottom: B, left: B, right: B };
const HB = { style: BorderStyle.SINGLE, size: 1, color: "1B4F72" };
const hBorders = { top: HB, bottom: HB, left: HB, right: HB };
const cm = { top: 60, bottom: 60, left: 100, right: 100 };

const hCell = (t, w) => new TableCell({
  borders: hBorders, width: { size: w, type: WidthType.DXA },
  shading: { fill: "1B4F72", type: ShadingType.CLEAR }, margins: cm,
  children: [new Paragraph({ children: [new TextRun({ text: t, bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })]
});
const dCell = (t, w, alt) => new TableCell({
  borders, width: { size: w, type: WidthType.DXA },
  shading: alt ? { fill: "EBF5FB", type: ShadingType.CLEAR } : undefined, margins: cm,
  children: [new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: t, font: "Arial", size: 20 })] })]
});
const greenCell = (t, w) => new TableCell({
  borders, width: { size: w, type: WidthType.DXA },
  shading: { fill: "E8F6E8", type: ShadingType.CLEAR }, margins: cm,
  children: [new Paragraph({ children: [new TextRun({ text: t, font: "Arial", size: 20, color: "1A7A1A" })] })]
});
const orangeCell = (t, w) => new TableCell({
  borders, width: { size: w, type: WidthType.DXA },
  shading: { fill: "FFF3E0", type: ShadingType.CLEAR }, margins: cm,
  children: [new Paragraph({ children: [new TextRun({ text: t, font: "Arial", size: 20, color: "E65100" })] })]
});

const h1 = t => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 240 },
  children: [new TextRun({ text: t, bold: true, font: "Arial" })] });
const h2 = t => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 180 },
  children: [new TextRun({ text: t, bold: true, font: "Arial" })] });
const h3 = t => new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 120 },
  children: [new TextRun({ text: t, bold: true, font: "Arial" })] });
const p = (t, o) => new Paragraph({ spacing: { after: 120 },
  children: [new TextRun({ text: t, font: "Arial", size: 22, ...o })] });
const bp = t => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 80 },
  children: [new TextRun({ text: t, font: "Arial", size: 22 })] });
const np = t => new Paragraph({ numbering: { reference: "num", level: 0 }, spacing: { after: 80 },
  children: [new TextRun({ text: t, font: "Arial", size: 22 })] });
const boldP = (label, text) => new Paragraph({ spacing: { after: 100 },
  children: [new TextRun({ text: label, font: "Arial", size: 22, bold: true }),
             new TextRun({ text, font: "Arial", size: 22 })] });
const PB = () => new Paragraph({ children: [new PageBreak()] });

// ─── DOCUMENT ─────────────────────────────────────────────────────
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
        run: { size: 22, bold: true, font: "Arial", color: "1A5276" },
        paragraph: { spacing: { before: 200, after: 120 } } },
    ]
  },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ]},
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 } }
    },
    headers: { default: new Header({ children: [
      new Paragraph({ alignment: AlignmentType.RIGHT, border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "1B4F72" } },
        children: [new TextRun({ text: "Infintor Solutions  |  Co Orbit \u2014 Odoo 19 Solutions Document", font: "Arial", size: 16, color: "888888", italics: true })]
      })
    ]})},
    footers: { default: new Footer({ children: [
      new Paragraph({ alignment: AlignmentType.CENTER, border: { top: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" } },
        children: [new TextRun({ text: "Confidential \u2014 Infintor Solutions | Page ", font: "Arial", size: 16, color: "888888" }),
                   new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "888888" })]
      })
    ]})},
    children: [
      // ──── TITLE PAGE ────
      new Paragraph({ spacing: { before: 2500 } }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
        children: [new TextRun({ text: "Co Orbit", font: "Arial", size: 56, bold: true, color: "1B4F72" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
        children: [new TextRun({ text: "Odoo 19 Coworking Industry Database", font: "Arial", size: 32, color: "2E86C1" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
        children: [new TextRun({ text: "Client Requirements \u2194 Odoo Solutions  |  Side-by-Side", font: "Arial", size: 28, color: "5DADE2" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
        border: { top: { style: BorderStyle.SINGLE, size: 6, color: "1B4F72" } } }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
        children: [new TextRun({ text: "Prepared by: Rohan Raj, Business Analyst Intern", font: "Arial", size: 22 })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
        children: [new TextRun({ text: "Infintor Solutions, Kochi  |  23 March 2026", font: "Arial", size: 20, color: "555555" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 },
        children: [new TextRun({ text: "Database: coworking2.odoo.com", font: "Arial", size: 20, color: "555555" })] }),

      PB(),

      // ═══════ SECTION 1: SUBSCRIPTIONS vs RENTAL ═══════
      h1("1. Subscriptions App vs. Rental App \u2014 Detailed Comparison"),
      p("Both apps handle 'renting' but serve fundamentally different purposes. Understanding this distinction is critical for correctly configuring Co Orbit."),

      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [2500, 3790, 3790],
        rows: [
          new TableRow({ children: [hCell("Feature", 2500), hCell("Subscriptions App", 3790), hCell("Rental App", 3790)] }),
          ...([
            ["Purpose", "Recurring billing for memberships and long-term leases", "Short-term physical item checkout with pickup/return tracking"],
            ["Duration Model", "Recurring plans (Monthly, Yearly) \u2014 auto-renewing", "Fixed period with exact start/end dates (Hours, Days, Weeks)"],
            ["Product Type", "Service \u2014 no inventory tracking needed", "Goods \u2014 tracks physical items via Serial Numbers"],
            ["Invoicing", "AUTOMATIC: System generates invoice at start of each billing cycle", "MANUAL: Create Invoice button after pickup confirmation"],
            ["Inventory Tracking", "None \u2014 no serial numbers, no stock counts", "Full tracking: Serial Numbers, On-Hand qty, Pickup/Return status"],
            ["Status Lifecycle", "Draft \u2192 In Progress \u2192 Paused \u2192 Closed", "Quotation \u2192 Confirmed \u2192 Picked-up \u2192 Returned"],
            ["Availability View", "None \u2014 no visual availability dashboard", "Gantt Schedule \u2014 shows exactly which items are rented and when"],
            ["Auto-Renewal", "Yes \u2014 continues until manually paused/closed", "No \u2014 each rental order is a one-time transaction"],
            ["Payment Terms", "Configurable: Immediate, Net 15, Net 30, etc.", "Standard sales payment terms"],
            ["Scalability", "Handles 100s of contracts running simultaneously", "Best for tracking 10\u201350 physical assets"],
            ["Best For Co Orbit", "Monthly cabin rent (\u20B950,000/mo), desk memberships, virtual office addresses", "Short-term cabin hire (day/week), meeting equipment rental"],
          ]).map((r, i) => new TableRow({
            children: [dCell(r[0], 2500, i%2===0), dCell(r[1], 3790, i%2===0), dCell(r[2], 3790, i%2===0)]
          }))
        ]
      }),

      h2("Key Insight: When to Use Which"),
      boldP("RULE: ", "A product CANNOT be both a Subscription and Rental item simultaneously in Odoo 19."),
      p("This means Co Orbit must use separate products for recurring vs. short-term revenue streams:"),
      bp("Monthly Cabin Lease (recurring billing) \u2192 Subscriptions App"),
      bp("Daily/Weekly Cabin Rental (tracked checkout) \u2192 Rental App"),
      bp("Meeting Room Booking (hourly self-service) \u2192 Appointments App"),
      bp("Hot Desk Day Pass (one-time sale) \u2192 Sales App or Rental App"),

      PB(),

      // ═══════ SECTION 2: APPOINTMENTS DEEP DIVE ═══════
      h1("2. Appointments App \u2014 Meeting Room & Booking Deep Dive"),

      h2("2.1 Pre-Configured Appointment Types"),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [2000, 1200, 1300, 2580, 1500, 1500],
        rows: [
          new TableRow({ children: [hCell("Type", 2000), hCell("Duration", 1200), hCell("Assignment", 1300), hCell("Resources", 2580), hCell("Payment", 1500), hCell("Website", 1500)] }),
          ...([
            ["Shared Desk", "8 hours", "Automatic", "Seat 1, 2, 3, 4", "Free / Paid", "Published"],
            ["Free Tour", "1 hour", "Manual", "Staff member", "Free", "Published"],
            ["Meeting Room", "1 hour", "Manual", "Room 1, 2, 3, 4", "Free / Paid", "Published"],
          ]).map((r, i) => new TableRow({
            children: r.map((c, j) => dCell(c, [2000,1200,1300,2580,1500,1500][j], i%2===0))
          }))
        ]
      }),

      h2("2.2 Meeting Room Booking \u2014 How It Works"),
      np("Member visits the website booking page (auto-published)"),
      np("Selects 'Meeting Room' appointment type"),
      np("Chooses a specific meeting room (Manual assignment) or system picks one (Automatic)"),
      np("Selects an available time slot from the calendar"),
      np("If payment is configured: pays upfront via eCommerce checkout"),
      np("Booking confirmed \u2192 appears on the Gantt schedule for staff"),
      np("Member receives confirmation email with booking details"),

      h2("2.3 Meeting Room Configuration for Co Orbit"),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [3500, 3290, 3290],
        rows: [
          new TableRow({ children: [hCell("Setting", 3500), hCell("Current Value", 3290), hCell("Recommended for Co Orbit", 3290)] }),
          ...([
            ["Duration", "1 hour", "30 minutes (client requirement)"],
            ["Assignment Mode", "Manual (visitor chooses room)", "Keep Manual \u2014 members pick their preferred room"],
            ["Resources", "Meeting Room 1-4", "Rename to actual room names + add Conference Room"],
            ["Payment", "Not configured", "Enable Up-Front Payment + set per-slot price"],
            ["Website Visibility", "Published", "Keep Published for self-service booking"],
            ["Availability Hours", "Default working hours", "Set to Co Orbit operating hours (8 AM \u2013 8 PM)"],
            ["Cancellation Policy", "Not set", "Allow cancellation up to 2 hours before slot"],
          ]).map((r, i) => new TableRow({
            children: [dCell(r[0], 3500, i%2===0), dCell(r[1], 3290, i%2===0), dCell(r[2], 3290, i%2===0)]
          }))
        ]
      }),

      h2("2.4 Credit System \u2014 Gap Analysis"),
      p("Co Orbit currently uses a 'credits' system in Engage where each company gets X meeting room credits per month. In Odoo 19:"),
      bp("Native credit wallet: NOT available out-of-the-box"),
      bp("Workaround 1: Use Prepaid Pricelist \u2014 members buy a 'Meeting Room Credit Pack' (e.g., 10 slots), each booking deducts from the prepaid balance"),
      bp("Workaround 2: Use Odoo Studio to add a custom 'Credits Remaining' field on the company record and decrease it per booking"),
      bp("Workaround 3: Third-party module from Odoo App Store (search 'credit wallet')"),
      p("Recommendation: Start with simple per-booking payment. Add credits system in Phase 3 after initial deployment.", { italics: true }),

      PB(),

      // ═══════ SECTION 3: SIDE-BY-SIDE SOLUTIONS ═══════
      h1("3. Client Requirements \u2194 Odoo Solutions (Side-by-Side)"),

      h2("PHASE 1: Sales Automation & Lead Management"),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [900, 2700, 3490, 1500, 1490],
        rows: [
          new TableRow({ children: [hCell("#", 900), hCell("Client Requirement", 2700), hCell("Odoo Solution", 3490), hCell("App", 1500), hCell("Custom?", 1490)] }),
          ...([
            ["1.1", "WhatsApp enquiry auto-response", "CRM + WhatsApp Business connector. Auto-create lead on incoming message. Auto-reply with qualification questions.", "CRM", "Connector"],
            ["1.2", "Instagram enquiry capture", "CRM + Social Marketing. Auto-capture DMs as leads. Auto-acknowledgement.", "CRM", "Connector"],
            ["1.3", "Website enquiry form \u2192 CRM", "Website Form \u2192 auto-creates CRM lead. Captures: team size, company name, workspace type.", "Website + CRM", "No"],
            ["1.4", "Phone call \u2192 missed call \u2192 WhatsApp", "VoIP + WhatsApp connector. Log missed calls. Trigger auto-WhatsApp on missed call.", "CRM + VoIP", "Connector"],
            ["1.5", "Proposal follow-up automation", "CRM Pipeline: auto-email after 2 days, reminder after 5 days, re-engagement campaign after 3\u20136 months.", "CRM + Email", "No"],
            ["1.6", "Lead pipeline management", "CRM Kanban: New \u2192 Qualified \u2192 Tour Booked \u2192 Proposal Sent \u2192 Won/Lost", "CRM", "No"],
          ]).map((r, i) => new TableRow({
            children: [dCell(r[0], 900, i%2===0), dCell(r[1], 2700, i%2===0), dCell(r[2], 3490, i%2===0), dCell(r[3], 1500, i%2===0),
              r[4]==="No" ? greenCell(r[4], 1490) : orangeCell(r[4], 1490)]
          }))
        ]
      }),

      PB(),

      h2("PHASE 2: Operational Management (Engage Replacement)"),
      h3("A. Client Onboarding & Workspace Allocation"),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [900, 2700, 3490, 1500, 1490],
        rows: [
          new TableRow({ children: [hCell("#", 900), hCell("Client Requirement", 2700), hCell("Odoo Solution", 3490), hCell("App", 1500), hCell("Custom?", 1490)] }),
          ...([
            ["2.1", "Create company profile on join", "Contacts App: create Company record with all details. Link employees as child contacts.", "Contacts", "No"],
            ["2.2", "Contract preparation & signing", "Sign App: create lease template, send for digital e-signature. Auto-log in CRM.", "Sign", "No"],
            ["2.3", "Select workspace type (Cabin/Desk/Hot)", "Rental or Subscriptions: select product type during order creation. Each type is a separate product.", "Rental / Subs", "No"],
            ["2.4", "Cabin allocation (25 cabins with sizes)", "Inventory: create 25 Serial Numbers (Cabin-01 to Cabin-25) under cabin products (4/6/8/10-seater).", "Inventory", "No"],
            ["2.5", "View available cabin of specific size", "Rental Schedule Gantt: filter by product to see which 10-seater cabins are free.", "Rental", "No"],
            ["2.6", "Dedicated desk count tracking (7 desks)", "Inventory: set Qty On Hand = 7. Each allocation reduces count. No individual desk numbers.", "Inventory", "No"],
            ["2.7", "Hot desk (first-come-first-serve)", "No system allocation needed. Appointments App for day-pass booking.", "Appointments", "No"],
            ["2.8", "Billing starts from move-in, not contract signing", "Subscriptions: set Start Date to move-in date. Invoice generation begins from that date.", "Subscriptions", "Studio"],
          ]).map((r, i) => new TableRow({
            children: [dCell(r[0], 900, i%2===0), dCell(r[1], 2700, i%2===0), dCell(r[2], 3490, i%2===0), dCell(r[3], 1500, i%2===0),
              r[4]==="No" ? greenCell(r[4], 1490) : orangeCell(r[4], 1490)]
          }))
        ]
      }),

      h3("B. Meeting Room & Conference Room Booking"),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [900, 2700, 3490, 1500, 1490],
        rows: [
          new TableRow({ children: [hCell("#", 900), hCell("Client Requirement", 2700), hCell("Odoo Solution", 3490), hCell("App", 1500), hCell("Custom?", 1490)] }),
          ...([
            ["3.1", "Book meeting room in 30-min slots", "Appointments: set Meeting Room duration to 00:30. Members book via website.", "Appointments", "No"],
            ["3.2", "See available time slots", "Website booking page shows calendar with available slots in real-time.", "Appointments", "No"],
            ["3.3", "Book conference room separately", "Create separate 'Conference Room' appointment type with its own resources.", "Appointments", "No"],
            ["3.4", "Credit system for bookings", "Workaround: Prepaid Pack product or custom field via Odoo Studio.", "Appointments", "Studio"],
            ["3.5", "Allow booking active slots if unused", "Appointments: slot becomes bookable again if previous booking cancelled.", "Appointments", "No"],
            ["3.6", "Reception override capability", "Staff can create/edit bookings directly on Gantt schedule in backend.", "Appointments", "No"],
          ]).map((r, i) => new TableRow({
            children: [dCell(r[0], 900, i%2===0), dCell(r[1], 2700, i%2===0), dCell(r[2], 3490, i%2===0), dCell(r[3], 1500, i%2===0),
              r[4]==="No" ? greenCell(r[4], 1490) : orangeCell(r[4], 1490)]
          }))
        ]
      }),

      PB(),

      h3("C. Billing & Payment Management"),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [900, 2700, 3490, 1500, 1490],
        rows: [
          new TableRow({ children: [hCell("#", 900), hCell("Client Requirement", 2700), hCell("Odoo Solution", 3490), hCell("App", 1500), hCell("Custom?", 1490)] }),
          ...([
            ["4.1", "Auto-generate invoices on 1st of month", "Subscriptions: set invoice day to 1st. System auto-generates and sends.", "Subscriptions", "No"],
            ["4.2", "Payment via bank transfer / UPI", "Accounting: Bank Reconciliation auto-matches bank statement entries to invoices.", "Accounting", "No"],
            ["4.3", "No manual bank statement checking", "Accounting: import bank statements (OFX/CSV). Auto-reconciliation engine matches payments.", "Accounting", "No"],
            ["4.4", "Automatic payment reminders", "Accounting: Follow-up Levels. Auto-email on Day 7, 14, 30 overdue.", "Accounting", "No"],
            ["4.5", "Payment gateway integration", "eCommerce + Razorpay/PayU connector for online payments.", "Website", "Connector"],
          ]).map((r, i) => new TableRow({
            children: [dCell(r[0], 900, i%2===0), dCell(r[1], 2700, i%2===0), dCell(r[2], 3490, i%2===0), dCell(r[3], 1500, i%2===0),
              r[4]==="No" ? greenCell(r[4], 1490) : orangeCell(r[4], 1490)]
          }))
        ]
      }),

      h3("D. Access Control, Mobile App & Community"),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [900, 2700, 3490, 1500, 1490],
        rows: [
          new TableRow({ children: [hCell("#", 900), hCell("Client Requirement", 2700), hCell("Odoo Solution", 3490), hCell("App", 1500), hCell("Custom?", 1490)] }),
          ...([
            ["5.1", "Access card for entry", "API integration with existing access control hardware. Sync member status.", "Custom", "Developer"],
            ["5.2", "Auto-activate card during booking", "Connect Appointments booking event \u2192 access control API.", "Custom", "Developer"],
            ["5.3", "Mobile app for members", "Odoo Portal: members log in via browser/PWA. View invoices, bookings, tickets.", "Website Portal", "No"],
            ["5.4", "View/book meeting rooms from app", "Odoo Portal + Appointments: self-service booking from mobile browser.", "Appointments", "No"],
            ["5.5", "Member benefits display", "Website: create 'Member Benefits' page listing partner offers.", "Website", "No"],
            ["5.6", "Events listing", "Events App: create upcoming events. Members see on portal/website.", "Events", "No"],
            ["5.7", "Community feed (photos/posts)", "Discuss or Website Blog module for member community posts.", "Website Blog", "Studio"],
            ["5.8", "Issue/ticket reporting", "Helpdesk: members submit tickets via portal. Auto-assign to staff. SLA tracking.", "Helpdesk", "No"],
          ]).map((r, i) => new TableRow({
            children: [dCell(r[0], 900, i%2===0), dCell(r[1], 2700, i%2===0), dCell(r[2], 3490, i%2===0), dCell(r[3], 1500, i%2===0),
              r[4]==="No" ? greenCell(r[4], 1490) : orangeCell(r[4], 1490)]
          }))
        ]
      }),

      h3("E. Visual Floor Plan & Space Planning"),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [900, 2700, 3490, 1500, 1490],
        rows: [
          new TableRow({ children: [hCell("#", 900), hCell("Client Requirement", 2700), hCell("Odoo Solution", 3490), hCell("App", 1500), hCell("Custom?", 1490)] }),
          ...([
            ["6.1", "2D floor plan with cabin map", "Custom web widget showing office layout with live occupancy overlay.", "Custom", "Developer"],
            ["6.2", "Color-coded status (Green/Red/Yellow)", "Custom widget reads Rental/Subscription status \u2192 colors cabins.", "Custom", "Developer"],
            ["6.3", "Staff-only visibility", "Access rights: restrict floor plan view to internal users only.", "Settings", "No"],
            ["6.4", "Floor/Building fields on products", "Odoo Studio: add 'Floor' and 'Building' selection fields to Product form.", "Studio", "Studio"],
          ]).map((r, i) => new TableRow({
            children: [dCell(r[0], 900, i%2===0), dCell(r[1], 2700, i%2===0), dCell(r[2], 3490, i%2===0), dCell(r[3], 1500, i%2===0),
              r[4]==="No" ? greenCell(r[4], 1490) : orangeCell(r[4], 1490)]
          }))
        ]
      }),

      PB(),

      // ═══════ SECTION 4: SUMMARY ═══════
      h1("4. Summary: Customization Scorecard"),
      new Table({
        width: { size: 10080, type: WidthType.DXA },
        columnWidths: [3500, 2000, 2290, 2290],
        rows: [
          new TableRow({ children: [hCell("Category", 3500), hCell("Total Req.", 2000), hCell("Out-of-Box", 2290), hCell("Needs Custom", 2290)] }),
          ...([
            ["Phase 1: Sales & Lead Mgmt", "6", "2", "4 (connectors)"],
            ["Phase 2A: Onboarding & Allocation", "8", "7", "1 (Studio)"],
            ["Phase 2B: Meeting Room Booking", "6", "5", "1 (Studio)"],
            ["Phase 2C: Billing & Payment", "5", "4", "1 (connector)"],
            ["Phase 2D: Mobile/Access/Community", "8", "5", "3 (Dev/Studio)"],
            ["Phase 2E: Floor Plan", "4", "1", "3 (Dev/Studio)"],
            ["TOTAL", "37", "24 (65%)", "13 (35%)"],
          ]).map((r, i) => new TableRow({
            children: [dCell(r[0], 3500, i%2===0), dCell(r[1], 2000, i%2===0),
              greenCell(r[2], 2290), orangeCell(r[3], 2290)]
          }))
        ]
      }),

      p(""),
      boldP("Bottom Line: ", "65% of Co Orbit's requirements work out-of-the-box with the Odoo 19 Coworking Industry database. The remaining 35% are primarily third-party connectors (WhatsApp, Instagram, Razorpay) and Odoo Studio customizations \u2014 NOT custom code development. Only the Floor Plan visual widget requires actual developer involvement."),

      new Paragraph({ spacing: { before: 600 }, border: { top: { style: BorderStyle.SINGLE, size: 4, color: "1B4F72" } } }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 },
        children: [new TextRun({ text: "End of Document", font: "Arial", size: 20, color: "888888", italics: true })] }),
    ]
  }]
});

const out = "c:/Odoo Study/My learnings/Blogs InDevelopment/CoOrbit_Solutions_SideBySide.docx";
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(out, buf);
  console.log("DOCX created: " + out);
}).catch(e => console.error("Error:", e));
