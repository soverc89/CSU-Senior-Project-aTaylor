# Property and Stand Map

Implemented October 12, 2026 for Requirements 4, 6, and 7: create stands through a form, place them on a map, and manage saved stands. Device geolocation is available on property and stand forms as of October 20. All stands share weather fetched for the property's coordinates; a stand's device location only sets its map position.

## Using the map

1. Open a property using **View Stands**. The map opens with satellite imagery; select **Streets** to switch to OpenStreetMap.
2. Click **Add stand on map**, then click a location. Select **Create stand here** in the blue pin's popup.
3. The stand form opens with those coordinates. Enter a name and facing direction. Drag the circular direction control's arrow (or tap the circle) to aim the stand; its numeric degree and the map pin arrow update together. Click elsewhere or drag the blue map pin to adjust its position, then select **Save Stand**.
4. Saved pins show stand facing arrows and the same grade colors as the ranked list. Select a pin to view its grade, edit the stand, or delete it with confirmation.
5. Existing stands without coordinates remain in the list. Select **Place on map**, choose their location, and save. **Show on map** focuses a located stand's pin.
6. In the editor, **Clear location** removes the position when the form is saved. It does not delete the stand. **Cancel** discards unsaved changes.
7. When adding a stand in the field, select **Find My Location** in the stand form and allow browser location access. The form fills the device coordinates and centers the blue pin. Check the reported accuracy, adjust the pin if needed, enter the name and facing direction, and select **Save Stand**. The same button is available when editing a stand.

The blue dot on the property map marks the property's weather location. Stand coordinates are only used for map placement. Moving a stand does not trigger a separate weather lookup or change the property coordinates. The dashboard's current-wind label describes where wind comes **from** (for example, "From the northwest"). Blue compass arrows and internal grading headings use the direction wind travels **toward**.

### Stand direction control

The stand creation/edit form includes a circular facing-direction control. Drag with a mouse or touch, or tap a point on the circle. North is up, matching the map; east is right. The arrow, numeric degree input, and editor map pin facing stay synchronized. Direction remains unset on a new form until the user chooses or types a value, and editing preserves the saved value (including 360°).

The control supports keyboard arrow keys in 1° steps, Shift plus an arrow key in 15° steps, Page Up/Down in 15° steps, Home for north, and End for 359°. A focused control has a visible focus ring and announces its heading through slider accessibility attributes. Numeric input remains available if JavaScript is disabled, and the dial works if the map library is unavailable.

`app/static/stand-direction.js` converts pointer positions into clockwise headings and dispatches the degree input's normal input event. It makes no requests or database changes. Selecting a direction only fills the form; **Save Stand** persists it. Run `node tests/js/stand-direction.test.mjs` for eight simulated interaction scenarios covering pointer/touch, cardinal and diagonal angles, pointer cancellation, wraparound, keyboard input, preserved/manual values, and editor map-arrow synchronization.

### Stand device location

`app/static/stand-location.js` requests a fresh, high-accuracy device location only after **Find My Location** is selected. It fills six-decimal coordinates without submitting the form and notifies the map editor to update the pin and center at zoom 17. Permission denial, unavailable location, timeouts, unsupported browsers, and invalid results leave existing coordinates intact and allow a retry. Coordinates can still be filled when the map library is unavailable.

Device geolocation needs browser/device location permission and a secure context. Local development on `localhost` or `127.0.0.1` is supported; accessing the app from a phone over a plain HTTP LAN address generally requires switching to HTTPS for device location. Map selection and manual coordinate entry remain available.

The request prefers high accuracy, accepts no previously cached position, and times out after 15 seconds. The accuracy shown comes from the device; the user reviews and saves the location. This does not change the property coordinates or the weather cache.

## Temporary wind preview — October 20, 2026

The property stand dashboard displays actual wind rounded to the nearest of 16 compass directions. In **Try a different wind**, choose a direction under **Wind coming from** to preview that wind. Grades, ranked rows, blue compass arrows, map pin colors, and popup grades update together. The actual-wind label remains visible, and the preview is marked with a highlighted panel and **Preview Grade** column.

