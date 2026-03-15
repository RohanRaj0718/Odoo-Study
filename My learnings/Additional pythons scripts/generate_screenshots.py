"""Generate realistic Odoo 19 mock screenshots for the client operations guide.
These match the visual style observed in the reference documents."""
from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs('screenshots', exist_ok=True)

# ── Odoo 19 Color Palette (from reference screenshots) ──
NAVBAR_DARK = (25, 52, 95)       # #19345F - top bar
NAVBAR_MID = (40, 82, 149)       # #285295 - nav items
PURPLE_BTN = (113, 75, 154)      # #714B9A - primary button (Odoo 19)
WHITE = (255, 255, 255)
BG_LIGHT = (249, 250, 251)       # #F9FAFB - alternating row bg
BORDER = (222, 226, 230)         # #DEE2E6 - table borders
TEXT_DARK = (33, 37, 41)         # #212529 - primary text
TEXT_MID = (108, 117, 125)       # #6C757D - secondary text
TEXT_BLUE = (0, 123, 190)        # #007BBE - link text
GREEN = (40, 167, 69)            # #28A745 - success/profit
RED = (220, 53, 69)              # #DC3545 - loss/negative
SIDEBAR_BG = (39, 42, 53)       # #272A35 - dark mode sidebar
YELLOW_STAR = (255, 193, 7)      # #FFC107
BREADCRUMB_BG = (248, 249, 250)  # light grey breadcrumb area

def get_font(size=14, bold=False):
    """Try to get a system font, fallback to default"""
    font_paths = [
        'C:/Windows/Fonts/segoeui.ttf',
        'C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',
        'C:/Windows/Fonts/arial.ttf',
        'C:/Windows/Fonts/calibri.ttf',
    ]
    if bold:
        font_paths.insert(0, 'C:/Windows/Fonts/segoeuib.ttf')
        font_paths.insert(1, 'C:/Windows/Fonts/arialbd.ttf')
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except:
            continue
    return ImageFont.load_default()

FONT_SM = get_font(13)
FONT_REG = get_font(15)
FONT_MED = get_font(16, bold=True)
FONT_LG = get_font(18, bold=True)
FONT_XL = get_font(22, bold=True)
FONT_TINY = get_font(11)
FONT_BTN = get_font(13, bold=True)

def draw_navbar(draw, w, app_name="Sales", breadcrumb=""):
    """Draw Odoo 19 top navigation bar"""
    # Top dark bar
    draw.rectangle([0, 0, w, 46], fill=NAVBAR_DARK)
    # App name area
    draw.rectangle([0, 0, 50, 46], fill=NAVBAR_MID)
    # Hamburger menu icon
    for y_off in [16, 22, 28]:
        draw.rectangle([15, y_off, 35, y_off+2], fill=WHITE)
    # Odoo logo area
    draw.text((60, 13), "Odoo", fill=WHITE, font=FONT_MED)
    # App name
    draw.text((120, 13), app_name, fill=(200, 210, 220), font=FONT_REG)
    
    # Company selector on right
    draw.text((w-200, 13), "Parappattu Group ▾", fill=(180, 190, 200), font=FONT_SM)
    
    # User avatar circle
    draw.ellipse([w-38, 10, w-12, 36], fill=PURPLE_BTN)
    draw.text((w-32, 14), "G", fill=WHITE, font=FONT_BTN)
    
    # Breadcrumb bar
    if breadcrumb:
        draw.rectangle([0, 46, w, 82], fill=WHITE)
        draw.line([0, 82, w, 82], fill=BORDER, width=1)
        draw.text((20, 54), breadcrumb, fill=TEXT_DARK, font=FONT_MED)
    return 82 if breadcrumb else 46

def draw_button(draw, x, y, text, color=PURPLE_BTN, text_color=WHITE):
    """Draw an Odoo-style button"""
    tw = len(text) * 8 + 20
    draw.rounded_rectangle([x, y, x+tw, y+32], radius=4, fill=color)
    draw.text((x+10, y+7), text, fill=text_color, font=FONT_BTN)
    return tw

def draw_field(draw, x, y, label, value, w=250):
    """Draw a form field with label and value"""
    draw.text((x, y), label, fill=TEXT_MID, font=FONT_SM)
    draw.rectangle([x, y+18, x+w, y+44], outline=BORDER, width=1)
    draw.text((x+8, y+22), value, fill=TEXT_DARK, font=FONT_REG)
    return y + 52

def draw_dropdown_field(draw, x, y, label, value, w=250):
    """Draw a form field with dropdown indicator"""
    draw.text((x, y), label, fill=TEXT_MID, font=FONT_SM)
    draw.rectangle([x, y+18, x+w, y+44], outline=BORDER, width=1)
    draw.text((x+8, y+22), value, fill=TEXT_DARK, font=FONT_REG)
    draw.text((x+w-20, y+22), "▾", fill=TEXT_MID, font=FONT_SM)
    return y + 52

def draw_table_row(draw, x, y, cols, widths, bg=WHITE, bold=False, colors=None):
    """Draw a table row"""
    font = FONT_MED if bold else FONT_REG
    draw.rectangle([x, y, x+sum(widths), y+36], fill=bg)
    draw.line([x, y+36, x+sum(widths), y+36], fill=BORDER, width=1)
    cx = x
    for i, (col, w) in enumerate(zip(cols, widths)):
        color = colors[i] if colors else (TEXT_DARK if not bold else TEXT_DARK)
        draw.text((cx+10, y+8), str(col), fill=color, font=font)
        draw.line([cx+w, y, cx+w, y+36], fill=BORDER, width=1)
        cx += w
    return y + 36

