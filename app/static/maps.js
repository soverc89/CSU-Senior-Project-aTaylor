/* Property weather location and stand map positions are deliberately separate. */
(() => {
    'use strict';
    const element = document.getElementById('stand-map');
    if (!element) return;
    const status = document.getElementById('map-status');
    const tileStatus = document.getElementById('map-tiles-status');
    const addButton = document.getElementById('add-on-map');
    const clearButton = document.getElementById('clear-map-location');
    if (!window.L) {
        status.textContent = 'The map could not load. You can still manage stands using the form and coordinates.';
        if (addButton) addButton.disabled = true;
        if (clearButton) clearButton.disabled = true;
        return;
    }
    const data = JSON.parse(document.getElementById('map-data').textContent);
    const editor = element.dataset.mode === 'editor';
    const latitudeInput = document.getElementById('lat-input');
    const longitudeInput = document.getElementById('lng-input');
    const headingInput = document.getElementById('deg-input');
    const panel = element.closest('.dashboard-panel');
    let needsInitialFit = panel && !panel.open;
    const map = L.map(element, { scrollWheelZoom: false }).setView([39.5, -98.35], 4);
    const satellite = L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxNativeZoom: 19, maxZoom: 20,
        attribution: 'Tiles &copy; Esri &mdash; Esri, Vantor, Earthstar Geographics, and the GIS User Community',
    });
    const streets = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxNativeZoom: 19, maxZoom: 20,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
    });
    let activeLayer = satellite;
    satellite.addTo(map);
    L.control.layers({ Satellite: satellite, Streets: streets }, null, { collapsed: false }).addTo(map);
    map.on('baselayerchange', event => {
        activeLayer = event.layer;
        tileStatus.textContent = '';
    });
    [satellite, streets].forEach(layer => {
        layer.on('tileerror', () => {
            if (activeLayer === layer) tileStatus.textContent = 'Some map images could not load. Try the other map layer. Coordinate entry still works.';
        });
    });

    const numberValue = input => input && input.value.trim() !== '' ? Number(input.value) : null;
    const locationValid = (latitude, longitude) => Number.isFinite(latitude) && Number.isFinite(longitude)
        && latitude >= -90 && latitude <= 90 && longitude >= -180 && longitude <= 180;
    const gradeClass = score => score === null ? 'unknown' : score >= 80 ? 'good' : score >= 50 ? 'fair' : 'poor';
    const pinIcon = (degree, color) => {
        const pin = document.createElement('div');
        pin.className = `stand-pin ${color}`;
        if (Number.isFinite(degree)) {
            const arrow = document.createElement('span');
            arrow.className = 'stand-pin-arrow';
            arrow.style.transform = `rotate(${degree}deg)`;
            pin.appendChild(arrow);
        } else {
            pin.textContent = '+';
        }
        return L.divIcon({ className: 'stand-map-icon', html: pin, iconSize: [36, 36], iconAnchor: [18, 18] });
    };
    const textElement = (tag, text) => {
        const node = document.createElement(tag);
        node.textContent = text;
        return node;
    };
    const propertyLocation = data.property;
    const bounds = [];
    if (locationValid(propertyLocation.latitude, propertyLocation.longitude)) {
        const position = [propertyLocation.latitude, propertyLocation.longitude];
        const reference = L.circleMarker(position, { radius: 7, color: '#fff', weight: 2, fillColor: '#176fc1', fillOpacity: 1 }).addTo(map);
        reference.bindPopup(textElement('p', `${propertyLocation.name}: property weather location`));
        bounds.push(position);
    }

    const markers = new Map();
    const markerGrades = new Map();
    const gradeText = (stand, preview) => `${stand.degree === null ? 'Heading not set' : `${stand.degree}° facing`} · ${stand.score === null ? 'Grade unavailable' : `${stand.score}% ${preview ? 'preview grade' : 'grade'}`}`;
    data.stands.forEach(stand => {
        const position = [stand.latitude, stand.longitude];
        bounds.push(position);
        const marker = L.marker(position, { icon: pinIcon(stand.degree, gradeClass(stand.score)), title: stand.name }).addTo(map);
        marker.bindTooltip(textElement('span', stand.name));
        const popup = document.createElement('div');
        popup.className = 'map-popup';
        popup.appendChild(textElement('strong', stand.name));
        const grade = textElement('p', gradeText(stand, false));
        popup.appendChild(grade);
        markerGrades.set(String(stand.id), grade);
        const actions = document.createElement('div');
        actions.className = 'map-popup-actions';
        const editLink = textElement('a', 'Edit stand');
        editLink.href = stand.edit_url;
        actions.appendChild(editLink);
        const deleteForm = document.createElement('form');
        deleteForm.method = 'POST';
        deleteForm.action = stand.delete_url;
        if (data.csrf_token) {
            const token = document.createElement('input');
            token.type = 'hidden';
            token.name = 'csrf_token';
            token.value = data.csrf_token;
            deleteForm.appendChild(token);
        }
        const deleteButton = textElement('button', 'Delete');
        deleteButton.type = 'submit';
        deleteForm.appendChild(deleteButton);
        // Only the dashboard offers deletion; editor neighbor pins are for orientation.
        if (!editor) actions.appendChild(deleteForm);
        deleteForm.addEventListener('submit', event => {
            if (!window.confirm(`Delete ${stand.name}?`)) event.preventDefault();
        });
        popup.appendChild(actions);
        marker.bindPopup(popup);
        markers.set(String(stand.id), marker);
    });

    if (!editor) document.addEventListener('wind-preview-change', event => {
        const scores = new Map(event.detail.standScores.map(stand => [stand.id, stand.score]));
        data.stands.forEach(stand => {
            if (!scores.has(stand.id)) return;
            const score = scores.get(stand.id);
            markers.get(String(stand.id)).setIcon(pinIcon(stand.degree, gradeClass(score)));
            markerGrades.get(String(stand.id)).textContent = gradeText({ ...stand, score }, event.detail.overridden);
        });
    });

    let pickedMarker = null;
    const selectedLocation = () => [numberValue(latitudeInput), numberValue(longitudeInput)];
    const setPickedLocation = position => {
        const latitude = Math.max(-90, Math.min(90, position.lat));
        const longitude = ((position.lng + 180) % 360 + 360) % 360 - 180;
        latitudeInput.value = latitude.toFixed(6);
        longitudeInput.value = longitude.toFixed(6);
        updatePickedMarker();
    };
    const updatePickedMarker = () => {
        const [latitude, longitude] = selectedLocation();
        if (!locationValid(latitude, longitude)) {
            if (pickedMarker) map.removeLayer(pickedMarker);
            pickedMarker = null;
            status.textContent = 'Click the map to choose a location, or enter both coordinates. Save the form to keep your changes.';
            return;
        }
        const icon = pinIcon(numberValue(headingInput), 'pending');
        if (!pickedMarker) {
            pickedMarker = L.marker([latitude, longitude], { icon, draggable: true, title: 'Selected stand location' }).addTo(map);
            pickedMarker.on('dragend', event => setPickedLocation(event.target.getLatLng()));
        } else {
            pickedMarker.setLatLng([latitude, longitude]).setIcon(icon);
        }
        status.textContent = `Selected: ${latitude.toFixed(6)}, ${longitude.toFixed(6)}. Click again or drag the blue pin to move it. Save Stand to keep your changes.`;
    };
    const fitLocations = () => {
        const selected = editor ? selectedLocation() : [null, null];
        if (locationValid(...selected)) map.setView(selected, 17);
        else if (bounds.length) map.fitBounds(bounds, { padding: [35, 35], maxZoom: 17 });
        else map.setView([39.5, -98.35], 4);
    };
    fitLocations();
    const refreshMapLayout = () => {
        map.invalidateSize({ pan: false });
        if (needsInitialFit) {
            fitLocations();
            needsInitialFit = false;
        }
    };
    if (panel) panel.addEventListener('toggle', () => {
        if (panel.open) refreshMapLayout();
    });
    document.getElementById('fit-map').addEventListener('click', fitLocations);

    if (editor) {
        updatePickedMarker();
        document.addEventListener('stand-location-found', () => {
            updatePickedMarker();
            fitLocations();
        });
        map.on('click', event => setPickedLocation(event.latlng));
        [latitudeInput, longitudeInput].forEach(input => input.addEventListener('change', () => {
            updatePickedMarker();
            const selected = selectedLocation();
            if (locationValid(...selected)) map.panTo(selected);
        }));
        if (headingInput) headingInput.addEventListener('input', updatePickedMarker);
        clearButton.addEventListener('click', () => {
            latitudeInput.value = '';
            longitudeInput.value = '';
            updatePickedMarker();
        });
    } else {
        let placing = false;
        let draftMarker = null;
        addButton.addEventListener('click', () => {
            placing = !placing;
            element.classList.toggle('is-placing', placing);
            addButton.textContent = placing ? 'Cancel placement' : 'Add stand on map';
            addButton.setAttribute('aria-pressed', String(placing));
            status.textContent = placing ? 'Click a location on the map, then choose Create stand here.' : 'Select a stand pin to view its grade, edit it, or delete it.';
            if (!placing && draftMarker) {
                map.removeLayer(draftMarker);
                draftMarker = null;
            }
        });
        map.on('click', event => {
            if (!placing) return;
            if (draftMarker) map.removeLayer(draftMarker);
            const point = event.latlng.wrap();
            const popup = document.createElement('div');
            popup.className = 'map-popup';
            popup.appendChild(textElement('strong', 'New stand location'));
            popup.appendChild(textElement('p', `${point.lat.toFixed(6)}, ${point.lng.toFixed(6)}`));
            const link = textElement('a', 'Create stand here');
            const url = new URL(data.new_stand_url, window.location.origin);
            url.searchParams.set('latitude', point.lat.toFixed(6));
            url.searchParams.set('longitude', point.lng.toFixed(6));
            link.href = url.href;
            popup.appendChild(link);
            draftMarker = L.marker(point, { icon: pinIcon(null, 'pending'), title: 'New stand location' }).addTo(map);
            draftMarker.bindPopup(popup).openPopup();
        });
        document.querySelectorAll('[data-focus-stand]').forEach(button => button.addEventListener('click', () => {
            const marker = markers.get(button.dataset.focusStand);
            if (!marker) return;
            if (panel) {
                panel.open = true;
                refreshMapLayout();
            }
            map.setView(marker.getLatLng(), Math.max(map.getZoom(), 17));
            marker.openPopup();
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }));
    }
})();
