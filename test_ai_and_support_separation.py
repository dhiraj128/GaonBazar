import asyncio
import os
import sys
import io
from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def run_tests():
    print("======================================================================")
    print("AI ASSISTANT & SUPPORT CENTER SEPARATION OF CONCERNS VERIFICATION")
    print("======================================================================")
    
    file_path = os.path.abspath("index.html")
    file_url = f"file:///{file_path.replace(os.sep, '/')}"
    
    passed = 0
    total = 0
    
    def record(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  ✓ PASS: {name} - {details}")
        else:
            print(f"  ✗ FAIL: {name} - {details}")
            
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 393, "height": 852}, is_mobile=True)
        page = await context.new_page()
        
        await page.goto(file_url)
        await page.wait_for_timeout(600)
        
        # Navigate to dashboard
        await page.evaluate("navigateToPhase('dashboard')")
        await page.wait_for_timeout(400)
        
        # ====================================================================
        # MODULE 1: COMMERCE AI ASSISTANT (BOTTOM NAVIGATION)
        # ====================================================================
        print("\n--- MODULE 1: Commerce AI Assistant (Bottom Navigation) ---")
        
        # 1. Bottom navigation tab order: strictly [Stores, Categories, AI Assistant, Orders]
        tabs = await page.evaluate("""() => {
            const nav = document.getElementById('customer-bottom-nav');
            if (!nav) return [];
            return Array.from(nav.children).filter(el => el.tagName === 'BUTTON').map(b => b.id);
        }""")
        record("Bottom Nav Exactly 4 Tabs", len(tabs) == 4, f"Found {len(tabs)} tabs: {tabs}")
        expected_tabs = ['nav-btn-stores', 'nav-btn-categories', 'nav-btn-ai', 'nav-btn-orders']
        record("Bottom Nav Tab Order Strictly [Stores, Categories, AI Assistant, Orders]", 
               tabs == expected_tabs, f"Order: {tabs}")
        
        # 2. Tab 3 has Microphone / AI icon
        has_mic_icon = await page.locator("#nav-btn-ai .material-symbols-outlined:has-text('mic')").count() > 0
        record("AI Assistant Tab Displays Prominent Microphone Icon", has_mic_icon, "Found 'mic' icon in nav-btn-ai")
        
        # 3. Clicking AI Assistant tab navigates to #view-commerce-ai
        await page.click("#nav-btn-ai")
        await page.wait_for_timeout(400)
        
        is_commerce_ai_visible = await page.is_visible("#view-commerce-ai")
        record("Navigates to #view-commerce-ai", is_commerce_ai_visible, "Commerce AI screen is active")
        
        is_bottom_nav_visible_on_ai = await page.is_visible("#customer-bottom-nav")
        record("Bottom Nav Persists on Commerce AI Screen", is_bottom_nav_visible_on_ai, "Bottom nav remains accessible")
        
        # 4. Voice-First interface with prominent Microphone touch button
        mic_btn = page.locator("#commerce-ai-mic-btn")
        record("Prominent Microphone Button Exists", await mic_btn.count() == 1, "commerce-ai-mic-btn rendered")
        mic_box = await mic_btn.bounding_box()
        record("Microphone Touch Target Large (>= 72px)", mic_box["width"] >= 72 and mic_box["height"] >= 72, 
               f"Dimensions: {mic_box['width']}x{mic_box['height']}px")
        
        # 5. NLP Query Execution: "I want 1kg Aata and 1 packet Milk"
        print("  Testing Voice/Text Parsing: 'I want 1kg Aata and 1 packet Milk'")
        await page.evaluate("processCommerceAiQuery('I want 1kg Aata and 1 packet Milk')")
        await page.wait_for_timeout(400)
        
        matched_cards = await page.locator("#commerce-ai-results [id^='commerce-card-']").count()
        record("AI Parses Multiple Items & Renders Product Cards", matched_cards >= 2, f"Rendered {matched_cards} cards")
        
        # Verify Aata and Milk cards are present
        has_aata = await page.locator("#commerce-card-item_1").count() == 1
        has_milk = await page.locator("#commerce-card-item_d1").count() == 1
        record("Aashirvaad Chakki Atta Card Rendered", has_aata, "Found item_1 card")
        record("Amul Taaza Milk Card Rendered", has_milk, "Found item_d1 card")
        
        # 6. Direct "Add to Cart" button on product cards
        add_btn_aata = page.locator("#commerce-card-item_1 button:has-text('Add to Cart'), #commerce-card-item_1 button:has-text('कार्ट में जोड़ें')")
        record("Card Has Direct 'Add to Cart' CTA Button", await add_btn_aata.count() == 1, "Add to Cart button present")
        
        # Click Add to Cart for Aata
        initial_cart_badge = await page.inner_text("#header-cart-badge")
        await add_btn_aata.click()
        await page.wait_for_timeout(300)
        
        new_cart_badge = await page.inner_text("#header-cart-badge")
        record("Clicking Add to Cart Increments Cart Badge", int(new_cart_badge) > int(initial_cart_badge), 
               f"Badge went from {initial_cart_badge} to {new_cart_badge}")
        
        # Verify sticky "View Cart & Checkout" bar is visible
        is_cart_bar_visible = await page.is_visible("#commerce-view-cart-bar")
        record("Sticky View Cart & Checkout Bar Unhidden", is_cart_bar_visible, "Cart CTA bar active")
        
        # ====================================================================
        # MODULE 2: SUPPORT AI CHAT (SIDEBAR MENU)
        # ====================================================================
        print("\n--- MODULE 2: Support AI Chat (Sidebar Menu) ---")
        
        # 1. Return to dashboard and open Hamburger menu
        await page.evaluate("navigateToPhase('dashboard')")
        await page.wait_for_timeout(300)
        await page.evaluate("openSidebarDrawer()")
        await page.wait_for_timeout(300)
        
        # 2. Check for "AI Order Support" menu item
        ai_support_item = page.locator("#drawer-support-ai-btn")
        record("Sidebar Drawer Contains 'AI Order Support' Menu Item", await ai_support_item.count() == 1, 
               "drawer-support-ai-btn exists")
        
        # 3. Clicking "AI Order Support" opens #modal-support-chat
        await page.evaluate("document.getElementById('drawer-support-ai-btn').click()")
        await page.wait_for_timeout(400)
        
        is_chat_modal_visible = await page.is_visible("#modal-support-chat")
        record("Clicking 'AI Order Support' Opens Support Chat Overlay", is_chat_modal_visible, "Chat modal visible")
        
        # 4. Check for Quick-Action Chips
        has_chip_order = await page.is_visible("#chip-order-status")
        has_chip_refund = await page.is_visible("#chip-refund-status")
        has_chip_cancel = await page.is_visible("#chip-cancel-order")
        record("Quick-Action Chip: 'Where is my order?'", has_chip_order, "chip-order-status present")
        record("Quick-Action Chip: 'Refund Status'", has_chip_refund, "chip-refund-status present")
        record("Quick-Action Chip: 'Cancel Order'", has_chip_cancel, "chip-cancel-order present")
        
        # 5. Execution Logic: Ask about order status
        await page.click("#chip-order-status")
        await page.wait_for_timeout(400)
        
        latest_reply = await page.evaluate("document.getElementById('chat-messages-container').lastElementChild.innerText")
        record("Support Chat Answers Order Status Query with Real-time Info", 
               ("Order Status" in latest_reply or "ऑर्डर" in latest_reply) and ("OTP" in latest_reply or "रास्ते" in latest_reply or "Delivery" in latest_reply),
               f"Reply: {latest_reply[:80]}...")
        
        # 6. Strictly NO shopping/cart cards inside Support Chat
        chat_shopping_cards = await page.locator("#modal-support-chat [id^='commerce-card-']").count()
        record("Support Chat Strictly Has NO Commerce/Shopping Cards", chat_shopping_cards == 0, 
               "Clean post-order interface without shopping cards")
        
        # Close support chat
        await page.evaluate("closeSupportModal()")
        await page.wait_for_timeout(300)
        
        # ====================================================================
        # MODULE 3: TRADITIONAL HELP & SUPPORT CENTER
        # ====================================================================
        print("\n--- MODULE 3: Traditional Help & Support Center ---")
        
        # 1. Open sidebar drawer and find "Help & Support"
        await page.evaluate("openSidebarDrawer()")
        await page.wait_for_timeout(300)
        
        help_center_btn = page.locator("#drawer-help-center-btn")
        record("Sidebar Drawer Contains 'Help & Support' Menu Item", await help_center_btn.count() == 1,
               "drawer-help-center-btn exists")
        
        # 2. Clicking navigates to #view-support-center
        await page.evaluate("document.getElementById('drawer-help-center-btn').click()")
        await page.wait_for_timeout(400)
        
        is_support_center_visible = await page.is_visible("#view-support-center")
        record("Navigates to Dedicated #view-support-center Page", is_support_center_visible, 
               "Traditional Support Center screen active")
        
        # 3. Verify it is NOT an AI chat page (no chat-messages-container inside view-support-center)
        is_not_chat = await page.locator("#view-support-center #chat-messages-container").count() == 0
        record("Support Center is NOT an AI Chat Page", is_not_chat, "Confirmed traditional self-service layout")
        
        # 4. Helpline Banner
        helpline_phone = await page.locator("#view-support-center a[href='tel:18001204266']").count()
        record("Helpline Call Card (1800-120-4266) Present", helpline_phone >= 1, "Toll-free escalation button present")
        
        # 5. FAQ Section (Accordion-style)
        faq_items = await page.locator("#faq-accordion-list > div").count()
        record("FAQ Accordion List Contains Questions", faq_items >= 4, f"Found {faq_items} FAQ items")
        
        # Test FAQ Expand/Collapse
        faq_btn_1 = page.locator("#faq-accordion-list > div:first-child button")
        faq_answer_1 = page.locator("#faq-accordion-list > div:first-child > div")
        record("FAQ Answer Initially Hidden", await faq_answer_1.is_hidden(), "Accordion item closed by default")
        
        await faq_btn_1.click()
        await page.wait_for_timeout(200)
        record("Clicking FAQ Question Expands Answer", await faq_answer_1.is_visible(), "Accordion expands on tap")
        
        # 6. Raise a Ticket Form
        has_ticket_form = await page.is_visible("#support-ticket-form")
        has_subject = await page.is_visible("#ticket-subject")
        has_desc = await page.is_visible("#ticket-description")
        has_upload = await page.locator("#ticket-attachment").count() > 0
        has_submit_btn = await page.is_visible("#btn-submit-support-ticket")
        
        record("Raise a Ticket Form Rendered", has_ticket_form, "Form container visible")
        record("Ticket Subject & Description Inputs Present", has_subject and has_desc, "Form fields present")
        record("Attachment / File Upload Input Present", has_upload, "File input present")
        record("Submit Ticket Button Present", has_submit_btn, "btn-submit-support-ticket visible")
        
        # 7. Submit a New Complaint Ticket
        await page.fill("#ticket-subject", "Flour packet seal broken")
        await page.fill("#ticket-description", "Received Aashirvaad Atta with torn packet seal. Requesting replacement.")
        await page.click("#btn-submit-support-ticket")
        await page.wait_for_timeout(400)
        
        # 8. Ticket History Section
        first_ticket = await page.locator("#support-ticket-history-list > div:first-child").inner_text()
        record("Submitted Ticket Appears in Ticket History List", "Flour packet seal broken" in first_ticket,
               f"History top ticket: {first_ticket[:60]}...")
        record("New Ticket Has 'Open' Status Badge", "Open" in first_ticket, "Status: Open confirmed")
        
        # ====================================================================
        # NAVIGATION & BACK GESTURE ROUTING
        # ====================================================================
        print("\n--- Navigation & Back Routing Check ---")
        # Header back button on #view-support-center navigates to dashboard
        back_btn = page.locator("#view-support-center button[aria-label='Back to home']")
        await back_btn.click()
        await page.wait_for_timeout(300)
        
        is_dash = await page.is_visible("#view-p2-dashboard")
        record("Back Button Returns from Support Center to Dashboard", is_dash, "Back to home confirmed")
        
        await browser.close()
        
    print("\n======================================================================")
    print(f"RESULTS: {passed}/{total} AUDITS PASSED ({(passed/total)*100:.1f}%)")
    print("======================================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
