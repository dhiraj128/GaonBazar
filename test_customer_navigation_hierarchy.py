"""Customer information-architecture regression checks (no DB or network access).

The interactive flows are covered separately by test_mobile_e2e.py.
"""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


HTML = Path(__file__).with_name("index.html").read_text(encoding="utf-8")


class IdCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        self.ids.extend(value for key, value in attrs if key == "id")


def section(start, end):
    begin = HTML.index(start)
    finish = HTML.index(end, begin + len(start))
    return HTML[begin:finish]


class CustomerNavigationHierarchyTests(unittest.TestCase):
    def test_unique_html_ids(self):
        parser = IdCollector()
        parser.feed(HTML)
        duplicates = [name for name, count in Counter(parser.ids).items() if count != 1]
        self.assertEqual(duplicates, [], f"Duplicate DOM ids: {duplicates}")

    def test_drawer_is_secondary_navigation_only(self):
        drawer = section('id="sidebar-drawer"', "</aside>")
        for old_route in (
            "drawer-account-btn", "drawer-cart-btn", "drawer-orders-btn",
            "drawer-payments-btn", "drawer-support-btn", "drawer-lang-btn",
            "drawer-theme-curr", "profile-saved-payment-list",
        ):
            with self.subTest(old_route=old_route):
                self.assertNotIn(old_route, drawer)
        for action in ("drawer-user-card", "drawer-notifications-btn", "drawer-help-center-btn"):
            self.assertIn(action, drawer)
        self.assertEqual(len(re.findall(r'<button id="drawer-help-center-btn"', drawer)), 1)
        self.assertNotIn("logoutCustomer()", drawer)

    def test_orders_and_account_have_single_purpose(self):
        orders = section('id="view-p5-tracking"', 'id="view-offline-fallback"')
        account = section('id="view-profile"', 'id="view-commerce-ai"')
        self.assertIn('id="orders-history-list"', orders)
        self.assertIn('id="btn-call-runner"', orders)
        self.assertNotIn('href="tel:9876543210"', orders)
        self.assertNotIn('runner_ramesh.png', orders)
        self.assertNotIn('id="orders-history-list"', account)
        self.assertIn('id="profile-saved-payment-list"', account)
        self.assertIn('id="profile-saved-payments-panel"', account)
        self.assertIn('id="btn-profile-lang-hi"', account)
        self.assertIn('id="btn-profile-lang-en"', account)
        self.assertIn('id="btn-theme-dark"', account)
        self.assertNotIn('id="profile-row-help-support"', account)
        self.assertEqual(account.count('onclick="logoutCustomer()"'), 1)

    def test_help_is_single_hub_for_all_support_options(self):
        help_center = section('id="view-support-center"', "</section>")
        for action in (
            'id="support-ai-chat-btn"', 'id="support-helpline-banner"',
            'id="faq-accordion-list"', 'id="btn-submit-support-ticket"',
            'id="support-ticket-history-list"',
        ):
            self.assertIn(action, help_center)

    def test_primary_tabs_remain_persistent_and_no_fake_orders_or_cart(self):
        navigation = section("function navigateToPhase(", "window.navigateToPhase = navigateToPhase")
        for phase in ("'dashboard'", "'ai-commerce'", "'cart'", "'tracking'", "'profile'"):
            self.assertIn(phase, navigation)
        self.assertNotIn("quickAddFeaturedItem(", navigation)
        tracking = section("async function renderLiveTrackingView(", "window.renderLiveTrackingView = renderLiveTrackingView")
        self.assertIn("showTrackingEmptyState();", tracking)
        self.assertNotIn("#GB-1284", tracking)
        self.assertNotIn("Sharma Brothers Kirana", tracking)
        populate = section("function populateTrackingUI(", "window.populateTrackingUI = populateTrackingUI")
        self.assertIn("validRunnerPhone", populate)
        self.assertIn("btnCallRunner.removeAttribute('href')", populate)
        self.assertIn("supportTickets: []", HTML)
        self.assertNotIn("TKT-82419", HTML)
        notifications = section("async function loadRealNotifications()", "window.loadRealNotifications = loadRealNotifications")
        self.assertNotIn("'9876543210'", notifications)

    def test_new_labels_are_translated_in_both_languages(self):
        for key in ("drawer_quick_access", "drawer_bottom_tip", "profile_add_payment"):
            self.assertEqual(len(re.findall(r"\b" + key + r":\s*\"", HTML)), 2, key)


if __name__ == "__main__":
    unittest.main()
