// Run with: node tests/js/dashboard-panels.test.mjs
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { runInNewContext } from 'node:vm';

const source = await readFile(new URL('../../app/static/dashboard-panels.js', import.meta.url), 'utf8');
const page = mobile => {
    const media = {
        matches: mobile,
        addEventListener(name, callback) { this.change = callback; },
    };
    const panels = Array.from({ length: 2 }, () => ({
        open: true, summary: {},
        querySelector() { return this.summary; },
        addEventListener(name, callback) { this.toggle = callback; },
    }));
    runInNewContext(source, {
        document: { querySelectorAll: () => panels },
        window: { matchMedia: () => media },
    });
    return { panels, resize(mobile) { media.matches = mobile; media.change(); } };
};

const phone = page(true);
assert.ok(phone.panels.every(panel => !panel.open && panel.summary.tabIndex === 0));
phone.panels[0].open = true;
phone.panels[0].toggle();
assert.equal(phone.panels[0].open, true);
assert.equal(phone.panels[1].open, false); // Sections can be opened independently.
phone.panels[0].open = false;
phone.panels[0].toggle();
assert.equal(phone.panels[0].open, false);
phone.resize(false);
assert.ok(phone.panels.every(panel => panel.open && panel.summary.tabIndex === -1));
phone.panels[0].open = false;
phone.panels[0].toggle();
assert.equal(phone.panels[0].open, true); // Desktop stays expanded.
phone.resize(true);
assert.ok(phone.panels.every(panel => !panel.open && panel.summary.tabIndex === 0));
assert.ok(page(false).panels.every(panel => panel.open));
assert.ok(page(true).panels.every(panel => !panel.open)); // Reload resets mobile panels.
console.log('Passed dashboard panel scenarios (mobile defaults, independent toggles, desktop expansion, resize, and reload).');
