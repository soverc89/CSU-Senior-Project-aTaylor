/* Keep the stand list within easy reach on phones; desktop panels stay open. */
(() => {
    'use strict';
    const panels = document.querySelectorAll('.dashboard-panel');
    if (!panels.length) return;
    const mobile = window.matchMedia('(max-width: 720px)');
    const updateLayout = () => panels.forEach(panel => {
        panel.open = !mobile.matches;
        panel.querySelector('summary').tabIndex = mobile.matches ? 0 : -1;
    });
    panels.forEach(panel => panel.addEventListener('toggle', () => {
        if (!mobile.matches) panel.open = true;
    }));
    mobile.addEventListener('change', updateLayout);
    updateLayout();
})();
