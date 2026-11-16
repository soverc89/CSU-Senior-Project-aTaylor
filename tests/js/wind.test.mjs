// Run with: node tests/js/wind.test.mjs
// Exercises the actual dashboard scripts with a small DOM/Leaflet test double.
import assert from 'node:assert/strict';
import { copyFile, mkdtemp, rm, rmdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

class Element {
    constructor() {
        this.dataset = {}; this.style = {}; this.children = []; this.listeners = {};
        this.textContent = ''; this.value = ''; this.disabled = false;
        this.classes = new Set();
        this.classList = { toggle: (name, enabled) => enabled ? this.classes.add(name) : this.classes.delete(name) };
    }
    appendChild(child) {
        this.children = this.children.filter(item => item !== child);
        this.children.push(child); return child;
    }
    replaceChildren(...children) { this.children = children; }
    addEventListener(name, callback) { (this.listeners[name] ??= []).push(callback); }
    dispatchEvent(event) { (this.listeners[event.type] ?? []).forEach(callback => callback(event)); }
    querySelector(selector) { return this.parts[selector]; }
    querySelectorAll() { return this.children; }
    get selectedOptions() { return [{ textContent: this.optionNames[this.value] }]; }
}

let imports = 0;
let cases = 0;
const directory = await mkdtemp(join(tmpdir(), 'stand-wind-tests-'));
const load = async file => {
    const target = join(directory, `${imports++}.mjs`);
    await copyFile(new URL(`../../app/static/${file}`, import.meta.url), target);
    await import(pathToFileURL(target).href);
};

async function page(actualWind = 180, { map = true, headings = [0, 180, null] } = {}) {
    const elements = Object.fromEntries([
        'wind-controls', 'wind-override', 'wind-reset', 'wind-status', 'wind-grade-title',
        'stand-rows', 'stand-map', 'map-status', 'map-tiles-status', 'add-on-map', 'fit-map', 'map-data',
    ].map(id => [id, new Element()]));
    elements['wind-controls'].dataset.actualWind = actualWind === null ? '' : String(actualWind);
    elements['stand-map'].dataset.mode = 'dashboard';
    elements['wind-override'].optionNames = {
        '0': 'North', '22.5': 'North-northeast', '67.5': 'East-northeast',
        '90': 'East', '157.5': 'South-southeast', '180': 'South', '202.5': 'South-southwest',
    };
    const rows = headings.map((degree, index) => {
        const row = new Element();
        row.dataset = { standId: String(index + 1), facing: degree === null ? '' : String(degree) };
        row.parts = { '[data-wind-grade]': new Element(), '.wind-arrow': new Element() };
        return row;
    });
    elements['stand-rows'].children = [...rows];
    const located = headings.map((degree, index) => ({
        id: index + 1, name: `Stand ${index + 1}`, degree, latitude: 34, longitude: -81,
        score: null, edit_url: '/edit', delete_url: '/delete',
    }));
    elements['map-data'].textContent = JSON.stringify({
        property: { name: 'Test Property', latitude: 34, longitude: -81 }, stands: located,
        new_stand_url: '/new', csrf_token: 'test-token',
    });
    const document = new Element();
    document.getElementById = id => elements[id] ?? null;
    document.createElement = () => new Element();
    document.querySelectorAll = () => [];
    const window = new Element();
    const forbidden = () => { throw new Error('Preview must not make requests or persist data'); };
    window.fetch = forbidden; window.localStorage = { setItem: forbidden };
    window.sessionStorage = { setItem: forbidden };
    const markers = [];
    const leafletMap = { setView() { return this; }, fitBounds() {}, on() {}, getZoom() { return 17; } };
    const layer = () => ({ addTo() { return this; }, on() {}, bindPopup() {} });
    const L = {
        map: () => leafletMap, tileLayer: layer, circleMarker: layer,
        control: { layers: () => ({ addTo() {} }) }, divIcon: options => options,
        marker: (position, options) => {
            const marker = {
                options, addTo() { return this; }, bindTooltip() {}, bindPopup(popup) { this.popup = popup; },
                setIcon(icon) { this.options.icon = icon; },
            };
            markers.push(marker); return marker;
        },
    };
    Object.assign(globalThis, { document, window, L, fetch: forbidden,
        localStorage: window.localStorage, sessionStorage: window.sessionStorage,
        CustomEvent: class { constructor(type, options) { this.type = type; this.detail = options.detail; } },
    });
    window.L = map ? L : null;
    await load('maps.js'); // Missing-Leaflet fallback must not break wind controls.
    await load('wind.js');
    return {
        elements, rows, markers,
        choose(value) { elements['wind-override'].value = String(value); elements['wind-override'].dispatchEvent({ type: 'change' }); },
        reset() { elements['wind-reset'].dispatchEvent({ type: 'click' }); },
        reload() { window.dispatchEvent({ type: 'pageshow' }); },
        grade(index) { return rows[index].parts['[data-wind-grade]'].children[0].textContent; },
    };
}

try {
    let p = await page();
    assert.equal(p.grade(0), '100%'); assert.equal(p.grade(1), '0%');
    p.choose(180); // Wind from south travels north: south-facing stand becomes ideal.
    assert.equal(p.grade(0), '0%'); assert.equal(p.grade(1), '100%');
    assert.equal(p.elements['stand-rows'].children[0], p.rows[1]);
    assert.equal(p.grade(2), 'Unavailable');
    assert.equal(p.rows[0].parts['.wind-arrow'].style.transform, 'rotate(0deg)');
    assert.match(p.elements['wind-status'].textContent, /From the south/);
    assert.equal(p.elements['wind-grade-title'].textContent, 'Preview Grade');
    assert.match(p.markers[1].options.icon.html.className, /good/);
    assert.match(p.markers[1].popup.children[1].textContent, /100% preview grade/);
    p.reset();
    assert.equal(p.grade(0), '100%'); assert.equal(p.elements['stand-rows'].children[0], p.rows[0]);
    assert.equal(p.elements['wind-grade-title'].textContent, 'Current Grade');
    assert.match(p.markers[0].popup.children[1].textContent, /100% grade/);
    assert.equal(p.elements['wind-reset'].disabled, true);
    cases++;

    p.choose(90); assert.equal(p.grade(0), '50%'); assert.equal(p.grade(1), '50%');
    assert.equal(p.elements['stand-rows'].children[0], p.rows[0]); // Stable order for ties.
    for (const [source, grade] of [[22.5, '88%'], [67.5, '62%'], [157.5, '12%']]) {
        p.choose(source); assert.equal(p.grade(0), grade); // Python's halfway rounding.
    }
    p.reload();
    assert.equal(p.elements['wind-override'].value, ''); assert.equal(p.grade(0), '100%');
    assert.equal(p.elements['wind-controls'].classes.has('is-overridden'), false);
    cases++;

    p = await page(null, { map: false });
    assert.equal(p.grade(0), 'Unavailable'); assert.equal(p.rows[0].parts['.wind-arrow'].hidden, true);
    assert.equal(p.elements['wind-override'].disabled, false);
    p.choose(0); assert.equal(p.grade(0), '100%'); assert.equal(p.rows[0].parts['.wind-arrow'].hidden, false);
    p.reset(); assert.equal(p.grade(0), 'Unavailable');
    assert.match(p.elements['wind-status'].textContent, /Actual wind is unavailable/);
    cases++;

    p = await page(0, { headings: [0, 180, 360] });
    assert.equal(p.grade(0), '0%'); assert.equal(p.grade(1), '100%'); assert.equal(p.grade(2), '0%');
    p.choose(0); assert.equal(p.grade(0), '100%'); assert.equal(p.grade(2), '100%');
    p.reload(); assert.equal(p.grade(1), '100%');
    cases++;

    p = await page(null, { headings: [] });
    p.choose(202.5); assert.match(p.elements['wind-status'].textContent, /south-southwest/);
    p.reset();
    cases++;
    console.log(`Passed ${cases} wind interaction scenarios (grades, rankings, map popups, reset, reload, missing weather/library, and no persistence).`);
} finally {
    for (let index = 0; index < imports; index++) await rm(join(directory, `${index}.mjs`), { force: true });
    await rmdir(directory);
}
