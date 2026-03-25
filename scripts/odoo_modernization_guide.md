# Odoo Website Modernization: Developer Guide

This guide describes how to modernize Odoo website pages using a "Database Injection" approach that maintains compatibility with the Odoo Drag-and-Drop editor.

## **1. Core Concept: `arch_db` Injection**
Every Odoo website page is stored as a "View" (`ir.ui.view`). The HTML of the page's body is stored in a field called `arch_db`. 
*   **The Workflow**: Build the HTML locally → Connect to Odoo Shell → Run a Python script to update the `arch_db`.

---

## **2. Snippet-Based HTML (The "Odoo Way")**
To ensure the **Edit** button in Odoo works, your HTML must use specific "Snippet" attributes. If you omit these, the page will be "static" and the client won't be able to change anything.

### **Mandatory Wrapper Attributes**
For each section (`<section>` tag), you MUST include:
*   `class="s_cover"`, `class="s_text_image"`, etc. (The snippet's class)
*   `data-snippet="s_cover"`, `data-snippet="s_text_image"`, etc. (The snippet's identifier)
*   `data-name="Cover"`, `data-name="Text - Image"`, etc. (The human-readable name)

### **Key Snippet Examples**
*   **Hero Section**: `<section class="s_cover parallax s_parallax_is_fixed" data-snippet="s_cover" data-name="Cover">`
*   **Itinerary Step (Text/Image)**: `<section class="s_text_image" data-snippet="s_text_image" data-name="Text - Image">`
*   **Quick Info (Features)**: `<section class="s_features" data-snippet="s_features" data-name="Features">`
*   **Call to Action**: `<section class="s_call_to_action" data-snippet="s_call_to_action" data-name="Call to Action">`

---

## **3. The "Safe" Injection Script**
When running on **Live Sites**, never use record IDs (like `2851`). Always search by `key`.

### **Injection Template (Python Shell)**
```python
# 1. Provide your HTML as a string
new_html = '<t t-name="website.PAGE_KEY"><t t-call="website.layout"><div id="wrap" class="oe_structure oe_empty">...SNIPPETS HERE...</div></t></t>'

# 2. Find the view dynamically by its key
view = env['ir.ui.view'].search([('key', '=', 'website.PAGE_KEY')], limit=1)

if view:
    # 3. Write it to the database
    view.write({'arch_db': new_html})
    # 4. Commit to save the changes
    env.cr.commit()
    print('SUCCESS: View updated successfully.')
else:
    print('ERROR: Could not find view with that key.')
```

---

## **4. Prompting Copilot for Help**

### **For Generating HTML Content**
> "I am modernizing an Odoo 19 travel website page. I need the HTML for a [Destination] package itinerary. 
> REQUIREMENTS:
> 1. Use Odoo native snippet attributes like 'data-snippet=\"s_text_image\"' and 'data-name=\"Text - Image\"' for every section.
> 2. Use a zigzag layout (Image-Left then Image-Right) for the itinerary days.
> 3. Use Bootstrap 5 classes (col-lg-6, mb-4, etc.) for layout.
> 4. Add a 'Features' section at the top for quick trip info (Price, Duration, Transport).
> DETAILS: [Paste PDF text or itinerary details here]"

### **For Generating the Injection Code**
> "Generate an Odoo Python shell script that searches for an 'ir.ui.view' with key 'website.manali-package' and updates its 'arch_db' field with the following HTML: [Paste HTML]. Ensure 'env.cr.commit()' is included and use a dynamic search instead of a hardcoded ID."

### **For Fixing Specific Elements (Like the "Day 0" issue)**
> "Write a one-line Python script for the Odoo shell to find a view with key 'website.manali-kasol-4n-5d-package' and replace the text 'DAY 0' with 'JOURNEY NIGHT' in its 'arch_db' field without changing anything else."

---

## **5. Live Site Safety Steps**
1.  **Backup**: Always trigger an Odoo.sh backup first.
2.  **Staging**: Test the code on a staging branch before running on Production.
3.  **Read Before Write**: Always run a `print(view.arch_db[:500])` first to make sure you found the right record.
