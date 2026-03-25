const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat,
  HeadingLevel, BorderStyle, WidthType, ShadingType,
  PageNumber, PageBreak, TableOfContents
} = require("docx");

// ─── Constants ───
const PAGE_WIDTH = 12240;
const MARGIN = 1440;
const CW = PAGE_WIDTH - 2 * MARGIN; // 9360

// ─── Helpers ───
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const hdrBorder = { style: BorderStyle.SINGLE, size: 1, color: "1F4E79" };
const hdrBorders = { top: hdrBorder, bottom: hdrBorder, left: hdrBorder, right: hdrBorder };
const cm = { top: 80, bottom: 80, left: 120, right: 120 };

function hCell(text, w) {
  return new TableCell({ borders: hdrBorders, width: { size: w, type: WidthType.DXA }, shading: { fill: "1F4E79", type: ShadingType.CLEAR }, margins: cm, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 20 })] })] });
}
function tCell(text, w, opts = {}) {
  const runs = Array.isArray(text) ? text.map(t => new TextRun(typeof t === "string" ? { text: t, font: "Arial", size: 20, color: "333333" } : { font: "Arial", size: 20, color: "333333", ...t })) : [new TextRun({ text, font: "Arial", size: 20, color: opts.color || "333333", bold: !!opts.bold })];
  return new TableCell({ borders, width: { size: w, type: WidthType.DXA }, shading: opts.shade ? { fill: opts.shade, type: ShadingType.CLEAR } : undefined, margins: cm, children: [new Paragraph({ alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT, children: runs })] });
}
function h1(t) { return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 200 }, children: [new TextRun({ text: t, bold: true, font: "Arial", size: 32, color: "1F4E79" })] }); }
function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 160 }, children: [new TextRun({ text: t, bold: true, font: "Arial", size: 26, color: "2E75B6" })] }); }
function h3(t) { return new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 120 }, children: [new TextRun({ text: t, bold: true, font: "Arial", size: 22, color: "404040" })] }); }
function p(text, opts = {}) {
  const runs = Array.isArray(text) ? text.map(t => new TextRun(typeof t === "string" ? { text: t, font: "Arial", size: 20, color: "333333" } : { font: "Arial", size: 20, color: "333333", ...t })) : [new TextRun({ text, font: "Arial", size: 20, color: "333333" })];
  return new Paragraph({ spacing: { after: opts.after || 160 }, alignment: opts.align || AlignmentType.LEFT, children: runs });
}
function sp() { return new Paragraph({ spacing: { after: 80 }, children: [new TextRun("")] }); }

// Script dialogue line with timestamp and visual cue
function dialogueLine(timestamp, visual, narration) {
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [1100, 3130, 5130],
    rows: [new TableRow({ children: [
      tCell(timestamp, 1100, { center: true, shade: "F0F4F8", bold: true, color: "2E75B6" }),
      tCell(visual, 3130, { shade: "FFF9E6", color: "666666" }),
      tCell(narration, 5130),
    ] })],
  });
}

// Section header row for the script table
function sectionHeader(text) {
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [CW],
    rows: [new TableRow({ children: [
      new TableCell({ borders: hdrBorders, width: { size: CW, type: WidthType.DXA }, shading: { fill: "2E75B6", type: ShadingType.CLEAR }, margins: { top: 100, bottom: 100, left: 200, right: 200 }, children: [new Paragraph({ alignment: AlignmentType.LEFT, children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 22 })] })] })
    ] })],
  });
}

// Callout box
function callout(title, lines) {
  const content = [new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: title, bold: true, font: "Arial", size: 20, color: "1F4E79" })] })];
  lines.forEach(l => content.push(new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: l, font: "Arial", size: 19, color: "333333" })] })));
  return new Table({
    width: { size: CW, type: WidthType.DXA }, columnWidths: [CW],
    rows: [new TableRow({ children: [new TableCell({
      borders: { top: { style: BorderStyle.SINGLE, size: 1, color: "BDD7EE" }, bottom: { style: BorderStyle.SINGLE, size: 1, color: "BDD7EE" }, left: { style: BorderStyle.SINGLE, size: 6, color: "2E75B6" }, right: { style: BorderStyle.SINGLE, size: 1, color: "BDD7EE" } },
      width: { size: CW, type: WidthType.DXA }, shading: { fill: "EAF2FB", type: ShadingType.CLEAR }, margins: { top: 120, bottom: 120, left: 200, right: 200 }, children: content,
    })] })],
  });
}

// Bullet item
function bullet(text, ref = "bullets") {
  const runs = Array.isArray(text) ? text.map(t => new TextRun(typeof t === "string" ? { text: t, font: "Arial", size: 20, color: "333333" } : { font: "Arial", size: 20, color: "333333", ...t })) : [new TextRun({ text, font: "Arial", size: 20, color: "333333" })];
  return new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 80 }, children: runs });
}

