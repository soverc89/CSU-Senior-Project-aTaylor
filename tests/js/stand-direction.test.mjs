// Run with: node tests/js/stand-direction.test.mjs
// Exercises pointer/keyboard input and the actual editor map script with test doubles.
import assert from 'node:assert/strict';
import { copyFile, mkdtemp, rm, rmdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

class Element {
    constructor() {
        this.dataset = {}; this.style = {}; this.value = ''; this.children = []; this.listeners = {};
        this.attributes = {}; this.classes = new Set(); this.captured = new Set();
        this.classList = { toggle: (name, on) => on ? this.classes.add(name) : this.classes.delete(name) };
    }
    addEventListener(type, callback) { (this.listeners[type] ??= []).push(callback); }
    dispatchEvent(event) { (this.listeners[event.type] ?? []).forEach(callback => callback(event)); }
    setAttribute(name, value) { this.attributes[name] = value; }
    appendChild(child) { this.children.push(child); return child; }
    focus() { this.focused = true; }
    getBoundingClientRect() { return { left: 20, top: 40, width: 180, height: 180 }; }
    setPointerCapture(id) { this.captured.add(id); }
    hasPointerCapture(id) { return this.captured.has(id); }
    releasePointerCapture(id) { this.captured.delete(id); }
}

let imports = 0;
let cases = 0;
const directory = await mkdtemp(join(tmpdir(), 'stand-direction-tests-'));
const load = async file => {
    const target = join(directory, `${imports++}.mjs`);
    await copyFile(new URL(`../../app/static/${file}`, import.meta.url), target);
    await import(pathToFileURL(target).href);
};

async function page(initial = '', map = true) {
    const elements = Object.fromEntries([
        'stand-direction-control', 'stand-direction-dial', 'stand-direction-arrow', 'stand-direction-value',
        'deg-input', 'lat-input', 'lng-input', 'stand-map', 'map-status', 'map-tiles-status',
        'clear-map-location', 'fit-map', 'map-data',
    ].map(id => [id, new Element()]));
    elements['stand-direction-control'].hidden = true;
    elements['deg-input'].value = initial;
    elements['lat-input'].value = '34'; elements['lng-input'].value = '-81';
    elements['stand-map'].dataset.mode = 'editor';
    elements['map-data'].textContent = JSON.stringify({ property: { name: 'Property', latitude: 34, longitude: -81 }, stands: [] });
    const document = new Element();
    document.getElementById = id => elements[id] ?? null;
    document.createElement = () => new Element();
    const markers = [];
    const leafletMap = { setView() { return this; }, fitBounds() {}, on() {}, removeLayer() {}, panTo() {} };
    const L = {
        map: () => leafletMap, tileLayer: () => ({ addTo() {}, on() {} }),
        circleMarker: () => ({ addTo() { return this; }, bindPopup() {} }),
        control: { layers: () => ({ addTo() {} }) }, divIcon: options => options,
        marker: (position, options) => {
            const marker = {
                options, addTo() { return this; }, on() {}, setLatLng() { return this; },
                setIcon(icon) { this.options.icon = icon; return this; },
            };
            markers.push(marker); return marker;
        },
    };
    Object.assign(globalThis, { document, L, window: { L: map ? L : null },
        Event: class { constructor(type) { this.type = type; } },
    });
    await load('maps.js'); await load('stand-direction.js');
    const dial = elements['stand-direction-dial'];
    const input = elements['deg-input'];
    return {
        elements, dial, input, markers,
        pointer(type, heading, extra = {}) {
            const radians = heading * Math.PI / 180;
            const event = {
                type, pointerId: 1, pointerType: 'mouse', isPrimary: true, button: 0,
                clientX: 110 + Math.sin(radians) * 80, clientY: 130 - Math.cos(radians) * 80,
                preventDefault() {}, ...extra,
            };
            dial.dispatchEvent(event);
        },
        key(key, shiftKey = false) {
            const event = { type: 'keydown', key, shiftKey, prevented: false, preventDefault() { this.prevented = true; } };
            dial.dispatchEvent(event); return event;
        },
        type(value, event = 'input') { input.value = value; input.dispatchEvent(new Event(event)); },
        pinRotation() { return markers[0].options.icon.html.children[0].style.transform; },
    };
}

try {
    let p = await page();
    assert.equal(p.elements['stand-direction-control'].hidden, false);
    assert.equal(p.input.value, '', 'Opening a form must not invent a saved heading');
    assert.equal(p.dial.attributes['aria-valuetext'], 'No direction selected');
    assert.equal(p.dial.classes.has('is-unset'), true);
    cases++;

    p.pointer('pointerdown', 0);
    assert.equal(p.input.value, '0'); assert.equal(p.dial.hasPointerCapture(1), true);
    for (const heading of [45, 90, 135, 180, 225, 270, 315]) {
        p.pointer('pointermove', heading);
        assert.equal(p.input.value, String(heading));
        assert.equal(p.elements['stand-direction-arrow'].style.transform, `rotate(${heading}deg)`);
        assert.equal(p.pinRotation(), `rotate(${heading}deg)`);
    }
    p.pointer('pointerup', 270);
    assert.equal(p.dial.hasPointerCapture(1), false);
    p.pointer('pointermove', 90); assert.equal(p.input.value, '270');
    cases++;

    p = await page();
    p.pointer('pointerdown', 0, { clientX: 110, clientY: 130 });
    assert.equal(p.input.value, '');
    p.pointer('pointercancel', 0);
    p.pointer('pointerdown', 90, { button: 2 }); assert.equal(p.input.value, '');
    p.pointer('pointerdown', 180, { pointerType: 'touch' }); assert.equal(p.input.value, '180');
    p.pointer('pointermove', 90, { pointerId: 2 }); assert.equal(p.input.value, '180');
    p.pointer('lostpointercapture', 0);
    p.pointer('pointermove', 90); assert.equal(p.input.value, '180');
    assert.equal(p.dial.classes.has('is-dragging'), false);
    cases++;

    p = await page();
    p.pointer('pointerdown', 359.4); assert.equal(p.input.value, '359');
    p.pointer('pointermove', 359.7); assert.equal(p.input.value, '0');
    p.pointer('pointerup', 0.4); assert.equal(p.input.value, '0');
    cases++;

    p = await page('359');
    assert.equal(p.key('ArrowRight').prevented, true); assert.equal(p.input.value, '0');
    p.key('ArrowLeft'); assert.equal(p.input.value, '359');
    p.key('ArrowDown', true); assert.equal(p.input.value, '344');
    p.key('PageUp'); assert.equal(p.input.value, '359');
    p.key('Home'); assert.equal(p.input.value, '0');
    p.key('End'); assert.equal(p.input.value, '359');
    assert.equal(p.key('Enter').prevented, false);
    assert.equal(p.pinRotation(), 'rotate(359deg)');
    cases++;

    p = await page('225');
    assert.equal(p.input.value, '225'); assert.match(p.elements['stand-direction-value'].textContent, /Southwest/);
    p.type('360'); assert.equal(p.input.value, '360');
    assert.equal(p.elements['stand-direction-arrow'].style.transform, 'rotate(0deg)');
    assert.equal(p.dial.attributes['aria-valuenow'], '0'); assert.match(p.dial.attributes['aria-valuetext'], /North/);
    p.type('90', 'change'); assert.equal(p.elements['stand-direction-arrow'].style.transform, 'rotate(90deg)');
    for (const invalid of ['90.5', '361', '']) {
        p.type(invalid); assert.equal(p.input.value, invalid); assert.equal(p.dial.classes.has('is-unset'), true);
    }
    cases++;

    p = await page('360', false);
    assert.equal(p.input.value, '360');
    p.key('ArrowUp'); assert.equal(p.input.value, '1');
    p.pointer('pointerdown', 90); assert.equal(p.input.value, '90');
    cases++;

    globalThis.document = { getElementById: () => null };
    await load('stand-direction.js'); // Other pages have no direction control.
    cases++;
    console.log(`Passed ${cases} stand direction scenarios (drag/touch, compass quadrants, wraparound, keyboard, saved/manual values, map arrow updates, and missing map).`);
} finally {
    for (let index = 0; index < imports; index++) await rm(join(directory, `${index}.mjs`), { force: true });
    await rmdir(directory);
}
