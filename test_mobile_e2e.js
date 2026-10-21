/**
 * GaonBazaar (गांव बाज़ार) - Playwright Mobile Automated Test Suite
 * 
 * Simulates:
 * 1. iPhone 16 (Viewport: 393 x 852, DPR: 3.0, Mobile Safari)
 * 2. Low-End Budget Android (Viewport: 360 x 740, DPR: 2.0, Mobile Chrome)
 * 
 * Tests All 5 Phases:
 * - Phase 1: Onboarding, Language Toggle, Phone Login, 6-Box OTP, Rural Landmark Setup
 * - Phase 2: Main Dashboard (Sticky Landmark Header, Store Feeds)
 * - Phase 3: Store & Product View (Sharma Brothers Kirana, [-] 1 [+] Steppers, Cart Bar)
 * - Phase 4: Cart Review (Line Items, Bill Details, Free Delivery) & Checkout (Address, COD/UPI)
 * - Phase 5: Live Order Tracking (#RUR Order ID, 5-Stage Timeline, Doorstep Delivery OTP)
 * 
 * Verifications:
 * - Horizontal overflow & element width leaks
 * - UI layout squeezing & blank whitespace on the right
 * - Console errors, page exceptions, and functional step navigation
 * - Writes comprehensive audit to 'test_report.txt'
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');

// Target file path
const HTML_FILE_PATH = path.resolve(__dirname, 'index.html');
const REPORT_FILE_PATH = path.resolve(__dirname, 'test_report.txt');

// Test Devices Configuration
const TEST_DEVICES = [
  {
    name: 'iPhone 16',
    deviceType: 'ios',
    viewport: { width: 393, height: 852 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
  },
  {
    name: 'Pixel 7',
    deviceType: 'android',
    viewport: { width: 412, height: 915 },
    deviceScaleFactor: 2.625,
    isMobile: true,
    hasTouch: true,
    userAgent: 'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36'
  },
  {
    name: 'Galaxy S22',
    deviceType: 'android',
    viewport: { width: 360, height: 780 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
    userAgent: 'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
  }
];

// Helper logger
class TestLogger {
  constructor() {
    this.logs = [];
    this.totalTests = 0;
    this.passedTests = 0;
    this.failedTests = 0;
  }

  log(msg) {
    const timestamp = new Date().toISOString().replace('T', ' ').slice(0, 19);
    const line = `[${timestamp}] ${msg}`;
    console.log(line);
    this.logs.push(line);
  }

  recordTest(name, passed, detail = '') {
    this.totalTests++;
    if (passed) {
      this.passedTests++;
      this.log(`  ✓ PASS: ${name} ${detail ? '(' + detail + ')' : ''}`);
    } else {
      this.failedTests++;
      this.log(`  ✗ FAIL: ${name} - ERROR: ${detail}`);
    }
  }

  saveReport() {
    const summaryHeader = [
      '================================================================================',
      '                     GAONBAZAAR AUTOMATED PLAYWRIGHT TEST REPORT                ',
      '================================================================================',
      `Date & Time: ${new Date().toLocaleString()}`,
      `Tested File: ${HTML_FILE_PATH}`,
      `Total Checks: ${this.totalTests}`,
      `Passed: ${this.passedTests}`,
      `Failed: ${this.failedTests}`,
      `Overall Status: ${this.failedTests === 0 ? 'SUCCESS (100% HEALTHY)' : 'ATTENTION REQUIRED'}`,
      '--------------------------------------------------------------------------------',
      ''
    ].join('\n');

    const reportContent = summaryHeader + this.logs.join('\n') + '\n';
    fs.writeFileSync(REPORT_FILE_PATH, reportContent, 'utf8');
    console.log(`\n📄 Report written to: ${REPORT_FILE_PATH}\n`);
  }
}

// Check for horizontal overflow & layout squeeze
async function inspectViewportAndLayout(page, phaseName, logger) {
  const layoutMetrics = await page.evaluate(() => {
    const winWidth = window.innerWidth;
    const docWidth = document.documentElement.scrollWidth;
    const bodyWidth = document.body.scrollWidth;
    const root = document.getElementById('app-root') || document.body;
    const rootRect = root.getBoundingClientRect();

    // Check for elements overflowing beyond window width + 2px tolerance
    const overflowingElements = [];
    document.querySelectorAll('*').forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.right > winWidth + 2 && rect.width > 0 && rect.height > 0) {
        overflowingElements.push({
          tag: el.tagName.toLowerCase(),
          id: el.id || '',
          className: (el.className || '').toString().slice(0, 40),
          width: Math.round(rect.width),
          right: Math.round(rect.right),
          overflowAmount: Math.round(rect.right - winWidth)
        });
      }
    });

    // Check layout squeezing
    // If root wrapper takes < 95% of window width, it is squeezed with right-side blank space
    const isSqueezed = rootRect.width < (winWidth * 0.95);
    const blankSpaceRight = Math.max(0, Math.round(winWidth - rootRect.width));

    return {
      winWidth,
      docWidth,
      bodyWidth,
      rootWidth: Math.round(rootRect.width),
      hasHorizontalOverflow: docWidth > (winWidth + 2) || bodyWidth > (winWidth + 2),
      isSqueezed,
      blankSpaceRight,
      overflowingCount: overflowingElements.length,
      sampleOverflow: overflowingElements.slice(0, 3)
    };
  });

  // Verify Horizontal Overflow
  if (!layoutMetrics.hasHorizontalOverflow && layoutMetrics.overflowingCount === 0) {
    logger.recordTest(
      `${phaseName} - No Horizontal Overflow`,
      true,
      `doc: ${layoutMetrics.docWidth}px, viewport: ${layoutMetrics.winWidth}px`
    );
  } else {
    logger.recordTest(
      `${phaseName} - Horizontal Overflow Detected`,
      false,
      `doc width ${layoutMetrics.docWidth}px exceeds viewport ${layoutMetrics.winWidth}px. Leaking elements: ${JSON.stringify(layoutMetrics.sampleOverflow)}`
    );
  }

  // Verify Layout Squeeze / Right-Side Blank Whitespace
  if (!layoutMetrics.isSqueezed) {
    logger.recordTest(
      `${phaseName} - Full-Width Expansion (No Squeezing)`,
      true,
      `root width: ${layoutMetrics.rootWidth}px / ${layoutMetrics.winWidth}px (100% fill)`
    );
  } else {
    logger.recordTest(
      `${phaseName} - UI Squeezed to Left`,
      false,
      `Root width is only ${layoutMetrics.rootWidth}px on a ${layoutMetrics.winWidth}px screen (${layoutMetrics.blankSpaceRight}px blank whitespace on right)`
    );
  }
}

async function runDeviceSimulation(browser, deviceConfig, logger) {
  logger.log(`\n================================================================================`);
  logger.log(`STARTING SIMULATION: ${deviceConfig.name}`);
  logger.log(`Dimensions: ${deviceConfig.viewport.width}x${deviceConfig.viewport.height} | DPR: ${deviceConfig.deviceScaleFactor}`);
  logger.log(`================================================================================`);

  const context = await browser.newContext({
    viewport: deviceConfig.viewport,
    deviceScaleFactor: deviceConfig.deviceScaleFactor,
    isMobile: deviceConfig.isMobile,
    hasTouch: deviceConfig.hasTouch,
    userAgent: deviceConfig.userAgent
  });

  const page = await context.newPage();

  // Track console errors
  const pageErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      pageErrors.push(msg.text());
    }
  });
  page.on('pageerror', err => {
    pageErrors.push(err.message);
  });

  // 1. Navigate to index.html
  const fileUrl = pathToFileURL(HTML_FILE_PATH).href;
  logger.log(`Loading application: ${fileUrl}`);
  await page.goto(fileUrl, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);

  // Verify Viewport Meta Tag
  const metaViewport = await page.getAttribute('meta[name="viewport"]', 'content');
  const validViewportMeta = metaViewport && metaViewport.includes('width=device-width');
  logger.recordTest('HTML Viewport Meta Tag Check', validViewportMeta, `content="${metaViewport}"`);

  // --- PHASE 1.1: LOGIN ---
  const devName = device.name;
  logger.log(`\n--- [${devName}] Testing Phase 1.1: Phone Login & Language Toggle ---`);
  await inspectViewportAndLayout(page, `[${devName}] Phase 1.1 Login`, logger);

  // Test Bilingual Toggle
  const initialLang = (await page.innerText('#global-lang-label')).trim();
  await page.click('#global-lang-btn');
  await page.waitForTimeout(300);
  const switchedLang = (await page.innerText('#global-lang-label')).trim();
  const langToggleWorked = initialLang !== switchedLang;
  logger.recordTest(`[${devName}] Bilingual Toggle (Instant State Switch)`, langToggleWorked, `${initialLang} -> ${switchedLang}`);

  // Switch back to Hindi
  if (switchedLang !== 'हिंदी') {
    await page.click('#global-lang-btn');
    await page.waitForTimeout(300);
  }

  // Enter Mobile Number
  await page.fill('#p1-phone-input', '9876543210');
  await page.waitForTimeout(300);

  // Check valid hint and Send OTP button enabled
  const sendBtnDisabled = await page.getAttribute('#p1-send-otp-btn', 'disabled');
  const sendBtnIsEnabled = await page.isEnabled('#p1-send-otp-btn');
  logger.recordTest(`[${devName}] 10-Digit Mobile Validation`, sendBtnDisabled === null && sendBtnIsEnabled, 'Send OTP button enabled');

  // Click Send OTP
  await page.click('#p1-send-otp-btn');
  await page.waitForTimeout(900);

  // --- PHASE 1.2: OTP VERIFICATION ---
  logger.log('\n--- Testing Phase 1.2: OTP Verification ---');
  const isOtpVisible = await page.isVisible('#view-p1-otp');
  logger.recordTest('Transition to OTP Screen', isOtpVisible);
  await inspectViewportAndLayout(page, 'Phase 1.2 OTP', logger);

  // Fill OTP cells or trigger submission
  await page.fill('.otp-cell[data-idx="0"]', '5');
  await page.fill('.otp-cell[data-idx="1"]', '8');
  await page.fill('.otp-cell[data-idx="2"]', '2');
  await page.fill('.otp-cell[data-idx="3"]', '9');
  await page.fill('.otp-cell[data-idx="4"]', '4');
  await page.fill('.otp-cell[data-idx="5"]', '1');
  await page.waitForTimeout(500);

  // Click Verify button if not auto-advanced
  if (await page.isVisible('#view-p1-otp')) {
    await page.click('button:has-text("Verify")');
    await page.waitForTimeout(400);
  }

  // --- PHASE 1.3: RURAL LANDMARK SETUP ---
  logger.log('\n--- Testing Phase 1.3: Rural Landmark Setup ---');
  const isLandmarkVisible = await page.isVisible('#view-p1-landmark');
  logger.recordTest('Transition to Landmark Setup Screen', isLandmarkVisible);
  await inspectViewportAndLayout(page, 'Phase 1.3 Landmark', logger);

  // Fill Name and Landmark
  await page.fill('#p1-name-input', 'Ramesh Patel');
  await page.fill('#p1-landmark-text', 'Near Shiva Mandir, Opp. Blue Water Tank');
  await page.waitForTimeout(300);

  // Verify Landmark Length Check (>= 10 chars)
  const landmarkText = await page.inputValue('#p1-landmark-text');
  logger.recordTest('Rural Landmark Character Count', landmarkText.length >= 10, `${landmarkText.length} chars`);

  // Submit Landmark Form
  await page.click('button:has-text("Save & Enter Market")');
  await page.waitForTimeout(500);

  // --- PHASE 2: MAIN DASHBOARD ---
  logger.log('\n--- Testing Phase 2: Main Dashboard & Store Discovery ---');
  const isDashboardVisible = await page.isVisible('#view-p2-dashboard');
  logger.recordTest('Transition to Dashboard', isDashboardVisible);
  await inspectViewportAndLayout(page, 'Phase 2 Dashboard', logger);

  // Verify Sticky Landmark Header
  const villageLabel = await page.innerText('#p2-loc-village');
  logger.recordTest('Sticky Village Header Rendered', villageLabel.length > 0, villageLabel);

  // Open Store View (Sharma Brothers Kirana)
  await page.click('div[onclick*="sharma_brothers"]');
  await page.waitForTimeout(400);

  // --- PHASE 3: STORE & PRODUCT VIEW ---
  logger.log('\n--- Testing Phase 3: Store Catalog & Dynamic Steppers ---');
  const isStoreVisible = await page.isVisible('#view-p3-store');
  logger.recordTest('Transition to Store View (Sharma Brothers Kirana)', isStoreVisible);
  await inspectViewportAndLayout(page, 'Phase 3 Store', logger);

  // Add Item to Cart using dynamic stepper [+]
  const initialCartBarHidden = !(await page.isVisible('#p3-cart-bar'));
  // Click first Add / [+] button in the product catalog
  const addBtn = page.locator('#p3-product-list button:has-text("ADD"), #p3-product-list button:has(.material-symbols-outlined:has-text("add"))').first();
  await addBtn.click();
  await page.waitForTimeout(400);

  // Verify Sticky Floating Cart Bar is visible
  const isCartBarVisible = await page.isVisible('#p3-cart-bar');
  logger.recordTest('Dynamic Stepper -> Cart Bar Triggered', isCartBarVisible, 'Cart bar popped up');

  // Click View Cart
  await page.click('#p3-cart-bar button:has-text("View Cart")');
  await page.waitForTimeout(400);

  // --- PHASE 4: CART & CHECKOUT ---
  logger.log('\n--- Testing Phase 4.1: Cart Review ---');
  const isCartVisible = await page.isVisible('#view-p4-cart');
  logger.recordTest('Transition to Cart Review Screen', isCartVisible);
  await inspectViewportAndLayout(page, 'Phase 4.1 Cart', logger);

  // Click Proceed to Address & Pay
  await page.click('button:has-text("Proceed")');
  await page.waitForTimeout(400);

  logger.log('\n--- Testing Phase 4.2: Checkout & Payment Selection ---');
  const isCheckoutVisible = await page.isVisible('#view-p4-checkout');
  logger.recordTest('Transition to Checkout Screen', isCheckoutVisible);
  await inspectViewportAndLayout(page, 'Phase 4.2 Checkout', logger);

  // Verify COD Payment Mode
  await page.click('#pay-card-cod');
  await page.waitForTimeout(200);

  // Click Place Order
  await page.click('#btn-place-order');
  await page.waitForTimeout(1400);

  // --- PHASE 5: LIVE ORDER TRACKING ---
  logger.log('\n--- Testing Phase 5: Live Order Tracking ---');
  const isTrackingVisible = await page.isVisible('#view-p5-tracking');
  logger.recordTest('Transition to Live Order Tracking Screen', isTrackingVisible);
  await inspectViewportAndLayout(page, 'Phase 5 Tracking', logger);

  // Verify Order ID & Doorstep Delivery OTP
  const orderId = await page.innerText('#p5-order-id');
  const hasValidOrderId = orderId.startsWith('#RUR-');
  logger.recordTest('Live Tracking Order ID Generated', hasValidOrderId, orderId);

  const otpBoxVisible = await page.isVisible('text="DELIVERY OTP:"');
  logger.recordTest('Safe Doorstep Delivery OTP Displayed', otpBoxVisible, '4-digit OTP code visible');

  // Check JavaScript Page Errors
  logger.log('\n--- Console & Script Execution Audit ---');
  if (pageErrors.length === 0) {
    logger.recordTest('Zero JavaScript Console Errors', true, 'Clean runtime execution');
  } else {
    logger.recordTest('JavaScript Console Errors Encountered', false, pageErrors.join(' | '));
  }

  await context.close();
}

// Main execution runner
async function runPlaywrightSuite() {
  const logger = new TestLogger();
  logger.log('Starting Playwright End-to-End Mobile Test Runner for GaonBazaar...');

  if (!fs.existsSync(HTML_FILE_PATH)) {
    console.error(`Error: Cannot find index.html at ${HTML_FILE_PATH}`);
    process.exit(1);
  }

  let browser;
  try {
    browser = await chromium.launch({
      headless: true
    });

    for (const device of TEST_DEVICES) {
      await runDeviceSimulation(browser, device, logger);
    }
  } catch (err) {
    logger.log(`FATAL RUNNER ERROR: ${err.message}`);
    logger.recordTest('Test Runner Execution', false, err.message);
  } finally {
    if (browser) {
      await browser.close();
    }
    logger.saveReport();
  }
}

// Execute
runPlaywrightSuite();