def draw_checkbox(draw, x, y, label, checked=False):
    """Draw a checkbox with label"""
    draw.rectangle([x, y, x+18, y+18], outline=BORDER, width=1, fill=WHITE)
    if checked:
        draw.rectangle([x+2, y+2, x+16, y+16], fill=PURPLE_BTN)
        draw.text((x+4, y+0), "✓", fill=WHITE, font=FONT_SM)
    draw.text((x+26, y+0), label, fill=TEXT_DARK, font=FONT_REG)

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 1: Company Selector
# ══════════════════════════════════════════════════════════════════
def create_company_selector():
    w, h = 1200, 500
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    draw_navbar(draw, w, "Sales")
    
    # Company selector dropdown expanded
    sx = w - 280
    draw.rectangle([sx, 46, sx+260, 260], fill=WHITE, outline=BORDER)
    # Shadow effect
    draw.rectangle([sx+2, 262, sx+262, 264], fill=(230, 230, 230))
    
    companies = [
        ("Parappattu Group", True, True),
        ("  ├ Georgeon Furniture", False, False),
        ("  └ PSQUARE INTERIOR", False, False),
        ("PSQUARE INTERIOR FURNISHING", False, False),
    ]
    cy = 54
    for name, selected, is_parent in companies:
        bg = (240, 243, 255) if selected else WHITE
        draw.rectangle([sx+2, cy, sx+258, cy+42], fill=bg)
        color = PURPLE_BTN if selected else TEXT_DARK
        font = FONT_MED if is_parent else FONT_REG
        draw.text((sx+16, cy+10), name, fill=color, font=font)
        if selected:
            draw.text((sx+230, cy+10), "✓", fill=PURPLE_BTN, font=FONT_MED)
        cy += 44
    
    # Content area hint
    draw.text((20, 100), "Select a company to switch context.", fill=TEXT_MID, font=FONT_REG)
    draw.text((20, 125), "All operations, reports and data will filter", fill=TEXT_MID, font=FONT_REG)
    draw.text((20, 150), "to the selected company.", fill=TEXT_MID, font=FONT_REG)
    
    # Red highlight arrow pointing to selector
    draw.text((sx-130, 50), "← Click here", fill=RED, font=FONT_LG)
    
    img.save('screenshots/01_company_selector.png')
    print("  ✓ 01_company_selector.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 2: Sales Order with Warehouse field
# ══════════════════════════════════════════════════════════════════
def create_sales_order():
    w, h = 1200, 620
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Sales", "Quotations / New")
    
    # Buttons row
    bx = 20
    draw_button(draw, bx, by+10, "Confirm")
    draw_button(draw, bx+110, by+10, "Send by Email", color=WHITE, text_color=TEXT_DARK)
    draw_button(draw, bx+260, by+10, "Cancel", color=WHITE, text_color=TEXT_DARK)
    
    # Status badge
    draw.rounded_rectangle([w-160, by+12, w-20, by+40], radius=12, fill=(230, 240, 255))
    draw.text((w-145, by+16), "Quotation", fill=PURPLE_BTN, font=FONT_SM)
    
    fy = by + 55
    
    # Form fields
    fy = draw_dropdown_field(draw, 20, fy, "Customer", "Kerala Home Décor", w=350)
    
    # Expiration and payment
    draw_field(draw, 400, fy-52, "Expiration", "03/25/2026", w=200)
    
    # WAREHOUSE FIELD - highlighted
    wy = fy + 10
    draw.text((20, wy), "Warehouse", fill=TEXT_MID, font=FONT_SM)
    # Yellow highlight box around warehouse field
    draw.rectangle([18, wy+16, 372, wy+48], outline=RED, width=2)
    draw.rectangle([20, wy+18, 370, wy+46], outline=BORDER, width=1, fill=(255, 255, 240))
    draw.text((28, wy+22), "Near Home GF (NH GF)", fill=TEXT_DARK, font=FONT_REG)
    draw.text((330, wy+22), "▾", fill=TEXT_MID, font=FONT_SM)
    
    # Red arrow
    draw.text((380, wy+18), "← Select warehouse here", fill=RED, font=FONT_MED)
    
    # Warehouse dropdown showing options
    ddx, ddy = 20, wy+48
    draw.rectangle([ddx, ddy, ddx+350, ddy+140], fill=WHITE, outline=BORDER)
    wh_options = ["Parappattu Group (WH)", "Near Home GF (NH GF)", "Near Home FF (NH FF)", "Factory Building (FB)"]
    for i, opt in enumerate(wh_options):
        row_bg = (240, 243, 255) if i == 1 else WHITE
        draw.rectangle([ddx+1, ddy+i*34+1, ddx+349, ddy+(i+1)*34], fill=row_bg)
        color = PURPLE_BTN if i == 1 else TEXT_DARK
        draw.text((ddx+12, ddy+i*34+8), opt, fill=color, font=FONT_REG)
    
    # Order lines table below
    tby = ddy + 160
    draw.text((20, tby), "Order Lines", fill=TEXT_DARK, font=FONT_MED)
    tby += 28
    cols_h = ["Product", "Description", "Quantity", "Unit Price", "Tax", "Subtotal"]
    widths_h = [200, 280, 80, 100, 120, 120]
    tby = draw_table_row(draw, 20, tby, cols_h, widths_h, bg=(245, 247, 250), bold=True)
    tby = draw_table_row(draw, 20, tby, ["PVC Blinds", "PVC Window Blinds - White", "50.00", "₹1,250.00", "18% GST", "₹62,500.00"], widths_h)
    tby = draw_table_row(draw, 20, tby, ["ESS Mat (DWR)", "Essential Mat Double Wash", "25.00", "₹890.00", "18% GST", "₹22,250.00"], widths_h)
    
    img.save('screenshots/02_sales_order_warehouse.png')
    print("  ✓ 02_sales_order_warehouse.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 3: Purchase Order with Deliver To
# ══════════════════════════════════════════════════════════════════
def create_purchase_order():
    w, h = 1200, 520
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Purchase", "Purchase Orders / New")
    
    draw_button(draw, 20, by+10, "Confirm Order")
    draw_button(draw, 170, by+10, "Send by Email", color=WHITE, text_color=TEXT_DARK)
    
    draw.rounded_rectangle([w-180, by+12, w-20, by+40], radius=12, fill=(255, 243, 224))
    draw.text((w-165, by+16), "RFQ", fill=(200, 120, 20), font=FONT_SM)
    
    fy = by + 55
    fy = draw_dropdown_field(draw, 20, fy, "Vendor", "ABC Suppliers Pvt Ltd", w=350)
    
    # Deliver To with highlight
    draw.text((400, fy-52), "Deliver To", fill=TEXT_MID, font=FONT_SM)
    draw.rectangle([398, fy-32, 702, fy-4], outline=RED, width=2)
    draw.rectangle([400, fy-30, 700, fy-6], outline=BORDER, width=1, fill=(255, 255, 240))
    draw.text((410, fy-26), "Factory Building (FB)", fill=TEXT_DARK, font=FONT_REG)
    draw.text((665, fy-26), "▾", fill=TEXT_MID, font=FONT_SM)
    draw.text((710, fy-26), "← Receive goods here", fill=RED, font=FONT_MED)
    
    fy += 10
    draw_field(draw, 20, fy, "Order Deadline", "02/28/2026", w=200)
    
    # Order lines
    tby = fy + 65
    draw.text((20, tby), "Products", fill=TEXT_DARK, font=FONT_MED)
    tby += 28
    cols_h = ["Product", "Description", "Quantity", "Unit Price", "Tax", "Subtotal"]
    widths_h = [200, 260, 80, 100, 120, 120]
    tby = draw_table_row(draw, 20, tby, cols_h, widths_h, bg=(245, 247, 250), bold=True)
    tby = draw_table_row(draw, 20, tby, ["001GREY@1560", "Grey Fabric Roll 1560", "100.00", "₹560.00", "18% GST", "₹56,000.00"], widths_h)
    
    img.save('screenshots/03_purchase_order_deliver_to.png')
    print("  ✓ 03_purchase_order_deliver_to.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 4: Internal Transfer form
# ══════════════════════════════════════════════════════════════════
def create_internal_transfer():
    w, h = 1200, 520
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Inventory", "Transfers / New")
    
    draw_button(draw, 20, by+10, "Mark as To Do")
    draw_button(draw, 180, by+10, "Validate", color=WHITE, text_color=TEXT_DARK)
    
    fy = by + 55
    
    # Operation type
    fy = draw_dropdown_field(draw, 20, fy, "Operation Type", "Internal Transfer", w=300)
    
    # Source and destination - highlighted
    src_y = fy + 5
    draw.text((20, src_y), "Source Location", fill=TEXT_MID, font=FONT_SM)
    draw.rectangle([20, src_y+18, 320, src_y+44], outline=PURPLE_BTN, width=2, fill=WHITE)
    draw.text((28, src_y+22), "WH/Stock", fill=TEXT_DARK, font=FONT_REG)
    
    draw.text((30, src_y+50), "──────────────────────────→", fill=PURPLE_BTN, font=FONT_REG)
    
    draw.text((350, src_y), "Destination Location", fill=TEXT_MID, font=FONT_SM)
    draw.rectangle([350, src_y+18, 650, src_y+44], outline=PURPLE_BTN, width=2, fill=WHITE)
    draw.text((358, src_y+22), "NH GF/Stock", fill=TEXT_DARK, font=FONT_REG)
    
    draw.text((670, src_y+22), "Main WH → Branch Store", fill=GREEN, font=FONT_MED)
    
    # Products table
    tby = src_y + 90
    draw.text((20, tby), "Detailed Operations", fill=TEXT_DARK, font=FONT_MED)
    tby += 28
    cols_h = ["Product", "Demand", "Quantity Done", "Unit of Measure"]
    widths_h = [300, 120, 140, 150]
    tby = draw_table_row(draw, 20, tby, cols_h, widths_h, bg=(245, 247, 250), bold=True)
    tby = draw_table_row(draw, 20, tby, ["PVC Blinds", "20.000", "20.000", "Units"], widths_h)
    tby = draw_table_row(draw, 20, tby, ["ESS Mat (DWR)", "10.000", "10.000", "Units"], widths_h)
    
    img.save('screenshots/04_internal_transfer.png')
    print("  ✓ 04_internal_transfer.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 5: Inventory Settings - Multi-Step Routes
# ══════════════════════════════════════════════════════════════════
def create_multistep_settings():
    w, h = 1200, 400
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Settings", "Inventory / Settings")
    
    draw_button(draw, 20, by+10, "Save")
    draw_button(draw, 90, by+10, "Discard", color=WHITE, text_color=TEXT_DARK)
    
    fy = by + 55
    draw.text((20, fy), "Warehouse", fill=TEXT_DARK, font=FONT_XL)
    fy += 40
    
    draw.line([20, fy, w-20, fy], fill=BORDER, width=1)
    fy += 15
    
    # Storage Locations
    draw_checkbox(draw, 30, fy, "Storage Locations", checked=True)
    draw.text((220, fy+2), "Track products in specific locations within your warehouses", fill=TEXT_MID, font=FONT_SM)
    fy += 35
    
    # Multi-Step Routes - highlighted
    draw.rectangle([24, fy-4, 700, fy+28], outline=RED, width=2, fill=(255, 255, 240))
    draw_checkbox(draw, 30, fy, "Multi-Step Routes", checked=True)
    draw.text((220, fy+2), "Use routes with multiple steps to move products between locations", fill=TEXT_MID, font=FONT_SM)
    draw.text((710, fy), "← Enable this", fill=RED, font=FONT_MED)
    fy += 40
    
    # Resupply
    draw_checkbox(draw, 30, fy, "Resupply Between Warehouses", checked=True)
    draw.text((300, fy+2), "Automatically create inter-warehouse transfers", fill=TEXT_MID, font=FONT_SM)
    
    img.save('screenshots/05_multistep_routes.png')
    print("  ✓ 05_multistep_routes.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 6: Warehouse config with Resupply From
# ══════════════════════════════════════════════════════════════════
def create_warehouse_resupply():
    w, h = 1200, 460
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Inventory", "Warehouses / Near Home GF")
    
    draw_button(draw, 20, by+10, "Save")
    
    fy = by + 55
    draw_field(draw, 20, fy, "Warehouse Name", "Near Home GF", w=300)
    draw_field(draw, 340, fy, "Short Name", "NH GF", w=120)
    draw_field(draw, 480, fy, "Company", "Parappattu Group", w=250)
    
    fy += 65
    draw.text((20, fy), "Warehouse Configuration", fill=TEXT_DARK, font=FONT_MED)
    fy += 30
    draw.line([20, fy, w-20, fy], fill=BORDER, width=1)
    fy += 15
    
    # Resupply From section - highlighted
    draw.text((30, fy), "Resupply From", fill=TEXT_MID, font=FONT_SM)
    fy += 20
    draw.rectangle([26, fy-2, 500, fy+80], outline=RED, width=2, fill=(255, 255, 240))
    
    draw_checkbox(draw, 36, fy+5, "Parappattu Group (WH)", checked=True)
    draw_checkbox(draw, 36, fy+30, "Near Home FF (NH FF)", checked=False)
    draw_checkbox(draw, 36, fy+55, "Factory Building (FB)", checked=False)
    
    draw.text((510, fy+10), "← Check the supply warehouse", fill=RED, font=FONT_MED)
    draw.text((510, fy+40), "Stock will auto-transfer from", fill=TEXT_MID, font=FONT_REG)
    draw.text((510, fy+60), "checked warehouse(s) to this one", fill=TEXT_MID, font=FONT_REG)
    
    img.save('screenshots/06_warehouse_resupply.png')
    print("  ✓ 06_warehouse_resupply.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 7: Reordering Rule form
# ══════════════════════════════════════════════════════════════════
def create_reordering_rule():
    w, h = 1200, 420
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Inventory", "Replenishment / Reordering Rules")
    
    # Table header
    fy = by + 20
    cols = ["Product", "Location", "On Hand", "Forecast", "Min", "Max", "To Order", "Route"]
    widths = [180, 130, 80, 80, 70, 70, 80, 220]
    fy = draw_table_row(draw, 20, fy, cols, widths, bg=(245, 247, 250), bold=True)
    
    # Rows
    rows = [
        ["PVC Blinds", "NH GF/Stock", "5.00", "5.00", "10.00", "50.00", "45.00", "NH GF: Supply from Parappattu"],
        ["ESS Mat (DWR)", "NH GF/Stock", "0.00", "0.00", "5.00", "20.00", "20.00", "NH GF: Supply from Parappattu"],
        ["001GREY@1560", "NH FF/Stock", "2.00", "2.00", "10.00", "30.00", "28.00", "NH FF: Supply from Parappattu"],
    ]
    for i, row in enumerate(rows):
        bg = BG_LIGHT if i % 2 == 0 else WHITE
        fy = draw_table_row(draw, 20, fy, row, widths, bg=bg)
    
    # Highlight Min/Max columns
    fy += 20
    draw.text((20, fy), "Min = Trigger level (reorder when stock falls below this)", fill=TEXT_MID, font=FONT_SM)
    draw.text((20, fy+20), "Max = Target level (stock is replenished up to this quantity)", fill=TEXT_MID, font=FONT_SM)
    draw.text((20, fy+45), "Route = The resupply route that handles the automatic transfer", fill=PURPLE_BTN, font=FONT_SM)
    
    img.save('screenshots/07_reordering_rules.png')
    print("  ✓ 07_reordering_rules.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 8: Inter-Company Settings
# ══════════════════════════════════════════════════════════════════
def create_intercompany_settings():
    w, h = 1200, 480
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Settings", "General Settings")
    
    draw_button(draw, 20, by+10, "Save")
    draw_button(draw, 90, by+10, "Discard", color=WHITE, text_color=TEXT_DARK)
    
    fy = by + 55
    draw.text((20, fy), "Inter-Company Transactions", fill=TEXT_DARK, font=FONT_XL)
    fy += 35
    draw.line([20, fy, w-20, fy], fill=BORDER, width=1)
    fy += 15
    
    # Enable checkbox
    draw.rectangle([24, fy-4, 750, fy+140], outline=RED, width=2, fill=(255, 255, 245))
    
    draw_checkbox(draw, 36, fy, "Synchronize Sales & Purchase Orders", checked=True)
    fy += 30
    
    draw.text((60, fy), "When a sales order is confirmed for another company in this database,", fill=TEXT_MID, font=FONT_SM)
    draw.text((60, fy+18), "a purchase order is automatically created in the other company.", fill=TEXT_MID, font=FONT_SM)
    fy += 45
    
    draw_checkbox(draw, 60, fy, "Generate Purchase Orders", checked=True)
    draw.text((310, fy+2), "SO in Company A → auto PO in Company B", fill=TEXT_MID, font=FONT_SM)
    fy += 28
    
    draw_checkbox(draw, 60, fy, "Generate Sales Orders", checked=True)
    draw.text((310, fy+2), "PO in Company A → auto SO in Company B", fill=TEXT_MID, font=FONT_SM)
    fy += 28
    
    draw_checkbox(draw, 60, fy, "Generate Bills and Refunds", checked=True)
    draw.text((310, fy+2), "Invoice in Company A → auto Bill in Company B", fill=TEXT_MID, font=FONT_SM)
    
    draw.text((760, by+100), "← Enable all these\n   for automatic\n   inter-company flow", fill=RED, font=FONT_MED)
    
    img.save('screenshots/08_intercompany_settings.png')
    print("  ✓ 08_intercompany_settings.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 9: Inter-Company Flow (SO creates PO)
# ══════════════════════════════════════════════════════════════════
def create_intercompany_flow():
    w, h = 1200, 500
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    # Two panels side by side
    mid = w // 2
    
    # Left panel: Company A (Parappattu Group)
    draw.rectangle([0, 0, mid-5, h], fill=WHITE, outline=BORDER)
    draw.rectangle([0, 0, mid-5, 40], fill=NAVBAR_DARK)
    draw.text((15, 10), "Parappattu Group — Sales Order", fill=WHITE, font=FONT_MED)
    
    ly = 55
    draw.text((15, ly), "S00045", fill=TEXT_DARK, font=FONT_XL)
    draw.rounded_rectangle([130, ly+2, 230, ly+28], radius=10, fill=(212, 237, 218))
    draw.text((140, ly+6), "Confirmed", fill=GREEN, font=FONT_SM)
    ly += 40
    
    draw_field(draw, 15, ly, "Customer", "PSQUARE INTERIOR FURNISHING", w=mid-30)
    ly += 55
    draw.text((15, ly), "Product: PVC Blinds  |  Qty: 100  |  ₹1,25,000", fill=TEXT_DARK, font=FONT_REG)
    ly += 25
    draw.text((15, ly), "Tax: 18% GST  |  Total: ₹1,47,500", fill=TEXT_DARK, font=FONT_REG)
    
    # Arrow in the middle
    arrow_y = h // 2 - 30
    draw.text((mid-5, arrow_y-15), "Odoo automatically creates →", fill=PURPLE_BTN, font=FONT_MED)
    for i in range(3):
        draw.polygon([(mid-8, arrow_y+20+i*5), (mid+8, arrow_y+20+i*5), (mid, arrow_y+30+i*5)], fill=PURPLE_BTN)
    
    # Right panel: Company B (PSQUARE INTERIOR FURNISHING)
    draw.rectangle([mid+5, 0, w, h], fill=WHITE, outline=BORDER)
    draw.rectangle([mid+5, 0, w, 40], fill=(100, 60, 120))
    draw.text((mid+20, 10), "PSQUARE INTERIOR FURNISHING — Purchase Order", fill=WHITE, font=FONT_MED)
    
    ry = 55
    draw.text((mid+20, ry), "P00012", fill=TEXT_DARK, font=FONT_XL)
    draw.rounded_rectangle([mid+150, ry+2, mid+280, ry+28], radius=10, fill=(255, 243, 224))
    draw.text((mid+160, ry+6), "Auto-Created", fill=(200, 120, 20), font=FONT_SM)
    ry += 40
    
    draw_field(draw, mid+20, ry, "Vendor", "Parappattu Group", w=mid-80)
    ry += 55
    draw.text((mid+20, ry), "Product: PVC Blinds  |  Qty: 100  |  ₹1,25,000", fill=TEXT_DARK, font=FONT_REG)
    ry += 25
    draw.text((mid+20, ry), "Tax: 18% GST  |  Total: ₹1,47,500", fill=TEXT_DARK, font=FONT_REG)
    
    # Bottom note
    draw.rectangle([0, h-60, w, h], fill=(245, 247, 250))
    draw.text((20, h-50), "✓ When a Sales Order is confirmed in Parappattu Group for PSQUARE INTERIOR FURNISHING,", fill=GREEN, font=FONT_REG)
    draw.text((20, h-28), "  Odoo automatically creates a matching Purchase Order in PSQUARE INTERIOR FURNISHING.", fill=GREEN, font=FONT_REG)
    
    img.save('screenshots/09_intercompany_flow.png')
    print("  ✓ 09_intercompany_flow.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 10: Profit and Loss Report
# ══════════════════════════════════════════════════════════════════
def create_profit_loss():
    w, h = 1200, 520
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Accounting", "Reporting / Profit and Loss")
    
    # Period selector
    draw.rounded_rectangle([20, by+10, 200, by+38], radius=4, fill=WHITE, outline=BORDER)
    draw.text((30, by+14), "January 2026 ▾", fill=TEXT_DARK, font=FONT_REG)
    
    draw.rounded_rectangle([210, by+10, 340, by+38], radius=4, fill=WHITE, outline=BORDER)
    draw.text((220, by+14), "Posted Entries", fill=TEXT_DARK, font=FONT_REG)
    
    fy = by + 55
    
    # P&L table
    draw.text((20, fy), "Profit and Loss", fill=TEXT_DARK, font=FONT_XL)
    draw.text((250, fy+4), "Parappattu Group", fill=TEXT_MID, font=FONT_REG)
    fy += 35
    
    cols = ["", "January 2026"]
    widths = [500, 200]
    fy = draw_table_row(draw, 20, fy, cols, widths, bg=(245, 247, 250), bold=True)
    
    rows = [
        ("Revenue", "₹8,45,200.00", TEXT_DARK, True),
        ("  Product Sales", "₹7,92,000.00", TEXT_DARK, False),
        ("  Service Income", "₹53,200.00", TEXT_DARK, False),
        ("Cost of Revenue", "₹4,12,600.00", TEXT_DARK, True),
        ("Gross Profit", "₹4,32,600.00", GREEN, True),
        ("Operating Expenses", "₹2,85,400.00", TEXT_DARK, True),
        ("  Salaries & Wages", "₹1,80,000.00", TEXT_DARK, False),
        ("  Rent", "₹65,000.00", TEXT_DARK, False),
        ("  Utilities", "₹40,400.00", TEXT_DARK, False),
        ("Net Profit", "₹1,47,200.00", GREEN, True),
    ]
    
    for label, amount, color, bold in rows:
        font = FONT_MED if bold else FONT_REG
        bg = BG_LIGHT if bold else WHITE
        draw.rectangle([20, fy, 720, fy+32], fill=bg)
        draw.line([20, fy+32, 720, fy+32], fill=BORDER, width=1)
        draw.text((30, fy+6), label, fill=TEXT_DARK, font=font)
        draw.text((560, fy+6), amount, fill=color, font=font)
        fy += 32
    
    img.save('screenshots/10_profit_loss.png')
    print("  ✓ 10_profit_loss.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 11: Trial Balance with Hierarchy
# ══════════════════════════════════════════════════════════════════
def create_trial_balance():
    w, h = 1200, 480
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Accounting", "Reporting / Trial Balance")
    
    # Options bar
    draw.rounded_rectangle([20, by+10, 160, by+38], radius=4, fill=WHITE, outline=BORDER)
    draw.text((30, by+14), "Posted Entries ▾", fill=TEXT_DARK, font=FONT_REG)
    
    # Hierarchy toggle highlighted
    draw.rectangle([168, by+8, 400, by+40], outline=RED, width=2, fill=(255, 255, 240))
    draw_checkbox(draw, 175, by+14, "Hierarchy and Subtotals", checked=True)
    draw.text((410, by+14), "← Enable this", fill=RED, font=FONT_MED)
    
    fy = by + 55
    cols = ["Account", "Debit", "Credit", "Balance"]
    widths = [450, 150, 150, 150]
    fy = draw_table_row(draw, 20, fy, cols, widths, bg=(245, 247, 250), bold=True)
    
    hier_rows = [
        ("▼ Assets", "₹12,45,000", "", "₹12,45,000", True, 0),
        ("  ▼ Current Assets", "₹8,20,000", "", "₹8,20,000", True, 1),
        ("    ▼ Bank and Cash", "₹5,60,000", "", "₹5,60,000", True, 2),
        ("      100001 — HDFC Bank", "₹3,20,000", "", "₹3,20,000", False, 3),
        ("      100002 — SIB Bank", "₹2,40,000", "", "₹2,40,000", False, 3),
        ("    ▼ Receivables", "₹2,60,000", "", "₹2,60,000", True, 2),
        ("▼ Income", "", "₹8,45,200", "₹8,45,200", True, 0),
        ("  Product Sales", "", "₹7,92,000", "₹7,92,000", False, 1),
    ]
    
    for label, debit, credit, balance, bold, indent in hier_rows:
        font = FONT_MED if bold else FONT_REG
        bg = BG_LIGHT if bold else WHITE
        draw.rectangle([20, fy, 920, fy+32], fill=bg)
        draw.line([20, fy+32, 920, fy+32], fill=BORDER, width=1)
        color = PURPLE_BTN if bold else TEXT_DARK
        draw.text((30 + indent*10, fy+6), label, fill=color, font=font)
        if debit:
            draw.text((480, fy+6), debit, fill=TEXT_DARK, font=font)
        if credit:
            draw.text((630, fy+6), credit, fill=TEXT_DARK, font=font)
        draw.text((780, fy+6), balance, fill=TEXT_DARK, font=font)
        fy += 32
    
    img.save('screenshots/11_trial_balance.png')
    print("  ✓ 11_trial_balance.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 12: Analytic Plans for Branches
# ══════════════════════════════════════════════════════════════════
def create_analytic_plans():
    w, h = 1200, 420
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Accounting", "Configuration / Analytic Plans")
    
    draw_button(draw, 20, by+10, "New")
    
    fy = by + 55
    draw.text((20, fy), "Analytic Plan: Branches", fill=TEXT_DARK, font=FONT_XL)
    fy += 40
    
    draw.text((20, fy), "Analytic Accounts", fill=TEXT_DARK, font=FONT_MED)
    fy += 30
    
    cols = ["Name", "Reference", "Company"]
    widths = [300, 200, 250]
    fy = draw_table_row(draw, 20, fy, cols, widths, bg=(245, 247, 250), bold=True)
    
    accounts = [
        ("Georgeon Furniture", "BRANCH-GF", "Parappattu Group"),
        ("PSQUARE INTERIOR", "BRANCH-PSI", "Parappattu Group"),
        ("Near Home GF Store", "BRANCH-NHGF", "Parappattu Group"),
        ("Near Home FF Store", "BRANCH-NHFF", "Parappattu Group"),
        ("Factory Building", "BRANCH-FB", "Parappattu Group"),
    ]
    for i, (name, ref, company) in enumerate(accounts):
        bg = BG_LIGHT if i % 2 == 0 else WHITE
        fy = draw_table_row(draw, 20, fy, [name, ref, company], widths, bg=bg)
    
    img.save('screenshots/12_analytic_plans.png')
    print("  ✓ 12_analytic_plans.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 13: Inventory Report by Warehouse
# ══════════════════════════════════════════════════════════════════
def create_inventory_report():
    w, h = 1200, 450
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Inventory", "Reporting / Inventory Report")
    
    # Group by indicator
    draw.rounded_rectangle([20, by+10, 220, by+38], radius=4, fill=(230, 240, 255))
    draw.text((30, by+14), "Grouped by: Warehouse", fill=PURPLE_BTN, font=FONT_SM)
    
    fy = by + 55
    cols = ["Product", "Location", "On Hand Qty", "Forecasted Qty", "Unit"]
    widths = [250, 180, 120, 130, 80]
    fy = draw_table_row(draw, 20, fy, cols, widths, bg=(245, 247, 250), bold=True)
    
    # Parappattu Group WH section
    draw.rectangle([20, fy, 780, fy+30], fill=(235, 238, 255))
    draw.text((30, fy+5), "▼ Parappattu Group (WH)", fill=PURPLE_BTN, font=FONT_MED)
    fy += 30
    
    wh_rows = [
        ("PVC Blinds", "WH/Stock", "137.50", "137.50", "Units"),
        ("001GREY@1560", "WH/Stock", "8.00", "8.00", "Units"),
        ("ESS Mat (DWR)", "WH/Fifth Floor", "10.00", "10.00", "Units"),
    ]
    for i, row in enumerate(wh_rows):
        bg = BG_LIGHT if i % 2 == 0 else WHITE
        fy = draw_table_row(draw, 20, fy, row, widths, bg=bg)
    
    # NH GF section
    draw.rectangle([20, fy, 780, fy+30], fill=(235, 238, 255))
    draw.text((30, fy+5), "▼ Near Home GF (NH GF)", fill=PURPLE_BTN, font=FONT_MED)
    fy += 30
    
    nhgf_rows = [
        ("PVC Blinds", "NH GF/Stock", "25.00", "25.00", "Units"),
    ]
    for i, row in enumerate(nhgf_rows):
        fy = draw_table_row(draw, 20, fy, row, widths, bg=BG_LIGHT)
    
    # NH FF section  
    draw.rectangle([20, fy, 780, fy+30], fill=(235, 238, 255))
    draw.text((30, fy+5), "▼ Near Home FF (NH FF)", fill=PURPLE_BTN, font=FONT_MED)
    fy += 30
    
    img.save('screenshots/13_inventory_report.png')
    print("  ✓ 13_inventory_report.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 14: New Company creation form
# ══════════════════════════════════════════════════════════════════
def create_new_company():
    w, h = 1200, 420
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Settings", "Companies / New")
    
    draw_button(draw, 20, by+10, "Save")
    draw_button(draw, 90, by+10, "Discard", color=WHITE, text_color=TEXT_DARK)
    
    fy = by + 55
    fy = draw_field(draw, 20, fy, "Company Name", "New Company Name", w=400)
    fy = draw_dropdown_field(draw, 20, fy, "Parent Company", "(leave blank for independent)", w=400)
    
    draw_field(draw, 450, fy-104, "Tax ID / GSTIN", "Enter GSTIN", w=300)
    draw_field(draw, 450, fy-52, "Country", "India", w=300)
    
    fy += 10
    draw.text((20, fy), "General Information", fill=TEXT_DARK, font=FONT_MED)
    fy += 30
    draw_field(draw, 20, fy, "Address", "Full business address", w=400)
    draw_field(draw, 450, fy, "State", "Kerala (IN)", w=300)
    
    fy += 65
    draw.rectangle([20, fy, w-20, fy+50], fill=(245, 250, 255))
    draw.text((30, fy+8), "💡 Set Parent Company to create a branch under an existing company.", fill=PURPLE_BTN, font=FONT_REG)
    draw.text((30, fy+28), "    Leave Parent Company blank to create an independent company with its own books.", fill=TEXT_MID, font=FONT_SM)
    
    img.save('screenshots/14_new_company.png')
    print("  ✓ 14_new_company.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 15: New Warehouse creation
# ══════════════════════════════════════════════════════════════════
def create_new_warehouse():
    w, h = 1200, 420
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Inventory", "Warehouses / New")
    
    draw_button(draw, 20, by+10, "Save")
    
    fy = by + 55
    fy = draw_field(draw, 20, fy, "Warehouse Name", "New Store Name", w=350)
    draw_field(draw, 390, fy-52, "Short Name", "CODE", w=120)
    draw_dropdown_field(draw, 530, fy-52, "Company", "Select Company", w=250)
    
    fy += 10
    draw.text((20, fy), "Warehouse Configuration", fill=TEXT_DARK, font=FONT_MED)
    fy += 30
    draw.line([20, fy, w-20, fy], fill=BORDER, width=1)
    fy += 15
    
    draw.text((30, fy), "Incoming Shipments:", fill=TEXT_MID, font=FONT_SM)
    draw.text((200, fy), "Receive in 1 step (stock)", fill=TEXT_DARK, font=FONT_REG)
    fy += 28
    draw.text((30, fy), "Outgoing Shipments:", fill=TEXT_MID, font=FONT_SM)
    draw.text((200, fy), "Deliver in 1 step (ship)", fill=TEXT_DARK, font=FONT_REG)
    fy += 35
    
    draw_checkbox(draw, 30, fy, "Buy to Resupply", checked=True)
    fy += 28
    draw_checkbox(draw, 30, fy, "Resupply From", checked=False)
    draw.text((220, fy+2), "Enable to auto-receive stock from another warehouse", fill=TEXT_MID, font=FONT_SM)
    
    img.save('screenshots/15_new_warehouse.png')
    print("  ✓ 15_new_warehouse.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 16: Analytic Accounting Settings toggle
# ══════════════════════════════════════════════════════════════════
def create_analytic_settings():
    w, h = 1200, 340
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Settings", "Accounting / Settings")
    
    draw_button(draw, 20, by+10, "Save")
    draw_button(draw, 90, by+10, "Discard", color=WHITE, text_color=TEXT_DARK)
    
    fy = by + 55
    draw.text((20, fy), "Analytics", fill=TEXT_DARK, font=FONT_XL)
    fy += 35
    draw.line([20, fy, w-20, fy], fill=BORDER, width=1)
    fy += 15
    
    draw.rectangle([24, fy-4, 620, fy+28], outline=RED, width=2, fill=(255, 255, 240))
    draw_checkbox(draw, 36, fy, "Analytic Accounting", checked=True)
    draw.text((240, fy+2), "Track costs and revenues by analytic account", fill=TEXT_MID, font=FONT_SM)
    draw.text((630, fy), "← Enable this for branch tracking", fill=RED, font=FONT_MED)
    
    fy += 40
    draw_checkbox(draw, 36, fy, "Analytic Plans", checked=True)
    draw.text((240, fy+2), "Create plans to organise analytic accounts", fill=TEXT_MID, font=FONT_SM)
    
    img.save('screenshots/16_analytic_settings.png')
    print("  ✓ 16_analytic_settings.png")

# ══════════════════════════════════════════════════════════════════
# SCREENSHOT 17: P&L filtered by Analytic
# ══════════════════════════════════════════════════════════════════
def create_pl_analytic():
    w, h = 1200, 480
    img = Image.new('RGBA', (w, h), WHITE)
    draw = ImageDraw.Draw(img)
    
    by = draw_navbar(draw, w, "Accounting", "Reporting / Profit and Loss")
    
    # Filter bar
    draw.rounded_rectangle([20, by+10, 200, by+38], radius=4, fill=WHITE, outline=BORDER)
    draw.text((30, by+14), "January 2026 ▾", fill=TEXT_DARK, font=FONT_REG)
    
    draw.rectangle([208, by+8, 420, by+40], outline=RED, width=2, fill=(255, 255, 240))
    draw.text((218, by+14), "Analytic: Branches ▾", fill=PURPLE_BTN, font=FONT_REG)
    draw.text((430, by+14), "← Filter by branch", fill=RED, font=FONT_MED)
    
    fy = by + 55
    draw.text((20, fy), "Profit and Loss by Branch", fill=TEXT_DARK, font=FONT_XL)
    fy += 35
    
    # Multi-column P&L
    cols = ["", "Georgeon\nFurniture", "PSQUARE\nINTERIOR", "Near Home\nGF", "Near Home\nFF", "Total"]
    widths = [250, 130, 130, 120, 120, 130]
    fy = draw_table_row(draw, 20, fy, ["", "Georgeon", "PSQUARE INT", "NH GF", "NH FF", "Total"], widths, bg=(245, 247, 250), bold=True)
    
    fin_rows = [
        ("Revenue", "₹2,10,000", "₹1,85,000", "₹3,20,000", "₹1,30,200", "₹8,45,200", True),
        ("Cost of Revenue", "₹1,02,000", "₹90,000", "₹1,55,000", "₹65,600", "₹4,12,600", True),
        ("Gross Profit", "₹1,08,000", "₹95,000", "₹1,65,000", "₹64,600", "₹4,32,600", True),
        ("Expenses", "₹72,000", "₹68,000", "₹98,000", "₹47,400", "₹2,85,400", True),
        ("Net Profit", "₹36,000", "₹27,000", "₹67,000", "₹17,200", "₹1,47,200", True),
    ]
    
    for label, *vals, bold in fin_rows:
        bg = BG_LIGHT if label in ("Revenue", "Gross Profit", "Net Profit") else WHITE
        font = FONT_MED if bold else FONT_REG
        draw.rectangle([20, fy, 900, fy+32], fill=bg)
        draw.line([20, fy+32, 900, fy+32], fill=BORDER, width=1)
        draw.text((30, fy+6), label, fill=TEXT_DARK, font=font)
        cx = 270
        for v in vals:
            color = GREEN if label == "Net Profit" else TEXT_DARK
            draw.text((cx, fy+6), v, fill=color, font=FONT_SM)
            cx += 130 if cx < 640 else 120
        fy += 32
    
    img.save('screenshots/17_pl_by_analytic.png')
    print("  ✓ 17_pl_by_analytic.png")

# ══════════════════════════════════════════════════════════════════
# RUN ALL
# ══════════════════════════════════════════════════════════════════
print("Generating Odoo 19 mock screenshots...\n")
create_company_selector()
create_sales_order()
create_purchase_order()
create_internal_transfer()
create_multistep_settings()
create_warehouse_resupply()
create_reordering_rule()
create_intercompany_settings()
create_intercompany_flow()
create_profit_loss()
create_trial_balance()
create_analytic_plans()
create_inventory_report()
create_new_company()
create_new_warehouse()
create_analytic_settings()
create_pl_analytic()
print(f"\nDone! All screenshots saved to screenshots/ folder")
