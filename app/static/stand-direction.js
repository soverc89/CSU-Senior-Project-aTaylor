/* The degree input remains the saved value; the dial is a visual way to set it. */
(() => {
    'use strict';
    const control = document.getElementById('stand-direction-control');
    if (!control) return;
    const dial = document.getElementById('stand-direction-dial');
    const arrow = document.getElementById('stand-direction-arrow');
    const input = document.getElementById('deg-input');
    const output = document.getElementById('stand-direction-value');
    const names = ['North', 'Northeast', 'East', 'Southeast', 'South', 'Southwest', 'West', 'Northwest'];
    let activePointer = null;
    const currentHeading = () => {
        if (input.value.trim() === '') return null;
        const heading = Number(input.value);
        return Number.isInteger(heading) && heading >= 0 && heading <= 360 ? heading : null;
    };
    const sync = () => {
        const heading = currentHeading();
        const rotation = heading === null ? 0 : heading % 360;
        const description = heading === null ? 'No direction selected' : `${names[Math.round(rotation / 45) % 8]} (${heading}°)`;
        arrow.style.transform = `rotate(${rotation}deg)`;
        dial.classList.toggle('is-unset', heading === null);
        dial.setAttribute('aria-valuenow', String(rotation));
        dial.setAttribute('aria-valuetext', description);
        output.textContent = heading === null ? 'Choose a direction or enter a whole degree from 0 to 360.' : `Stand faces ${description}`;
    };
    const setHeading = heading => {
        input.value = String((heading % 360 + 360) % 360);
        // The same event updates both the dial and the editor's stand-pin arrow.
        input.dispatchEvent(new Event('input', { bubbles: true }));
    };
    const pointAt = event => {
        const bounds = dial.getBoundingClientRect();
        const x = event.clientX - (bounds.left + bounds.width / 2);
        const y = event.clientY - (bounds.top + bounds.height / 2);
        if (Math.hypot(x, y) < 8) return; // The center has no meaningful direction.
        setHeading(Math.round(Math.atan2(x, -y) * 180 / Math.PI));
    };
    const stopDragging = event => {
        if (event.pointerId !== activePointer) return;
        activePointer = null;
        dial.classList.toggle('is-dragging', false);
        if (dial.hasPointerCapture(event.pointerId)) dial.releasePointerCapture(event.pointerId);
    };

    dial.addEventListener('pointerdown', event => {
        if (activePointer !== null || event.isPrimary === false || event.button !== 0) return;
        event.preventDefault();
        dial.focus({ preventScroll: true });
        activePointer = event.pointerId;
        dial.setPointerCapture(activePointer);
        dial.classList.toggle('is-dragging', true);
        pointAt(event);
    });
    dial.addEventListener('pointermove', event => {
        if (activePointer !== null && event.pointerId === activePointer) pointAt(event);
    });
    dial.addEventListener('pointerup', event => {
        if (activePointer !== null && event.pointerId === activePointer) pointAt(event);
        stopDragging(event);
    });
    dial.addEventListener('pointercancel', stopDragging);
    dial.addEventListener('lostpointercapture', stopDragging);
    dial.addEventListener('keydown', event => {
        const heading = (currentHeading() ?? 0) % 360;
        const step = event.shiftKey ? 15 : 1;
        const choices = {
            ArrowRight: heading + step, ArrowUp: heading + step,
            ArrowLeft: heading - step, ArrowDown: heading - step,
            PageUp: heading + 15, PageDown: heading - 15, Home: 0, End: 359,
        };
        if (!Object.hasOwn(choices, event.key)) return;
        event.preventDefault();
        setHeading(choices[event.key]);
    });
    input.addEventListener('input', sync);
    input.addEventListener('change', sync);
    sync();
    control.hidden = false;
})();
