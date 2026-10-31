// No browser, microphone, network, or database required. Exercise the actual
// voice engine embedded in index.html with isolated synthetic catalog data.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const from = html.indexOf('const VoiceCommerceEngine = {');
const to = html.indexOf('window.VoiceCommerceEngine = VoiceCommerceEngine;', from);
assert.ok(from > 0 && to > from, 'Voice engine is present');

const AppStore = {
  lang: 'hi',
  currentPhase: 'ai-commerce',
  catalog: [
    { id: 'item_tomato', name_hi: 'ताज़ा टमाटर', name_en: 'Fresh Tomato', price: 30, qty: 0 },
    { id: 'item_banana', name_hi: 'केला', name_en: 'Banana', price: 40, qty: 0 },
    { id: 'item_milk', name_hi: 'दूध', name_en: 'Milk', price: 60, qty: 0 },
  ],
};
let searchQueries = [];
const sandbox = {
  AppStore,
  window: { speechSynthesis: null },
  document: { getElementById: () => null },
  showAudioToast: () => {},
  modifyItemQty: (id, qty) => { AppStore.catalog.find(i => i.id === id).qty += qty; },
  processCommerceAiQuery: async query => { searchQueries.push(query); },
  syncCommerceCartBar: () => {},
};

vm.runInNewContext(`${html.slice(from, to)}\n globalThis.engine = VoiceCommerceEngine;`, sandbox);
const engine = sandbox.engine;

(async () => {
  assert.equal(engine.parseIntent('मुझे 1 किलो टमाटर चाहिए').intent, 'ADD_TO_CART');
  console.log('PASS: natural Hindi product request is recognized as cart intent');
  assert.equal(engine.parseIntent('2 केला जोड़ो').quantity, 2);
  console.log('PASS: Hindi quantity understood');
  const result = await engine.executeAiVoiceShoppingList('मुझे 1 किलो टमाटर और 2 केला चाहिए');
  assert.equal(result.added, 2);
  assert.equal(AppStore.catalog[0].qty, 1);
  assert.equal(AppStore.catalog[1].qty, 2);
  assert.equal(searchQueries[0], 'मुझे 1 किलो टमाटर और 2 केला चाहिए');
  console.log('PASS: AI voice adds both products and refreshes matching cards');

  const homeMic = html.match(/<button id="p2-voice-search-btn"[^>]+>/)?.[0];
  assert.ok(homeMic?.includes('onclick="triggerVoiceSearch()"'));
  const homeSearch = html.slice(html.indexOf('function triggerVoiceSearch()'), html.indexOf('function clearStoreSearch()'));
  assert.ok(homeSearch.includes('filterStoreCatalog(productQuery)'));
  assert.ok(!homeSearch.includes('navigateToPhase('));
  assert.ok(!homeSearch.includes('executeVoiceCommand('));
  console.log('PASS: Home microphone only searches and never navigates or adds to cart');

  assert.ok(html.includes('html.dark #p1-hero-badge'));
  assert.ok(html.includes('background-color: #2A323D !important;'));
  console.log('PASS: login hero badge has explicit dark-mode contrast styling');

  for (const filename of ['prod_tomato.png', 'prod_banana.png', 'hero_banner.png']) {
    const buffer = fs.readFileSync(path.join(__dirname, 'static/images', filename));
    assert.equal(buffer.subarray(1, 4).toString('utf8'), 'PNG');
    assert.ok(buffer.readUInt32BE(16) >= 300 && buffer.readUInt32BE(20) >= 300);
    console.log(`PASS: ${filename} has uncropped-resolution replacement`);
  }
})().catch(error => {
  console.error('FAIL:', error.message);
  process.exitCode = 1;
});
