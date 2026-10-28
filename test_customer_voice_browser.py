"""Customer voice/search/AI and layout regressions with mocked speech events.

This exercises a real Chromium UI on CI, but mocks speech recognition so it
never claims to prove physical-phone microphone permissions or capture audio.
"""

from pathlib import Path
from playwright.sync_api import sync_playwright


MOCK_SPEECH = """
class MockSpeechRecognition {
  constructor() { window.__latestSpeech = this; }
  start() { setTimeout(() => this.onstart?.(), 0); }
  stop() { setTimeout(() => this.onend?.(), 0); }
  abort() { setTimeout(() => this.onend?.(), 0); }
  emit(text, isFinal) {
    const item = [{ transcript: text }];
    item.isFinal = isFinal;
    this.onresult?.({ resultIndex: 0, results: [item] });
  }
}
// Chromium may expose an unprefixed native constructor. Override BOTH names,
// otherwise the page takes the real recognizer instead of our mock.
Object.defineProperty(window, 'SpeechRecognition', {
  configurable: true, value: MockSpeechRecognition
});
Object.defineProperty(window, 'webkitSpeechRecognition', {
  configurable: true, value: MockSpeechRecognition
});
"""


def main():
    passes = []

    def check(name, success):
        assert success, f"FAIL: {name}"
        passes.append(name)
        print(f"PASS: {name}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 393, "height": 851},
                                      is_mobile=True, has_touch=True,
                                      device_scale_factor=2.75)
        context.add_init_script(MOCK_SPEECH)
        page = context.new_page()
        page.goto(Path(__file__).with_name("index.html").as_uri(), wait_until="domcontentloaded")
        page.wait_for_function("typeof navigateToPhase === 'function' && !!window.VoiceCommerceEngine")

        page.evaluate("""() => {
          AppStore.lang = 'hi';
          navigateToPhase('dashboard');
          AppStore.catalog.forEach(item => { item.qty = 0; });
        }""")
        page.click("#p2-voice-search-btn")
        page.wait_for_function("""() =>
          !!window.__latestSpeech &&
          document.getElementById('p2-voice-search-btn').getAttribute('aria-pressed') === 'true'
        """, timeout=3000)
        check("Home mic listens on Home; no redirect to AI",
              page.is_visible("#view-p2-dashboard") and
              page.get_attribute("#p2-voice-search-btn", "aria-pressed") == "true")
        page.evaluate("window.__latestSpeech.emit('टमाटर', false)")
        check("Home mic shows live transcript", page.input_value("#p2-search-input") == "टमाटर")
        page.evaluate("window.__latestSpeech.emit('टमाटर', true)")
        page.wait_for_timeout(100)
        check("Home mic shows product search results",
              page.is_visible("#p2-search-results") and
              "टमाटर" in page.inner_text("#p2-search-results"))
        check("Home mic never modifies cart",
              page.evaluate("AppStore.catalog.every(item => item.qty === 0)"))

        page.evaluate("navigateToPhase('ai-commerce')")
        page.click("#commerce-ai-mic-btn")
        page.wait_for_function("""() =>
          !!window.__latestSpeech &&
          document.getElementById('commerce-ai-status-text').textContent.includes('सुन')
        """, timeout=3000)
        check("AI microphone has listening status on AI view",
              page.is_visible("#view-commerce-ai") and
              "सुन" in page.inner_text("#commerce-ai-status-text"))
        page.evaluate("window.__latestSpeech.emit('मुझे 1 किलो टमाटर और 2 केला चाहिए', true)")
        page.wait_for_function("""() => {
          const a = AppStore.catalog.find(i => i.id === 'item_tomato');
          const b = AppStore.catalog.find(i => i.id === 'item_banana');
          return a?.qty === 1 && b?.qty === 2;
        }""", timeout=10000)
        check("AI voice adds both Hindi products with quantities",
              page.evaluate("""() =>
                AppStore.catalog.find(i=>i.id==='item_tomato').qty === 1 &&
                AppStore.catalog.find(i=>i.id==='item_banana').qty === 2"""))
        check("AI keeps transcript and updates cart bar",
              "टमाटर" in page.inner_text("#commerce-ai-transcript") and
              "hidden" not in page.locator("#commerce-view-cart-bar").get_attribute("class"))

        page.evaluate("""() => {
          navigateToPhase('login');
          document.documentElement.classList.add('dark');
        }""")
        check("Dark login badge has charcoal background and bright text",
              page.locator("#p1-hero-badge").evaluate("""el => {
                const css = getComputedStyle(el);
                return css.backgroundColor === 'rgb(42, 50, 61)' &&
                       css.color === 'rgb(248, 250, 252)';
              }"""))
        page.evaluate("navigateToPhase('dashboard')")
        check("All category chips fit within Home screen horizontally",
              page.locator(".cat-chip").evaluate_all("""chips => chips.every(chip => {
                const b = chip.getBoundingClientRect();
                const p = chip.closest('.w-full').getBoundingClientRect();
                return b.left >= p.left - 1 && b.right <= p.right + 1;
              })"""))
        check("Popular product pictures load at complete resolution",
              page.locator("#home-popular-grid img").evaluate_all("""images =>
                images.every(img => img.complete && img.naturalWidth >= 300 && img.naturalHeight >= 300)
              """))
        check("Homepage promotion image is complete and high resolution",
              page.locator("#p2-guarantee-banner img").evaluate("""img =>
                img.complete && img.naturalWidth >= 300 && img.naturalHeight >= 300
              """))
        print(f"\n{len(passes)} CUSTOMER BROWSER CHECKS PASS (synthetic voice input)")
        browser.close()


if __name__ == "__main__":
    main()
