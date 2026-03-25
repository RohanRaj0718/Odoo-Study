"""
Build Odoo Website Homepage via Web Session API (Odoo.sh compatible)
"""
import json
import requests
import sys

URL = "https://rohanraj0718-infintor.odoo.com"
DB = "rohanraj0718-infintor-main-29796979"
USERNAME = "rohanraj.infintor@gmail.com"
PASSWORD = "Virat@ronaldo1"

def main():
    session = requests.Session()
    
    # Step 1: Authenticate via web session
    print("Authenticating via web session...")
    auth_resp = session.post(f"{URL}/web/session/authenticate", json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "db": DB,
            "login": USERNAME,
            "password": PASSWORD,
        },
        "id": 1
    })
    auth_result = auth_resp.json()
    
    if "error" in auth_result:
        print(f"Auth error: {json.dumps(auth_result['error'], indent=2)[:300]}")
        sys.exit(1)
    
    result = auth_result.get("result", {})
    uid = result.get("uid")
    if not uid:
        print(f"Auth failed, result: {json.dumps(result, indent=2)[:300]}")
        sys.exit(1)
    
    print(f"Authenticated as UID: {uid}, username: {result.get('username')}")
    
    # Step 2: Find homepage view using web dataset call
    print("\nFinding homepage view...")
    search_resp = session.post(f"{URL}/web/dataset/call_kw", json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "ir.ui.view",
            "method": "search_read",
            "args": [[["key", "like", "website.homepage"]]],
            "kwargs": {
                "fields": ["id", "name", "key", "arch_db"],
                "limit": 5
            }
        },
        "id": 2
    })
    search_result = search_resp.json()
    
    if "error" in search_result:
        print(f"Search error: {json.dumps(search_result['error'], indent=2)[:400]}")
        sys.exit(1)
    
    views = search_result.get("result", [])
    if not views:
        print("No homepage view found. Trying alternative search...")
        search_resp2 = session.post(f"{URL}/web/dataset/call_kw", json={
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "ir.ui.view",
                "method": "search_read",
                "args": [[["name", "ilike", "homepage"]]],
                "kwargs": {
                    "fields": ["id", "name", "key", "arch_db"],
                    "limit": 5
                }
            },
            "id": 3
        })
        views = search_resp2.json().get("result", [])
    
    if not views:
        print("Still no views found!")
        sys.exit(1)
    
    homepage_view = views[0]
    view_id = homepage_view['id']
    print(f"Found: ID={view_id}, Key={homepage_view['key']}, Name={homepage_view['name']}")
    print(f"\nCurrent arch:\n{homepage_view['arch_db'][:500]}")
    print("...\n")

    # Step 3: Build the new homepage HTML
    # We need to keep the outer QWeb template structure and only replace the inner content
    current_arch = homepage_view['arch_db']
    
    # The new body content
    new_body = '''
  <!-- HERO SECTION -->
  <section class="s_cover parallax s_parallax_is_fixed pt160 pb160 s_parallax_no_overflow_hidden" data-scroll-background-ratio="1" data-snippet="s_cover" style="background-image: url('/web/image/website.s_cover_default_image'); min-height: 600px;">
    <span class="s_parallax_bg oe_img_bg" style="background-image: url('/web/image/website.s_cover_default_image'); background-position: center center;"/>
    <div class="o_we_bg_filter bg-black-50"/>
    <div class="container">
      <div class="row s_nb_column_fixed">
        <div class="col-lg-12 s_col_no_bgcolor pt40 pb40" style="text-align: center;">
          <h1 style="text-align: center;"><font style="font-size: 48px; color: #ffffff;">&#8212; Your Gateway to Authentic Indian Adventures &#8212;</font></h1>
          <p style="text-align: center;"><font style="font-size: 20px; color: #ffffff;">Contact Us for Unforgettable Packages!</font></p>
          <p style="text-align: center;"><a href="/contactus" class="btn btn-primary btn-lg rounded-pill" style="background-color: #001C47; border-color: #001C47; padding: 12px 40px;">Contact Us</a></p>
        </div>
      </div>
    </div>
  </section>

  <!-- WHO WE ARE -->
  <section class="s_text_image pt48 pb48" data-snippet="s_text_image" style="background-color: #ffffff;">
    <div class="container">
      <div class="row s_nb_column_fixed">
        <div class="col-lg-6 pt16 pb16">
          <h2 style="color: #001C47;"><b>Who We Are</b></h2>
          <p style="font-size: 16px; line-height: 1.8; color: #555555;">We are <b>Infintor Solutions</b>, your trusted partner in digital transformation. We specialize in delivering cutting-edge ERP solutions powered by Odoo, helping businesses streamline their operations and accelerate growth.</p>
          <p style="font-size: 16px; line-height: 1.8; color: #555555;">With a team of certified consultants and deep domain expertise, we craft tailored solutions that align perfectly with your business objectives. From implementation to customization, training to support &#8212; we are with you every step of the way.</p>
        </div>
        <div class="col-lg-6 pt16 pb16" style="text-align: center;">
          <img src="/web/image/website.s_text_image_default_image" alt="Who We Are" class="img img-fluid mx-auto rounded-circle shadow" style="max-width: 400px; border: 5px solid #f0f0f0;"/>
        </div>
      </div>
    </div>
  </section>

  <!-- PROMO BANNER -->
  <section class="s_text_block pt48 pb48" data-snippet="s_text_block" style="background-color: #f8f9fa;">
    <div class="container">
      <div class="row s_nb_column_fixed">
        <div class="col-lg-12" style="text-align: center;">
          <h2 style="color: #001C47; font-size: 36px;"><b>Transform Your Business with Odoo ERP Solutions</b></h2>
          <p style="font-size: 18px; color: #666666; max-width: 700px; margin: 20px auto;">Let us help you build a seamless, integrated business ecosystem. Our expert team delivers personalized solutions for your unique challenges.</p>
          <p><a href="/contactus" class="btn btn-primary btn-lg rounded-pill" style="background-color: #001C47; border-color: #001C47; padding: 12px 40px;">Get Started Today</a></p>
        </div>
      </div>
    </div>
  </section>

  <!-- SERVICES GRID -->
  <section class="s_three_columns pt48 pb48" data-snippet="s_three_columns" style="background-color: #ffffff;">
    <div class="container">
      <div class="row s_nb_column_fixed" style="text-align: center;">
        <div class="col-lg-12 pb32">
          <h2 style="color: #001C47;"><b>Our Core Services</b></h2>
        </div>
      </div>
      <div class="row s_nb_column_fixed">
        <div class="col-lg-4 pt16 pb16">
          <div class="card shadow-sm border-0 h-100" style="border-radius: 12px; overflow: hidden;">
            <img src="/web/image/website.s_three_columns_default_image_1" alt="ERP Implementation" class="card-img-top" style="height: 200px; object-fit: cover;"/>
            <div class="card-body" style="padding: 24px;">
              <h4 style="color: #001C47;"><b>ERP Implementation</b></h4>
              <p style="color: #666666;">End-to-end Odoo ERP implementation tailored to your business processes. We ensure smooth deployment and minimal disruption.</p>
            </div>
          </div>
        </div>
        <div class="col-lg-4 pt16 pb16">
          <div class="card shadow-sm border-0 h-100" style="border-radius: 12px; overflow: hidden;">
            <img src="/web/image/website.s_three_columns_default_image_2" alt="Custom Development" class="card-img-top" style="height: 200px; object-fit: cover;"/>
            <div class="card-body" style="padding: 24px;">
              <h4 style="color: #001C47;"><b>Custom Development</b></h4>
              <p style="color: #666666;">Bespoke Odoo modules and integrations designed to extend your ERP capabilities and meet unique business requirements.</p>
            </div>
          </div>
        </div>
        <div class="col-lg-4 pt16 pb16">
          <div class="card shadow-sm border-0 h-100" style="border-radius: 12px; overflow: hidden;">
            <img src="/web/image/website.s_three_columns_default_image_3" alt="Training and Support" class="card-img-top" style="height: 200px; object-fit: cover;"/>
            <div class="card-body" style="padding: 24px;">
              <h4 style="color: #001C47;"><b>Training and Support</b></h4>
              <p style="color: #666666;">Comprehensive training programs and 24/7 support to ensure your team gets the most out of your Odoo investment.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- WHY CHOOSE US -->
  <section class="s_text_block pt48 pb48" data-snippet="s_text_block" style="background-color: #001C47;">
    <div class="container">
      <div class="row s_nb_column_fixed">
        <div class="col-lg-12" style="text-align: center;">
          <h2 style="color: #ffffff; font-size: 36px; margin-bottom: 40px;"><b>Why Choose Infintor?</b></h2>
        </div>
      </div>
      <div class="row s_nb_column_fixed">
        <div class="col-lg-4 pt16 pb16" style="text-align: center;">
          <h4 style="color: #ffffff;"><b>Certified Experts</b></h4>
          <p style="color: #cccccc;">Our team consists of Odoo-certified professionals with deep industry knowledge and hands-on implementation experience.</p>
        </div>
        <div class="col-lg-4 pt16 pb16" style="text-align: center;">
          <h4 style="color: #ffffff;"><b>Tailored Solutions</b></h4>
          <p style="color: #cccccc;">Every business is unique. We customize Odoo to fit your specific workflows, ensuring maximum efficiency and ROI.</p>
        </div>
        <div class="col-lg-4 pt16 pb16" style="text-align: center;">
          <h4 style="color: #ffffff;"><b>Dedicated Support</b></h4>
          <p style="color: #cccccc;">Round-the-clock support and maintenance to keep your systems running smoothly. We are always just a call away.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA -->
  <section class="s_text_block pt64 pb64" data-snippet="s_text_block" style="background-color: #f8f9fa;">
    <div class="container">
      <div class="row s_nb_column_fixed">
        <div class="col-lg-12" style="text-align: center;">
          <h2 style="color: #001C47; font-size: 36px;"><b>Ready to Transform Your Business?</b></h2>
          <p style="font-size: 18px; color: #666666; margin: 20px auto; max-width: 600px;">Get in touch with our experts today and discover how Odoo can revolutionize the way you work.</p>
          <p style="margin-top: 30px;"><a href="/contactus" class="btn btn-primary btn-lg rounded-pill" style="background-color: #001C47; border-color: #001C47; padding: 15px 50px; font-size: 18px;">Contact Us Now</a></p>
        </div>
      </div>
    </div>
  </section>
'''

    # Step 4: Construct new arch based on current structure
    # The standard Odoo homepage template format
    import re
    
    # Check if the current arch uses t-call="website.layout"
    if 'website.layout' in current_arch:
        # Find the oe_structure div and replace its content
        # Pattern: <div id="wrap" class="oe_structure...">...</div> before closing </t>
        pattern = r'(<div\s+id=["\']wrap["\']\s+class=["\'][^"\']*oe_structure[^"\']*["\']>)(.*?)(</div>\s*</t>\s*</t>)'
        new_arch = re.sub(pattern, 
            r'\g<1>' + new_body + r'\3', 
            current_arch, 
            flags=re.DOTALL)
    else:
        # Build from scratch
        new_arch = f'''<t name="Homepage" t-name="website.homepage">
    <t t-call="website.layout">
        <t t-set="pageName" t-value="'homepage'"/>
        <div id="wrap" class="oe_structure oe_empty">
{new_body}
        </div>
    </t>
</t>'''
    
    print(f"New arch length: {len(new_arch)} chars")
    print(f"New arch preview:\n{new_arch[:400]}...\n")
    
    # Step 5: Update the view
    print("Updating homepage view...")
    write_resp = session.post(f"{URL}/web/dataset/call_kw", json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "ir.ui.view",
            "method": "write",
            "args": [[view_id], {"arch_db": new_arch}],
            "kwargs": {}
        },
        "id": 4
    })
    write_result = write_resp.json()
    
    if "error" in write_result:
        print(f"Write error: {json.dumps(write_result['error'], indent=2)[:500]}")
        
        # If writing arch_db fails, try arch
        print("\nTrying with 'arch' field instead...")
        write_resp2 = session.post(f"{URL}/web/dataset/call_kw", json={
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "ir.ui.view",
                "method": "write",
                "args": [[view_id], {"arch": new_arch}],
                "kwargs": {}
            },
            "id": 5
        })
        write_result2 = write_resp2.json()
        if "error" in write_result2:
            print(f"Write error (method 2): {json.dumps(write_result2['error'], indent=2)[:500]}")
        else:
            print(f"✅ Homepage updated successfully (method 2)!")
            print(f"View at: {URL}/")
    else:
        result_val = write_result.get("result")
        print(f"Write result: {result_val}")
        if result_val:
            print(f"\n✅ Homepage updated successfully!")
            print(f"View at: {URL}/")
        else:
            print(f"\n❌ Write returned: {result_val}")

if __name__ == "__main__":
    main()
