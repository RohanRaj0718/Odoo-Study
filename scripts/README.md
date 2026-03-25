<<<<<<< HEAD
# scripts/ — Document & Root Generators

This folder contains the root-level Javascript tools that were moved here to keep the repo clean.

- `generate_*.js`: Node.js scripts used to generate formatted `.docx` files from Markdown or JSON data (e.g., `generate_seo_blog_docx_v2.js`).
- `package.json` / `package-lock.json`: Dependencies for the Node tools (`docx` library).

*Note on Python Tools:* The Odoo automation Python scripts remain in their original location: `My learnings/Additional pythons scripts/` to preserve the user's workflow.
=======
# scripts/ — Utility Scripts

Helper scripts for Odoo automation, document generation, and research.

## Subdirectories

| Folder | Language | Purpose |
|--------|----------|---------|
| `odoo-automation/` | Python | Odoo RPC/API scripts: demo data setup, audits, screenshots |
| `docx-generators/` | JavaScript (Node.js) | Generate formatted `.docx` files for blog posts and guides |
| `youtube/` | Python | Download YouTube video/playlist transcripts |

## Quick Start

### Download a YouTube transcript
```bash
pip install pytube youtube-transcript-api
python scripts/youtube/youtube_transcript.py "<YouTube URL>"
```

### Set up a demo Odoo environment
```bash
# Requires: Odoo 19 running locally + pip install odoolib
python scripts/odoo-automation/setup_advanced_demo.py
```

### Generate a .docx blog post
```bash
# Requires: Node.js + npm install docx
node scripts/docx-generators/generate_seo_blog_docx_v2.js
```

## Key Scripts

| Script | What it does |
|--------|-------------|
| `odoo-automation/setup_advanced_demo.py` | Full demo environment with products, customers, orders |
| `odoo-automation/setup_manufacturing_demo.py` | MFG-specific demo data (BoMs, work centers, MOs) |
| `odoo-automation/audit_odoo19.py` | Audits Odoo instance configuration |
| `odoo-automation/generate_screenshots.py` | Automated UI screenshot capture |
| `odoo-automation/create_bank_statement_excel.py` | Creates bank statement Excel for reconciliation demo |
| `docx-generators/generate_seo_blog_docx_v2.js` | Most up-to-date blog .docx generator |
| `youtube/youtube_transcript.py` | Generic transcript downloader |
>>>>>>> dabb357f8d4da860d0ebf466d30a56b1ab0b2abc