Choose **Use actual wind** or refresh the page to restore actual weather. Preview state exists only in the current page: it is not sent to the server, written to browser storage, saved to the database, or inserted into the one-hour weather cache. Returning to the page through browser back/forward navigation also clears the preview. Refresh uses the normal weather lookup, including its existing cache. Previewing also works when actual weather is unavailable or the map library fails to load; JavaScript must be enabled.

`app/wind.py` supplies coming-from labels, and `app/static/wind.js` manages the page-only preview. It converts the selected source direction to a travel direction and matches the model's scoring and rounding. `maps.js` listens for preview updates to recolor pins and update popup grades.

Verification: the full Python suite passed **78 tests** on October 20, 2026. `tests/test_wind.py` covers source labels, compass boundaries, actual cached weather, and unavailable weather. Run `node tests/js/wind.test.mjs` for five simulated DOM/Leaflet interaction scenarios covering previews, sorting, map updates, halfway rounding, resets, page restoration, zero headings, and unavailable weather/library. These JavaScript checks do not replace rendered browser testing.

Stand coordinates are optional for compatibility with existing records and manual entry. Latitude and longitude must be provided together, within -90 to 90 and -180 to 180 respectively. Heading must be an integer from 0 to 360; north-facing 0 is valid. Invalid submissions show field errors and do not save changes.

## Database setup and upgrade

Stop the running server before initializing or upgrading a database:

```powershell
py init_db.py
py run.py
```

`init_db.py` creates tables for a new database. For an existing SQLite database, it adds the nullable `stands.latitude` and `stands.longitude` columns without replacing tables or deleting rows. Before upgrading a legacy database it saves a SQLite backup alongside the database, named `app.before-map-<timestamp>.db`. Re-running initialization is safe and preserves saved coordinates.

The active database is `instance/app.db`. Existing stands receive no invented coordinates; their positions are chosen by the user. Copies of the project with older databases must run initialization before using the new models.

## Implementation

- `app/models.py`: stand coordinate columns.
- `app/forms.py`: shared coordinate validation, integer stand heading, and CSRF-protected stand deletion.
- `app/maps.py`: map presentation data for the authorized property. Unlocated stands are omitted from the marker payload. User names are serialized through Jinja's `tojson` and inserted into popups as text.
- `app/routes.py`: map-click coordinate prefill, stand coordinate persistence, and existing ownership checks. A GET request with map coordinates only fills a form; it never creates a stand.
- `app/static/maps.js` and `maps.css`: Leaflet controls, imagery toggle, draggable editor pin, marker actions, and responsive layout.
- `app/schema.py` and `init_db.py`: additive schema upgrade and backup.

The map uses [Leaflet 1.9.4](https://leafletjs.com/reference-1.9.4.html), [Esri World Imagery](https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer), and [OpenStreetMap](https://operations.osmfoundation.org/policies/tiles/). Provider attribution remains visible. No account or API key is configured for these public tile endpoints. Leaflet loads from jsDelivr and imagery loads directly from the providers; the interactive map requires internet access. If the library or tiles fail, coordinate forms and stand management remain available. There is no offline tile download or prefetch feature.

## Verification

```powershell
py -B -m pytest tests/ -q -p no:cacheprovider
```

Automated checks cover map-click prefill, saved/moved/cleared coordinates, invalid and partial coordinates, heading limits, zero-valued coordinates, legacy/unlocated stands, unavailable weather, ownership restrictions, popup serialization, deletion CSRF, and repeatable legacy schema upgrades.

On October 12, 2026, the full suite passed **51 tests**. Separately, **23 JavaScript assertions** passed using simulated DOM/Leaflet events for pin selection, dragging, coordinate wrapping, heading preview, clearing, popup safety, map-to-form links, and failure handling. The public Leaflet and satellite service endpoints responded successfully.

Rendered browser testing could not be performed because no browser automation surface was connected. Desktop/mobile appearance and real pointer/touch interaction still require a browser check; these results do not establish completed UAT.