// ─── BUILD DOCUMENT ───
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 32, bold: true, font: "Arial", color: "1F4E79" }, paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 26, bold: true, font: "Arial", color: "2E75B6" }, paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 22, bold: true, font: "Arial", color: "404040" }, paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "bullets2", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ],
  },
  sections: [
    // ═══ COVER PAGE ═══
    {
      properties: { page: { size: { width: PAGE_WIDTH, height: 15840 }, margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN } } },
      children: [
        sp(), sp(), sp(), sp(),
        p("INFINTOR SOLUTIONS", { align: AlignmentType.CENTER, after: 80 }),
        p([{ text: "Video Script & Production Guide", font: "Arial", size: 22, color: "2E75B6", bold: true }], { align: AlignmentType.CENTER, after: 200 }),
        sp(),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E75B6", space: 8 } }, children: [new TextRun({ text: "Odoo 19 Referrals App", font: "Arial", size: 48, bold: true, color: "1F4E79" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 }, children: [new TextRun({ text: "Complete Tutorial Video Script", font: "Arial", size: 36, bold: true, color: "2E75B6" })] }),
        sp(),
        p([{ text: "Gamify Your Hiring | Employee Referral Program in Odoo 19", italics: true, color: "666666", size: 22 }], { align: AlignmentType.CENTER }),
        sp(), sp(), sp(), sp(),
        p([{ text: "Prepared by: ", color: "333333" }, { text: "Rohan Raj", bold: true, color: "333333" }], { align: AlignmentType.CENTER }),
        p("Business Analyst Intern | Infintor Solutions", { align: AlignmentType.CENTER }),
        p("9th Floor, Vismaya Infopark, Kochi, Kerala 682030", { align: AlignmentType.CENTER }),
        p("Date: March 4, 2026", { align: AlignmentType.CENTER }),
        sp(), sp(),
        p([{ text: "Estimated Video Duration: 12\u201315 minutes", bold: true, color: "2E75B6", size: 22 }], { align: AlignmentType.CENTER }),
        p([{ text: "Format: Screen Recording + Voiceover Narration", color: "666666", size: 20 }], { align: AlignmentType.CENTER }),
      ],
    },
    // ═══ MAIN CONTENT ═══
    {
      properties: { page: { size: { width: PAGE_WIDTH, height: 15840 }, margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN } } },
      headers: { default: new Header({ children: [new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "2E75B6", space: 4 } }, children: [new TextRun({ text: "Infintor Solutions \u2014 Odoo 19 Referrals App | Video Script", font: "Arial", size: 16, color: "999999", italics: true })] })] }) },
      footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, border: { top: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC", space: 4 } }, children: [new TextRun({ text: "Infintor Solutions | Confidential | Page ", font: "Arial", size: 16, color: "999999" }), new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "999999" })] })] }) },
      children: [
        // ═══ TABLE OF CONTENTS ═══
        h1("Table of Contents"),
        new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 1: VIDEO OVERVIEW
        // ═══════════════════════════════════════════
        h1("1. Video Overview & Production Notes"),
        sp(),
        h2("1.1 Video Details"),
        new Table({
          width: { size: CW, type: WidthType.DXA }, columnWidths: [3000, 6360],
          rows: [
            new TableRow({ children: [hCell("Parameter", 3000), hCell("Details", 6360)] }),
            new TableRow({ children: [tCell("Title", 3000, { bold: true }), tCell("Odoo 19 Referrals App | Complete Guide | Infintor Solutions", 6360)] }),
            new TableRow({ children: [tCell("Duration", 3000, { bold: true }), tCell("12\u201315 minutes (target)", 6360)] }),
            new TableRow({ children: [tCell("Format", 3000, { bold: true }), tCell("Screen recording with voiceover narration", 6360)] }),
            new TableRow({ children: [tCell("Resolution", 3000, { bold: true }), tCell("1920\u00d71080 (Full HD)", 6360)] }),
            new TableRow({ children: [tCell("Software", 3000, { bold: true }), tCell("Odoo 19 (latest version)", 6360)] }),
            new TableRow({ children: [tCell("Target Audience", 3000, { bold: true }), tCell("HR Managers, Recruiters, Business Owners considering Odoo", 6360)] }),
            new TableRow({ children: [tCell("Tone", 3000, { bold: true }), tCell("Professional, friendly, clear \u2014 tutorial style", 6360)] }),
            new TableRow({ children: [tCell("Published By", 3000, { bold: true }), tCell("Infintor Solutions, Kochi", 6360)] }),
            new TableRow({ children: [tCell("YouTube Description", 3000, { bold: true }), tCell("See Section 11 of this document", 6360)] }),
          ],
        }),
        sp(),

        h2("1.2 Pre-Recording Checklist"),
        bullet("Odoo 19 instance ready with Referrals, Recruitment, Employees, and Website apps installed"),
        bullet("At least 2\u20133 published job positions created in Recruitment"),
        bullet("At least 2 employee users created (one as referrer, one as admin)"),
        bullet("Rewards configured (3\u20134 sample rewards with images and point costs)"),
        bullet("Browser zoom set to 100%, no browser extensions visible"),
        bullet("Clear browser bookmarks bar or hide it"),
        bullet("Use a clean, uncluttered Odoo database (no test data clutter)"),
        bullet("Microphone tested for clarity \u2014 no background noise"),
        sp(),
        callout("Recording Tip", [
          "Record in short segments (one section at a time). This makes editing easier and lets you re-record specific parts without redoing everything. Pause 2 seconds between sections for clean cuts."
        ]),
        sp(),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 2: SCRIPT FORMAT GUIDE
        // ═══════════════════════════════════════════
        h1("2. How to Read This Script"),
        sp(),
        p("The script below is organized in a three-column format:"),
        sp(),
        new Table({
          width: { size: CW, type: WidthType.DXA }, columnWidths: [1100, 3130, 5130],
          rows: [
            new TableRow({ children: [hCell("Timestamp", 1100), hCell("Visual / Screen Action", 3130), hCell("Narration (Voiceover Dialogue)", 5130)] }),
            new TableRow({ children: [
              tCell("0:00", 1100, { center: true, shade: "F0F4F8", bold: true, color: "2E75B6" }),
              tCell("What the viewer sees on screen", 3130, { shade: "FFF9E6", color: "666666" }),
              tCell("Exact words to speak in the voiceover", 5130),
            ] }),
          ],
        }),
        sp(),
        bullet([{ text: "Timestamp: ", bold: true }, { text: "Approximate time in the video. Adjust based on your actual pace." }]),
        bullet([{ text: "Visual: ", bold: true }, { text: "What you should be showing on screen at that moment (which page, which button to click, etc.)" }]),
        bullet([{ text: "Narration: ", bold: true }, { text: "The exact dialogue to speak. Read naturally \u2014 don\u2019t sound robotic. It\u2019s fine to slightly rephrase while keeping the meaning." }]),
        sp(),
        callout("Speaking Pace", [
          "Maintain a moderate pace \u2014 not too fast, not too slow. Aim for about 130\u2013150 words per minute. Pause briefly (1\u20132 seconds) after key sentences to let viewers absorb the information.",
          "When demonstrating a click, say what you\u2019re about to click BEFORE you click it. This gives viewers time to follow along."
        ]),
        sp(),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 3: INTRO SEGMENT
        // ═══════════════════════════════════════════
        h1("3. Intro & Hook (0:00 \u2013 0:45)"),
        sp(),
        sectionHeader("SEGMENT 1: INTRO & HOOK"),
        sp(),
        dialogueLine("0:00", "Infintor Solutions logo / animated intro (3\u20134 sec)", ""),
        sp(),
        dialogueLine("0:04", "Odoo 19 Referrals dashboard visible in background, slightly blurred", 
          "Hey everyone! Welcome back to Infintor Solutions. I\u2019m [Your Name], and in today\u2019s video, we\u2019re going to explore one of the most exciting yet often overlooked apps in Odoo 19 \u2014 the Referrals app."),
        sp(),
        dialogueLine("0:18", "Text overlay: \"What is the Referrals App?\"",
          "Now, if your company is struggling with hiring the right talent, or you want to motivate your employees to bring in quality candidates, this app is exactly what you need. It turns your entire employee referral program into a gamified experience \u2014 with points, levels, rewards, and even superhero avatars."),
        sp(),
        dialogueLine("0:35", "Quick montage: dashboard, rewards page, job cards (2\u20133 sec each)",
          "By the end of this video, you\u2019ll know how to set up, configure, and use the Referrals app from scratch. So, let\u2019s get started!"),
        sp(),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 4: PREREQUISITES
        // ═══════════════════════════════════════════
        h1("4. Prerequisites & Installation (0:45 \u2013 1:45)"),
        sp(),
        sectionHeader("SEGMENT 2: PREREQUISITES"),
        sp(),
        dialogueLine("0:45", "Odoo Apps store, search bar visible", 
          "Before we dive in, let me quickly tell you what you need for the Referrals app to work. You need three other apps to be installed: Employees, Recruitment, and Website. Without these three, the Referrals app won\u2019t function."),
        sp(),
        dialogueLine("1:00", "Show Apps menu \u2192 search \"Referrals\" \u2192 show Referrals app card",
          "To install the Referrals app, simply go to the Apps menu, search for \u201CReferrals\u201D, and click Install. Odoo will automatically install the required dependencies if they\u2019re not already installed."),
        sp(),
        dialogueLine("1:20", "Show main menu with Referrals icon visible",
          "Once installed, you\u2019ll see the Referrals app icon in your main menu. Now, let me also mention the access rights. There are three levels: Referral User, Officer, and Administrator. Regular employees can use the app to refer candidates and earn points. Only Administrators can access the configuration menus and reporting."),
        sp(),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 5: ONBOARDING
        // ═══════════════════════════════════════════
        h1("5. Onboarding Experience (1:45 \u2013 3:15)"),
        sp(),
        sectionHeader("SEGMENT 3: ONBOARDING"),
        sp(),
        dialogueLine("1:45", "Click on Referrals app to open it \u2192 Onboarding slide 1 appears",
          "When you open the Referrals app for the very first time, you\u2019ll be greeted with this beautiful onboarding experience. It\u2019s designed like a superhero comic strip \u2014 and it walks you through the app\u2019s concept."),
        sp(),
        dialogueLine("2:00", "Slide 1: \"OH NO! VILLAINS ARE LURKING THE CITY!\" text visible",
          "The first slide sets the scene \u2014 it says \"Oh no! Villains are lurking the city! Help us recruit a team of superheroes to save the day!\" This is Odoo\u2019s way of making the referral process feel fun and engaging for employees."),
        sp(),
        dialogueLine("2:15", "Click Next \u2192 Slide 2 appears",
          "On the second slide, it tells you to browse through open job positions, promote them on social media, or refer your friends. Let\u2019s click Next."),
        sp(),
        dialogueLine("2:25", "Click Next \u2192 Slide 3 appears",
          "Slide three explains the reward system \u2014 collect points and exchange them for awesome gifts in the shop. This is the gamification element that keeps employees motivated."),
        sp(),
        dialogueLine("2:35", "Click Next \u2192 Slide 4 appears",
          "And the final slide encourages healthy competition \u2014 compete against your colleagues to build the best team. Now let\u2019s click Start Now to enter the main dashboard."),
        sp(),
        dialogueLine("2:50", "Click \"Start Now\" \u2192 Main dashboard loads",
          "And here we are \u2014 the main Referrals dashboard! At the top, you can see your total points earned and points available to spend. Below that is your superhero avatar with your current level. We\u2019ll come back to levels in a moment."),
        sp(),
        callout("Admin Note", [
          "These onboarding slides appear every time a user opens the Referrals app until they click \"Start Now\". If they click \"Skip\", the slides will appear again next time. Once \"Start Now\" is clicked, they won\u2019t reappear.",
          "",
          "Admins can customize the onboarding slides from: Referrals \u2192 Configuration \u2192 Onboarding. You can change the text, images, and even the order of the slides."
        ]),
        sp(),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 6: VIEWING & SHARING JOBS
        // ═══════════════════════════════════════════
        h1("6. Viewing & Sharing Job Positions (3:15 \u2013 5:30)"),
        sp(),
        sectionHeader("SEGMENT 4: SHARING JOBS"),
        sp(),
        dialogueLine("3:15", "Dashboard visible, mouse hovering over \"View Jobs\" button",
          "Now let\u2019s look at the core functionality of this app \u2014 sharing job positions. From the dashboard, click the View Jobs button."),
        sp(),
        dialogueLine("3:25", "Click \"View Jobs\" \u2192 Job cards displayed",
          "This shows all currently published job positions. Each card displays the job title, the number of open positions, the total referral points you can earn if your candidate gets hired, and a brief job description."),
        sp(),
        dialogueLine("3:40", "Point to a specific job card, highlight the details",
          "For example, this position is for a Software Developer. It has 2 open positions, and the total points you can earn for a successful referral is 85 points. Now, there are multiple ways to share this job with potential candidates. Let me walk you through each one."),
        sp(),
        // Email
        dialogueLine("3:55", "Click the envelope icon (Send Email) on a job card",
          "First, you can share it via Email. Click the Send Email button. A preconfigured email template opens up. You just need to enter the recipient\u2019s email address. The subject is set to \"Job for you\" by default, and the body contains a tracking link to the job position on your company\u2019s website."),
        sp(),
        dialogueLine("4:15", "Show the email compose window, highlight the tracking link",
          "The beauty of this is that the link is a tracking link. When the person you referred clicks this link and applies, Odoo automatically tracks that the referral came from you. You can add a personal message here too, and then click Send Mail."),
        sp(),
        // SMS
        dialogueLine("4:30", "Close email, click SMS icon on a job card",
          "The second option is Send SMS. This opens a similar window where you enter the recipient\u2019s mobile number and send a text message with the job link. Do note that SMS requires IAP credits in Odoo, which need to be purchased separately."),
        sp(),
        // WhatsApp
        dialogueLine("4:45", "Close SMS, click WhatsApp icon on a job card",
          "Third, you have Send WhatsApp. This works the same way but sends the message via WhatsApp. You\u2019ll need to have WhatsApp configured in your Odoo instance for this to work."),
        sp(),
        // Social Media
        dialogueLine("4:55", "Point to Facebook, X, LinkedIn icons",
          "And then you have social media sharing. You can share the job directly to Facebook, X \u2014 formerly Twitter \u2014 or LinkedIn. Each of these opens the respective platform with a pre-filled post containing your tracking link."),
        sp(),
        dialogueLine("5:10", "Click \"Share Now\" (link icon)",
          "There\u2019s also the Share Now button, which copies a unique tracking link to your clipboard. You can paste this anywhere \u2014 a chat message, a personal blog, a community forum, wherever you like."),
        sp(),
        // Email all jobs
        dialogueLine("5:20", "Go back to main dashboard, point to \"Email a friend\" button at bottom",
          "One more thing \u2014 from the main dashboard, there\u2019s an Email a Friend button at the bottom. This lets you share all open job positions at once in a single email, rather than sharing one job at a time."),
        sp(),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 7: POINTS & LEVELS
        // ═══════════════════════════════════════════
        h1("7. Points System & Levels (5:30 \u2013 7:30)"),
        sp(),
        sectionHeader("SEGMENT 5: POINTS & LEVELS"),
        sp(),
        dialogueLine("5:30", "Main dashboard, point to Total points and To Spend sections",
          "Now let\u2019s understand the points system, which is really the heart of this whole gamification experience. On the dashboard, you\u2019ll see two numbers \u2014 Total points earned over your lifetime, and points available To Spend on rewards."),
        sp(),
        dialogueLine("5:50", "Click on \"Referrals\" tab below avatar",
          "Below your avatar, you\u2019ll see three sections: Referrals, Ongoing, and Successful. Referrals shows the total count, Ongoing shows candidates still in the hiring pipeline, and Successful shows the ones who actually got hired."),
        sp(),
        dialogueLine("6:05", "Click \"Referrals\" \u2192 My Referrals page opens, show referral cards",
          "Clicking on Referrals shows all your referral cards. Each card has the applicant\u2019s name, the job they applied for, the recruiter handling it, and a progress bar showing points earned. Successfully hired referrals have a green stripe and a \"Hired\" badge."),
        sp(),
        dialogueLine("6:25", "Zoom into a referral card\u2019s progress bar, highlight stages",
          "Now let me explain how points are earned. As your referred candidate progresses through the recruitment stages, you earn points at each milestone. Let me show you the default point structure."),
        sp(),
        // Points Table
        p([{ text: "[Show this table as text overlay or narrate]", italics: true, color: "999999" }]),
        sp(),
        new Table({
          width: { size: CW, type: WidthType.DXA }, columnWidths: [4680, 4680],
          rows: [
            new TableRow({ children: [hCell("Recruitment Stage", 4680), hCell("Points Earned", 4680)] }),
            new TableRow({ children: [tCell("Initial Qualification", 4680), tCell("1 point", 4680, { center: true })] }),
            new TableRow({ children: [tCell("First Interview", 4680), tCell("20 points", 4680, { center: true })] }),
            new TableRow({ children: [tCell("Second Interview", 4680), tCell("9 points", 4680, { center: true })] }),
            new TableRow({ children: [tCell("Contract Proposal", 4680), tCell("5 points", 4680, { center: true })] }),
            new TableRow({ children: [tCell("Contract Signed", 4680), tCell("50 points", 4680, { center: true, bold: true })] }),
            new TableRow({ children: [tCell("TOTAL (if hired)", 4680, { bold: true, shade: "E8F5E9" }), tCell("85 points", 4680, { center: true, bold: true, shade: "E8F5E9" })] }),
          ],
        }),
        sp(),
        dialogueLine("6:50", "Narrate the table, point to each stage",
          "So when your candidate first gets qualified, you get 1 point. When they clear the first interview, you get 20 more points. Second interview gives you 9 points, contract proposal gives you 5, and the big one \u2014 when the contract is signed, you get 50 points. That\u2019s a total of 85 points for a successful hire. And these points can be customized by the administrator in the Recruitment app."),
        sp(),
        // Levels
        dialogueLine("7:00", "Go back to dashboard, point to level indicator below user photo",
          "Now about Levels. See this circle around my photo? The cyan-colored portion shows my progress towards the next level. As you earn points, your avatar evolves \u2014 it gets capes, shields, and other superhero elements."),
        sp(),
        dialogueLine("7:15", "If level up is available, click \"CLICK TO LEVEL UP!\" Otherwise, show Configuration \u2192 Levels",
          "Levels are purely for fun and motivation \u2014 they don\u2019t affect anything functionally. But they add that competitive element. Administrators can customize the level names, the points required to reach each level, and even the avatar images from Configuration, then Levels."),
        sp(),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 8: REWARDS
        // ═══════════════════════════════════════════
        h1("8. Rewards \u2014 Configuration & Redemption (7:30 \u2013 9:30)"),
        sp(),
        sectionHeader("SEGMENT 6: REWARDS"),
        sp(),
        dialogueLine("7:30", "Navigate to Referrals \u2192 Configuration \u2192 Rewards",
          "Now let\u2019s talk about the best part \u2014 Rewards! This is the only configuration you absolutely need to set up for the Referrals app to be meaningful. Let me navigate to Configuration, then Rewards."),
        sp(),
        dialogueLine("7:45", "Rewards list view visible",
          "Here you can see all configured rewards. Let\u2019s create a new one to show you how it works."),
        sp(),
        dialogueLine("7:50", "Click \"New\" \u2192 Reward form opens",
          "Click New. Let me fill this in. For the Product Name, I\u2019ll type in \u201CAmazon Gift Card\u201D. For Cost, I\u2019ll set it to 100 points. The Gift Responsible is the person who actually procures and delivers the reward when an employee redeems it \u2014 I\u2019ll select our HR Manager here."),
        sp(),
        dialogueLine("8:15", "Add a photo, fill in description tab",
          "I\u2019ll add a photo of a gift card here, and in the Description tab, I\u2019ll write something like \u201CRedeem your hard-earned referral points for an Amazon gift card worth 500 rupees. Thank you for helping us grow the team!\u201D"),
        sp(),
        dialogueLine("8:35", "Click Save, go back to rewards list, show multiple rewards",
          "And that\u2019s it \u2014 let me save this. Now we have our reward configured. Let me show you a few more that I\u2019ve already set up \u2014 a company branded mug for 50 points, a backpack for 150 points, and a team lunch for 200 points."),
        sp(),
        callout("Important Tip", [
          "Always set a cost for your rewards. If you leave the cost at zero, the reward shows as free in the shop, and employees can redeem it unlimited times. Also, always add a photo \u2014 it makes the rewards page look much more appealing."
        ]),
        sp(),
        // Redeeming
        dialogueLine("8:55", "Go to main Referrals dashboard \u2192 Click \"Rewards\" button",
          "Now let me show you what the employee sees. From the Referrals dashboard, click the Rewards button. This is the rewards shop."),
        sp(),
        dialogueLine("9:05", "Rewards page with multiple reward cards visible",
          "Each reward is displayed as a card with the name, photo, description, and the points needed. If you have enough points, you\u2019ll see a Buy button at the bottom. If you don\u2019t have enough, it tells you exactly how many more points you need."),
        sp(),
        dialogueLine("9:20", "Click Buy on a reward (if points available), show confirmation dialog",
          "Let me buy this mug. Click Buy. A confirmation dialog appears \u2014 \"Are you sure?\" Click OK. And done! The points are deducted from my available balance, and the Gift Responsible person gets notified to deliver the reward."),
        sp(),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 9: HIRED REFERRALS
        // ═══════════════════════════════════════════
        h1("9. Hired Referrals & Friend Avatars (9:30 \u2013 10:30)"),
        sp(),
        sectionHeader("SEGMENT 7: HIRED REFERRALS"),
        sp(),
        dialogueLine("9:30", "Show dashboard with avatars beside the user\u2019s photo (if available). Otherwise, use text overlay to explain the concept.",
          "Here\u2019s something really cool. When a candidate you referred actually gets hired, the Referrals app celebrates it! The next time you open the app, instead of the normal dashboard, you get a special screen that says \u2014 \u201CYour referral has been hired! Choose an avatar for your new friend!\u201D"),
        sp(),
        dialogueLine("9:50", "Show the avatar selection screen (or screenshot from docs)",
          "You get to pick from five superhero avatars \u2014 they\u2019re fun characters like robots, dogs, heroes. Once you select one, that avatar appears on your dashboard next to yours, as part of your growing superhero team. It\u2019s a really nice visual touch."),
        sp(),
        dialogueLine("10:05", "Show Configuration \u2192 Friends",
          "Administrators can customize these friend avatars from Configuration, then Friends. You can change the names, images, and whether they appear in front of or behind your main avatar."),
        sp(),
        callout("Design Note", [
          "If you customize the avatar images, use files with transparent backgrounds. Once an image is changed and saved, you CANNOT revert to the original \u2014 you\u2019d need to uninstall and reinstall the Referrals app. So be careful with image customizations."
        ]),
        sp(),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 10: ALERTS
        // ═══════════════════════════════════════════
        h1("10. Alerts \u2014 Dashboard Announcements (10:30 \u2013 11:15)"),
        sp(),
        sectionHeader("SEGMENT 8: ALERTS"),
        sp(),
        dialogueLine("10:30", "Navigate to Referrals \u2192 Configuration \u2192 Alerts",
          "The Referrals app also has an Alerts feature. This lets administrators post important messages at the top of the Referrals dashboard. Think of it as an announcement banner \u2014 great for things like \"We urgently need a Senior Developer!\" or \"Double points this month for dev hires!\""),
        sp(),
        dialogueLine("10:45", "Click New \u2192 Alert form opens",
          "Let me create one. Click New. Set the Date From and Date To \u2014 this controls how long the alert stays visible. In the Alert field, type your message. For example, \u201CUrgent hiring! Refer candidates for our Qatar office and earn bonus rewards!\u201D"),
        sp(),
        dialogueLine("11:00", "Show On Click options (Not Clickable, Go to All Jobs, Specify URL)",
          "You can also control what happens when someone clicks the alert. You have three options \u2014 Not Clickable, which just shows the text. Go to All Jobs, which takes them to the job listings on your website. Or Specify URL, which lets you link to any custom URL."),
        sp(),
        dialogueLine("11:10", "Click Save, then click \"Send Mail\" button",
          "After saving, there\u2019s a Send Mail button that lets you email all employees about this alert, so they don\u2019t have to wait until they open the Referrals app to see it."),
        sp(),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 11: REPORTING
        // ═══════════════════════════════════════════
        h1("11. Reporting & Analytics (11:15 \u2013 12:30)"),
        sp(),
        sectionHeader("SEGMENT 9: REPORTING"),
        sp(),
        dialogueLine("11:15", "Navigate to Referrals \u2192 Reporting",
          "Now let\u2019s look at the reporting features. The Referrals app comes with three built-in reports. These are only accessible to Administrators."),
        sp(),
        // Points Report
        dialogueLine("11:25", "Click Reporting \u2192 Points",
          "The first report is the Points Report. This shows the total points earned by each employee, organized by their referrals. You can expand each employee\u2019s row to see which referrals earned them points, at which stage, and how many points."),
        sp(),
        dialogueLine("11:40", "Apply filter: Custom Filter \u2192 Stage = Contract Signed",
          "Here\u2019s a useful tip \u2014 you can filter this to show only \"Contract Signed\" stage entries. This immediately tells you who is the most successful referrer in your company \u2014 the employee with the most hired referrals."),
        sp(),
        // Referral Analysis
        dialogueLine("11:55", "Click Reporting \u2192 Referral Analysis",
          "The second report is the Referral Analysis. This is a bar chart that shows where your referrals are coming from \u2014 Email, LinkedIn, Facebook, SMS, and so on. The bars are color-coded to show how many are Hired, In Progress, or Not Hired."),
        sp(),
        dialogueLine("12:10", "Switch to Pivot view, adjust measures",
          "You can switch to a pivot table view for deeper analysis. For example, you can see which employee has the most referrals and the best conversion rate \u2014 meaning, the highest ratio of referrals to actual hires. You can even export this data to a spreadsheet."),
        sp(),
        // Rewards Report
        dialogueLine("12:20", "Click Reporting \u2192 Rewards",
          "And the third report is the Rewards Report. This shows which rewards are most popular among employees. This helps you plan your reward inventory \u2014 if everyone\u2019s redeeming gift cards but nobody wants the backpack, you know what to stock more of."),
        sp(),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 12: CLOSING
        // ═══════════════════════════════════════════
        h1("12. Closing & Call to Action (12:30 \u2013 13:00)"),
        sp(),
        sectionHeader("SEGMENT 10: CLOSING"),
        sp(),
        dialogueLine("12:30", "Main Referrals dashboard visible",
          "So that\u2019s the complete walkthrough of the Odoo 19 Referrals app! Let me quickly recap what we covered."),
        sp(),
        dialogueLine("12:35", "Text overlay or quick montage of each section (1 sec each)",
          "We saw how to install the app, the onboarding experience, how employees can share job positions via Email, SMS, WhatsApp, and social media, the points and leveling system, how to configure and redeem rewards, the hired referral celebration with friend avatars, dashboard alerts for important announcements, and three powerful reports to track your referral program\u2019s performance."),
        sp(),
        dialogueLine("12:55", "Infintor Solutions logo and contact info on screen",
          "If you found this video helpful, don\u2019t forget to hit that like button, subscribe to our channel, and turn on the bell icon so you don\u2019t miss our upcoming Odoo tutorials. If you need help implementing Odoo for your business, Infintor Solutions is here to help. We\u2019re an official Odoo partner, based in Kochi, Kerala, with offices in Qatar, Dubai, and Germany. Drop us a message or visit infintor.com to get started."),
        sp(),
        dialogueLine("13:10", "End screen: Subscribe button, related videos, Infintor website URL",
          "Thanks for watching, and we\u2019ll see you in the next one!"),
        sp(),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 13: YOUTUBE METADATA
        // ═══════════════════════════════════════════
        h1("13. YouTube Metadata & SEO"),
        sp(),
        h2("13.1 Video Title (Options)"),
        p([{ text: "Option A: ", bold: true }, { text: "Odoo 19 Referrals App | Complete Guide | Employee Referral Program | Infintor Solutions" }]),
        p([{ text: "Option B: ", bold: true }, { text: "Odoo 19 Referrals Overview | Gamify Your Hiring | Complete Tutorial | Infintor Solutions" }]),
        p([{ text: "Option C: ", bold: true }, { text: "How to Use the Referrals App in Odoo 19 | Points, Rewards & Reports | Infintor Solutions" }]),
        sp(),

        h2("13.2 Video Description"),
        callout("Copy this for YouTube Description", [
          "Discover how Odoo 19\u2019s Referrals app gamifies your employee referral program with points, levels, rewards, and superhero avatars!",
          "",
          "In this complete tutorial by Infintor Solutions, we cover:",
          "\u2022 Installation & Prerequisites",
          "\u2022 Onboarding Experience",
          "\u2022 Sharing Job Positions (Email, SMS, WhatsApp, Social Media)",
          "\u2022 Points System & Recruitment Stage Points",
          "\u2022 Levels & Avatars",
          "\u2022 Configuring & Redeeming Rewards",
          "\u2022 Alerts & Announcements",
          "\u2022 Reporting (Points, Referral Analysis, Rewards)",
          "",
          "Need help implementing Odoo? Contact Infintor Solutions!",
          "\uD83C\uDF10 Website: https://www.infintor.com",
          "\uD83D\uDCDE India: +91 97452 88880",
          "\uD83D\uDCDE Qatar: +974 3005 1818",
          "\uD83D\uDCDE UAE: +971 56 792 0239",
          "\uD83D\uDCCD Kochi | Doha | Dubai | Germany",
          "",
          "#Odoo19 #Referrals #EmployeeReferral #HRTech #OdooTutorial #InfintorSolutions #OdooPartner #Recruitment #Gamification #Odoo"
        ]),
        sp(),

        h2("13.3 Tags"),
        p("Odoo 19, Referrals app, Odoo Referrals, Employee Referral Program, Odoo 19 tutorial, Odoo HR, Odoo Recruitment, gamification, referral points, Odoo rewards, Infintor Solutions, Odoo partner India, Odoo Kochi, HR software, hiring automation, Odoo ERP"),
        sp(),

        h2("13.4 Thumbnail Suggestions"),
        bullet("Show split screen: Referrals dashboard on left, reward cards on right"),
        bullet("Text overlay: \"Odoo 19 Referrals\" in large bold text"),
        bullet("Include Infintor Solutions logo (small, bottom-right corner)"),
        bullet("Use bright colors \u2014 the app\u2019s superhero theme can work for this"),
        bullet("Add a small text callout: \"Points + Rewards + Gamification\""),
        sp(),
        new Paragraph({ children: [new PageBreak()] }),

        // ═══════════════════════════════════════════
        // SECTION 14: APPENDICES
        // ═══════════════════════════════════════════
        h1("14. Appendix \u2014 Quick Reference"),
        sp(),

        h2("14.1 Menu Paths Reference"),
        new Table({
          width: { size: CW, type: WidthType.DXA }, columnWidths: [3500, 5860],
          rows: [
            new TableRow({ children: [hCell("Action", 3500), hCell("Menu Path", 5860)] }),
            new TableRow({ children: [tCell("Open Referrals App", 3500), tCell("Main Menu \u2192 Referrals", 5860)] }),
            new TableRow({ children: [tCell("View Open Jobs", 3500), tCell("Referrals Dashboard \u2192 View Jobs", 5860)] }),
            new TableRow({ children: [tCell("Email All Jobs", 3500), tCell("Referrals Dashboard \u2192 Email a Friend (bottom)", 5860)] }),
            new TableRow({ children: [tCell("View Rewards Shop", 3500), tCell("Referrals Dashboard \u2192 Rewards", 5860)] }),
            new TableRow({ children: [tCell("Configure Rewards", 3500), tCell("Referrals \u2192 Configuration \u2192 Rewards", 5860)] }),
            new TableRow({ children: [tCell("Configure Alerts", 3500), tCell("Referrals \u2192 Configuration \u2192 Alerts", 5860)] }),
            new TableRow({ children: [tCell("Configure Onboarding", 3500), tCell("Referrals \u2192 Configuration \u2192 Onboarding", 5860)] }),
            new TableRow({ children: [tCell("Configure Levels", 3500), tCell("Referrals \u2192 Configuration \u2192 Levels", 5860)] }),
            new TableRow({ children: [tCell("Configure Friends", 3500), tCell("Referrals \u2192 Configuration \u2192 Friends", 5860)] }),
            new TableRow({ children: [tCell("Points Report", 3500), tCell("Referrals \u2192 Reporting \u2192 Points", 5860)] }),
            new TableRow({ children: [tCell("Referral Analysis", 3500), tCell("Referrals \u2192 Reporting \u2192 Referral Analysis", 5860)] }),
            new TableRow({ children: [tCell("Rewards Report", 3500), tCell("Referrals \u2192 Reporting \u2192 Rewards", 5860)] }),
          ],
        }),
        sp(),

        h2("14.2 Required Apps"),
        new Table({
          width: { size: CW, type: WidthType.DXA }, columnWidths: [3120, 6240],
          rows: [
            new TableRow({ children: [hCell("App", 3120), hCell("Why Required", 6240)] }),
            new TableRow({ children: [tCell("Employees", 3120, { bold: true }), tCell("Stores employee data; links referrers to their profiles", 6240)] }),
            new TableRow({ children: [tCell("Recruitment", 3120, { bold: true }), tCell("Manages job positions, applicant pipeline, and recruitment stages", 6240)] }),
            new TableRow({ children: [tCell("Website", 3120, { bold: true }), tCell("Publishes job positions online; generates tracking links for referrals", 6240)] }),
          ],
        }),
        sp(),

        h2("14.3 Access Rights"),
        new Table({
          width: { size: CW, type: WidthType.DXA }, columnWidths: [2340, 7020],
          rows: [
            new TableRow({ children: [hCell("Role", 2340), hCell("Can Do", 7020)] }),
            new TableRow({ children: [tCell("Referral User", 2340, { bold: true }), tCell("View jobs, share referrals, earn points, buy rewards", 7020)] }),
            new TableRow({ children: [tCell("Officer", 2340, { bold: true }), tCell("Everything above + view referral details", 7020)] }),
            new TableRow({ children: [tCell("Administrator", 2340, { bold: true }), tCell("Everything above + configure rewards, alerts, levels, onboarding; access all reports", 7020)] }),
          ],
        }),
        sp(), sp(),

        // ─── Document Info ───
        new Paragraph({ border: { top: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC", space: 8 } }, spacing: { before: 300, after: 60 }, children: [new TextRun({ text: "Document Information", font: "Arial", size: 18, bold: true, color: "999999" })] }),
        p([{ text: "Version: ", color: "999999", size: 18 }, { text: "1.0", color: "999999", size: 18 }]),
        p([{ text: "Author: ", color: "999999", size: 18 }, { text: "Rohan Raj, Business Analyst Intern, Infintor Solutions", color: "999999", size: 18 }]),
        p([{ text: "Date: ", color: "999999", size: 18 }, { text: "March 4, 2026", color: "999999", size: 18 }]),
        p([{ text: "Source: ", color: "999999", size: 18 }, { text: "Odoo 19 Official Documentation (Local 19.0 Docs)", color: "999999", size: 18 }]),
        p([{ text: "Reference Video: ", color: "999999", size: 18 }, { text: "Cybrosys Technologies \u2014 Odoo 19 Referrals Overview (YouTube)", color: "999999", size: 18 }]),
        p([{ text: "Company: ", color: "999999", size: 18 }, { text: "Infintor Solutions, 9th Floor, Vismaya Infopark, Kochi, Kerala 682030", color: "999999", size: 18 }]),
      ],
    },
  ],
});

// ─── Write ───
const OUT = "c:\\Odoo Study\\My learnings\\Referral_App_Video_Script_Infintor.docx";
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log(`Created: ${OUT}`);
  console.log(`Size: ${(buf.length / 1024).toFixed(1)} KB`);
}).catch(err => { console.error("Error:", err.message); process.exit(1); });
