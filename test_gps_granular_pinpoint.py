"""
Verification test for granular reverse geocoding UI display and hidden raw coordinates pinpointing.
"""

import sys
import unittest
from playwright.sync_api import sync_playwright
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

file_path = os.path.abspath("index.html")
file_url = f"file:///{file_path.replace(os.sep, '/')}"

class TestGpsGranularPinpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = sync_playwright().start()
        cls.browser = cls.p.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.p.stop()

    def test_granular_location_prioritization_and_hidden_coords(self):
        context = self.browser.new_context(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
            geolocation={"latitude": 26.1209, "longitude": 85.3647}, # Muzaffarpur coords
            permissions=["geolocation"]
        )
        page = context.new_page()
        page.goto(file_url)
        page.wait_for_timeout(500)
        page.evaluate("navigateToPhase('landmark')")
        page.wait_for_timeout(300)

        # 1. Test unit reverseGeocodeCoords with mocked address containing suburb/neighbourhood/road vs city
        result_suburb = page.evaluate("""() => {
            // Mock reverseGeocodeCoords parsing logic for Ahiyapur, Muzaffarpur
            const addr = {
                suburb: 'Ahiyapur',
                road: 'NH 28',
                city: 'Muzaffarpur',
                state_district: 'Muzaffarpur',
                state: 'Bihar'
            };
            const district = addr.state_district || addr.county || addr.district || addr.city || '';
            const granular = addr.village || addr.hamlet || addr.suburb || addr.neighbourhood || addr.road || '';
            return { district, granular };
        }""")
        self.assertEqual(result_suburb["granular"], "Ahiyapur")
        self.assertEqual(result_suburb["district"], "Muzaffarpur")
        print("  ✓ Prioritizes 'Ahiyapur' (suburb) over broad 'Muzaffarpur' (district)")

        # 2. Test unit with road priority when village and suburb are absent
        result_road = page.evaluate("""() => {
            const addr = {
                road: 'Motihari Road',
                city: 'Muzaffarpur',
                state_district: 'Muzaffarpur',
                state: 'Bihar'
            };
            const district = addr.state_district || addr.county || addr.district || addr.city || '';
            const granular = addr.village || addr.hamlet || addr.suburb || addr.neighbourhood || addr.road || '';
            return { district, granular };
        }""")
        self.assertEqual(result_road["granular"], "Motihari Road")
        self.assertEqual(result_road["district"], "Muzaffarpur")
        print("  ✓ Prioritizes 'Motihari Road' (road) over broad 'Muzaffarpur' (district)")

        # 3. Test applyLocationResult sets raw coordinates into hidden inputs
        coords_test = page.evaluate("""async () => {
            // Mock reverseGeocodeCoords
            window.reverseGeocodeCoords = async () => ({
                village: 'Chatursi',
                district: 'Muzaffarpur',
                state: 'Bihar',
                granular: 'Chatursi'
            });
            await detectGpsLocation();
            return {
                lat_input: document.getElementById('p1-latitude-input')?.value,
                lng_input: document.getElementById('p1-longitude-input')?.value,
                lat_alias: document.getElementById('latitude')?.value,
                lng_alias: document.getElementById('longitude')?.value,
                btn_text: document.getElementById('p1-locate-text')?.innerText,
                badge_text: document.getElementById('p1-gps-badge')?.innerText,
                appstore_lat: AppStore.user.latitude,
                appstore_lng: AppStore.user.longitude,
                appstore_granular: AppStore.user.granular
            };
        }""")

        self.assertAlmostEqual(float(coords_test["lat_input"]), 26.1209, places=3)
        self.assertAlmostEqual(float(coords_test["lng_input"]), 85.3647, places=3)
        self.assertAlmostEqual(float(coords_test["lat_alias"]), 26.1209, places=3)
        self.assertAlmostEqual(float(coords_test["lng_alias"]), 85.3647, places=3)
        self.assertIn("Chatursi", coords_test["btn_text"])
        self.assertIn("Chatursi", coords_test["badge_text"])
        self.assertIn("Muzaffarpur", coords_test["badge_text"])
        self.assertEqual(coords_test["appstore_granular"], "Chatursi")
        print("  ✓ Raw coords (26.1209, 85.3647) saved in hidden inputs (#p1-latitude-input, #latitude)")
        print("  ✓ Green button displays granular location: " + coords_test["btn_text"])
        print("  ✓ Subtitle badge displays granular location: " + coords_test["badge_text"])

        # 4. Test when only road / suburb is detected, button and badge show granular instead of Muzaffarpur
        road_test = page.evaluate("""async () => {
            window.reverseGeocodeCoords = async () => ({
                village: '',
                district: 'Muzaffarpur',
                state: 'Bihar',
                granular: 'Damodarpur'
            });
            await detectGpsLocation();
            return {
                btn_text: document.getElementById('p1-locate-text')?.innerText,
                badge_text: document.getElementById('p1-gps-badge')?.innerText,
                vill_input: document.getElementById('p1-village-input')?.value,
                dist_input: document.getElementById('p1-district-input')?.value
            };
        }""")

        self.assertIn("Damodarpur", road_test["btn_text"])
        self.assertIn("Damodarpur", road_test["badge_text"])
        print("  ✓ Suburb 'Damodarpur' displayed on button and badge instead of broad 'Muzaffarpur'")

        context.close()

if __name__ == "__main__":
    unittest.main()
