/* Device location fills the stand form only; Save Stand persists the selection. */
(() => {
    'use strict';
    const button = document.getElementById('find-stand-location');
    if (!button) return;
    const status = document.getElementById('stand-location-status');
    const latitude = document.getElementById('lat-input');
    const longitude = document.getElementById('lng-input');

    const finish = message => {
        button.disabled = false;
        button.removeAttribute('aria-busy');
        status.textContent = message;
    };
    const onError = error => {
        const messages = {
            1: 'Location access was denied. Allow location access in your browser and device settings, then try again, or choose a point on the map.',
            2: 'Your device could not determine your location. Try again outdoors, choose a point on the map, or enter coordinates.',
            3: 'Finding your location timed out. Try again, choose a point on the map, or enter coordinates.',
        };
        finish(messages[error.code] || 'Unable to find your location. Try again, choose a point on the map, or enter coordinates.');
    };

    button.disabled = false;
    button.addEventListener('click', () => {
        if (window.isSecureContext === false) {
            finish('Location access requires a secure connection (HTTPS). Open the app over HTTPS, choose a point on the map, or enter coordinates.');
            return;
        }
        if (!navigator.geolocation) {
            finish('Location services are not available in this browser. Choose a point on the map or enter coordinates.');
            return;
        }
        button.disabled = true;
        button.setAttribute('aria-busy', 'true');
        status.textContent = 'Finding your location...';
        try {
            navigator.geolocation.getCurrentPosition(position => {
                const { latitude: lat, longitude: lng, accuracy } = position.coords;
                if (!Number.isFinite(lat) || !Number.isFinite(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
                    finish('Your device returned an invalid location. Try again, choose a point on the map, or enter coordinates.');
                    return;
                }
                latitude.value = lat.toFixed(6);
                longitude.value = lng.toFixed(6);
                document.dispatchEvent(new CustomEvent('stand-location-found'));
                const precision = Number.isFinite(accuracy) && accuracy >= 0 ? ` (accuracy about ${Math.ceil(accuracy)} meters)` : '';
                finish(`Location found${precision}. Review the location and select Save Stand to keep it.`);
            }, onError, { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 });
        } catch (error) {
            onError({ code: error.name === 'SecurityError' ? 1 : 0 });
        }
    });
})();
