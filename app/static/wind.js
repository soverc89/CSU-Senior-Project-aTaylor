/* Wind previews live only in this page: no requests, storage, or cache writes. */
(() => {
    'use strict';
    const panel = document.getElementById('wind-controls');
    if (!panel) return;
    const select = document.getElementById('wind-override');
    const reset = document.getElementById('wind-reset');
    const status = document.getElementById('wind-status');
    const gradeTitle = document.getElementById('wind-grade-title');
    const table = document.getElementById('stand-rows');
    const rows = table ? Array.from(table.querySelectorAll('[data-stand-id]')) : [];
    const actualWind = panel.dataset.actualWind === '' ? null : Number(panel.dataset.actualWind);
    // Keep the original order for equal grades and when actual weather is unavailable.
    const originalOrder = new Map(rows.map((row, index) => [row, index]));

    const scoreFor = (facing, wind) => {
        if (facing === '' || wind === null) return null;
        const difference = 180 - Math.abs(Math.abs(wind - Number(facing)) - 180);
        const score = difference / 180 * 100;
        // Match Python round(): exactly halfway scores round to the nearest even integer.
        const floor = Math.floor(score);
        return score - floor === 0.5 ? floor + floor % 2 : Math.round(score);
    };

    const update = () => {
        const overridden = select.value !== '';
        const wind = overridden ? (Number(select.value) + 180) % 360 : actualWind;
        panel.classList.toggle('is-overridden', overridden);
        reset.disabled = !overridden;
        status.textContent = overridden
            ? `Preview wind: From the ${select.selectedOptions[0].textContent.toLowerCase()}. Grades and map colors show this temporary override. Refresh to restore actual wind.`
            : actualWind === null ? 'Actual wind is unavailable. Choose a wind to preview stand grades.'
                : "Grades use the property's actual wind.";
        if (gradeTitle) gradeTitle.textContent = overridden ? 'Preview Grade' : 'Current Grade';
        const scores = new Map();
        const standScores = [];
        rows.forEach(row => {
            const score = scoreFor(row.dataset.facing, wind);
            scores.set(row, score);
            standScores.push({ id: Number(row.dataset.standId), score });
            const badge = document.createElement('span');
            badge.className = `wind-grade ${score === null ? 'unknown' : score >= 80 ? 'good' : score >= 50 ? 'fair' : 'poor'}`;
            badge.textContent = score === null ? 'Unavailable' : `${score}%`;
            row.querySelector('[data-wind-grade]').replaceChildren(badge);
            const arrow = row.querySelector('.wind-arrow');
            arrow.hidden = wind === null;
            arrow.style.transform = `rotate(${wind === null ? 0 : wind}deg)`;
        });
        rows.sort((a, b) => ((scores.get(b) ?? -1) - (scores.get(a) ?? -1))
            || originalOrder.get(a) - originalOrder.get(b));
        rows.forEach(row => table.appendChild(row));
        document.dispatchEvent(new CustomEvent('wind-preview-change', { detail: { standScores, overridden } }));
    };

    const restoreActual = () => {
        select.value = '';
        update();
    };
    select.disabled = false;
    select.addEventListener('change', update);
    reset.addEventListener('click', restoreActual);
    // Reset restored form state on reload and when returning through the back/forward cache.
    window.addEventListener('pageshow', restoreActual);
    restoreActual();
})();
