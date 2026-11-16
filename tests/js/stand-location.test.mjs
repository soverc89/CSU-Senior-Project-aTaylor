// Run with: node tests/js/stand-location.test.mjs
// Browser/device location is simulated; no physical location is requested.
import assert from 'node:assert/strict';
import { copyFile, mkdtemp, rm, rmdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

class Element {
    constructor() { this.dataset = {}; this.style = {}; this.value = ''; this.listeners = {}; this.attributes = {}; this.children = []; }
    addEventListener(type, callback) { (this.listeners[type] ??= []).push(callback); }
    dispatchEvent(event) { (this.listeners[event.type] ?? []).forEach(callback => callback(event)); }
    appendChild(child) { this.children.push(child); return child; }
    setAttribute(name, value) { this.attributes[name] = value; }
    removeAttribute(name) { delete this.attributes[name]; }
}

let imports = 0;
let cases = 0;
const directory = await mkdtemp(join(tmpdir(), 'stand-location-tests-'));
const load = async file => {
    const target = join(directory, `${imports++}.mjs`);
    await copyFile(new URL(`../../app/static/${file}`, import.meta.url), target);
    await import(pathToFileURL(target).href);
};

async function page({ map = true, supported = true, secure = true, initial = ['', ''], throws = null } = {}) {
    const elements = Object.fromEntries([
        'find-stand-location', 'stand-location-status', 'lat-input', 'lng-input', 'deg-input',
        'stand-map', 'map-status', 'map-tiles-status', 'clear-map-location', 'fit-map', 'map-data',
    ].map(id => [id, new Element()]));
    elements['stand-map'].dataset.mode = 'editor';
    elements['lat-input'].value = initial[0]; elements['lng-input'].value = initial[1];
    elements['deg-input'].value = '0';
    elements['map-data'].textContent = JSON.stringify({
        property: { name: 'Property', latitude: 34, longitude: -81 }, stands: [],
    });
    const document = new Element();
    document.getElementById = id => elements[id] ?? null;
    document.createElement = () => new Element();
    const markers = [], views = [], calls = [];
    const leafletMap = {
        setView(position, zoom) { views.push({ position, zoom }); return this; },
        fitBounds() {}, on() {}, removeLayer() {}, panTo() {},
    };
    const L = {
        map: () => leafletMap,
        tileLayer: () => ({ addTo() {}, on() {} }),
        circleMarker: () => ({ addTo() { return this; }, bindPopup() {} }),
        control: { layers: () => ({ addTo() {} }) }, divIcon: options => options,
        marker: (position, options) => {
            const marker = {
                position, options, addTo() { return this; }, on() {},
                setLatLng(next) { this.position = next; return this; },
                setIcon(icon) { this.options.icon = icon; return this; },
            };
            markers.push(marker); return marker;
        },
    };
    const navigator = supported ? { geolocation: { getCurrentPosition(success, failure, options) {
        if (throws) throw throws;
        calls.push({ success, failure, options });
    } } } : {};
    Object.defineProperty(globalThis, 'navigator', { value: navigator, configurable: true });
    Object.assign(globalThis, { document, L, window: { L: map ? L : null, isSecureContext: secure },
        CustomEvent: class { constructor(type) { this.type = type; } },
    });
    await load('maps.js');
    await load('stand-location.js');
    assert.equal(calls.length, 0, 'Location must only be requested after a click');
    return {
        elements, markers, views, calls,
        click() { elements['find-stand-location'].dispatchEvent({ type: 'click' }); },
        success(latitude, longitude, accuracy = 8.2) { calls.at(-1).success({ coords: { latitude, longitude, accuracy } }); },
        error(code) { calls.at(-1).failure({ code }); },
    };
}

try {
    let p = await page();
    p.click();
    assert.equal(p.elements['find-stand-location'].disabled, true);
    assert.equal(p.elements['find-stand-location'].attributes['aria-busy'], 'true');
    assert.deepEqual(p.calls[0].options, { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 });
    p.success(34.0012344, -81.0023454);
    assert.equal(p.elements['lat-input'].value, '34.001234');
    assert.equal(p.elements['lng-input'].value, '-81.002345');
    assert.deepEqual(p.markers[0].position, [34.001234, -81.002345]);
    assert.deepEqual(p.views.at(-1), { position: [34.001234, -81.002345], zoom: 17 });
    assert.match(p.elements['stand-location-status'].textContent, /accuracy about 9 meters/);
    assert.match(p.elements['stand-location-status'].textContent, /Save Stand/);
    assert.equal(p.elements['find-stand-location'].disabled, false);
    cases++;

    p = await page({ initial: ['34', '-81'] });
    p.click(); p.success(0, 0);
    assert.equal(p.elements['lat-input'].value, '0.000000');
    assert.equal(p.elements['lng-input'].value, '0.000000');
    assert.equal(p.markers.length, 1, 'Reuse the editor pin when locating again');
    assert.deepEqual(p.markers[0].position, [0, 0]);
    cases++;

    p = await page({ map: false });
    p.click(); p.success(34, -81);
    assert.equal(p.elements['lat-input'].value, '34.000000');
    assert.equal(p.elements['lng-input'].value, '-81.000000');
    cases++;

    for (const [code, message] of [[1, /denied/], [2, /could not determine/], [3, /timed out/], [99, /Unable to find/]]) {
        p = await page({ initial: ['34', '-81'] });
        p.click(); p.error(code);
        assert.match(p.elements['stand-location-status'].textContent, message);
        assert.equal(p.elements['lat-input'].value, '34'); assert.equal(p.elements['lng-input'].value, '-81');
        assert.equal(p.elements['find-stand-location'].disabled, false);
        p.click(); assert.equal(p.calls.length, 2, 'Allow retry after a failed lookup');
        cases++;
    }
    for (const [options, message] of [[{ supported: false }, /not available/], [{ secure: false }, /HTTPS/]]) {
        p = await page(options); p.click();
        assert.equal(p.calls.length, 0); assert.match(p.elements['stand-location-status'].textContent, message);
        cases++;
    }
    for (const coords of [[91, -81], [34, Infinity]]) {
        p = await page({ initial: ['34', '-81'] }); p.click(); p.success(...coords);
        assert.match(p.elements['stand-location-status'].textContent, /invalid location/);
        assert.equal(p.elements['lat-input'].value, '34'); assert.equal(p.elements['lng-input'].value, '-81');
        cases++;
    }
    p = await page({ throws: Object.assign(new Error('Blocked'), { name: 'SecurityError' }) });
    p.click(); assert.match(p.elements['stand-location-status'].textContent, /denied/);
    assert.equal(p.elements['find-stand-location'].disabled, false);
    cases++;
    console.log(`Passed ${cases} stand location scenarios (device lookup, map centering, zero coordinates, retries, permission/timeout failures, and map fallback).`);
} finally {
    for (let index = 0; index < imports; index++) await rm(join(directory, `${index}.mjs`), { force: true });
    await rmdir(directory);
}
