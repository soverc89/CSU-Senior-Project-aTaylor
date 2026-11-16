# Project Handoff: Hunting Stand Weather Manager

**Project**: Hunting Stand Weather Manager (CSU Senior Project)  
**Author**: Andrew Taylor  
**Repository**: [CSU-Senior-Project-aTaylor](https://github.com/soverc89/CSU-Senior-Project-aTaylor)  
**Last Updated**: October 2026  

**October 12 update**: Map placement and management are now implemented. See [MAP_FEATURE.md](MAP_FEATURE.md) for usage, database upgrade instructions, and verification details. Property geolocation supplies shared weather for all stands; stand coordinates only place map pins. The active weather module now converts NWS source headings into the direction wind travels toward.

**October 20 update**: Property stand dashboards now label actual wind by its coming-from compass direction and offer a temporary 16-direction wind preview. Previews update grades, rankings, compass arrows, map colors, and popup grades without persisting or changing the weather cache. Refresh or **Use actual wind** restores actual conditions. The Python suite passed 78 tests; five simulated JavaScript interaction scenarios passed. See [MAP_FEATURE.md](MAP_FEATURE.md#temporary-wind-preview--october-20-2026) for details. Rendered browser verification remains pending.

**October 20 field placement update**: Stand creation and editing now include **Find My Location**, filling device coordinates and centering the map pin for review before saving. Device location does not change the property's weather coordinates. See [MAP_FEATURE.md](MAP_FEATURE.md#stand-device-location) for permission, HTTPS, accuracy, and error behavior.

**October 20 direction control update**: Stand creation/editing now includes a draggable circular direction control with mouse, touch, and keyboard support. It synchronizes the degree input and map-facing arrow, preserves saved headings, and leaves new headings unset until selected. Eight simulated interaction scenarios passed; rendered pointer/touch verification remains pending. See [MAP_FEATURE.md](MAP_FEATURE.md#stand-direction-control).

---

## 1. System Architecture

The Hunting Stand Weather Manager is built as a modular, lightweight Python web application utilizing the **Flask Application Factory** pattern, coupled with relational data modeling, external weather API integration, and server-rendered templates.

### High-Level Architecture Diagram

```
+-----------------------------------------------------------------------+
|                             Client Browser                            |
|             (Pure.css Responsive UI, HTML5 Geolocation, CSS Compass)  |
+-----------------------------------+-----------------------------------+
                                    | HTTP / HTTPS
                                    v
+-----------------------------------------------------------------------+
|                          Flask Application                            |
|  - App Factory (app/__init__.py)                                      |
|  - Authentication & Session Guard (Flask-Login)                       |
|  - Blueprints & Controller Logic (app/routes.py)                       |
|  - Form Processing & Validation (WTForms / Flask-WTF)                 |
+-------------------+-------------------------------+-------------------+
                    |                               |
                    v                               v
+-----------------------------+   +-------------------------------------+
|      Database Layer         |   |          Weather Subsystem          |
|  - SQLite (instance/app.db) |   |  - WeatherManager (app/weather.py)  |
|  - SQLAlchemy ORM           |   |  - 1-Hour In-Memory Cache           |
|  - Cascading Relationships  |   |  - National Weather Service API     |
+-----------------------------+   +-------------------------------------+
```

### Core Architecture Components

1. **Application Core & Factory (`app/__init__.py`)**:
   - Implements `create_app(test_config=None)` to facilitate testing with isolated configurations (e.g., in-memory SQLite databases during test execution).
   - Initializes extensions: `SQLAlchemy`, `LoginManager`.
   - Registers route blueprints and user loader callback.

2. **Data Model Layer (`app/models.py`)**:
   - Built on SQLAlchemy ORM targeting SQLite (`sqlite:///app.db`).
   - **`User`**: Manages credentials with Werkzeug secure password hashing (`generate_password_hash`, `check_password_hash`), inherits from `UserMixin`.
   - **`Property`**: Represents a hunting land/parcel. Stores GPS coordinates (`latitude`, `longitude`) and foreign key to `User`. Enforces cascading deletion of child stands.
   - **`Stand`**: Represents an individual hunting blind/stand. Stores facing direction (`degree`, 0–360°), optional map coordinates, and foreign key to `Property`. Weather continues to use property coordinates.
   - **Grading Algorithm**: `Stand.current_score(wind_degree)` computes the shortest angular difference on a circular 360° scale:
     $$\text{difference} = 180 - | | \text{wind\_degree} - \text{stand.degree} | - 180 |$$
     $$\text{score} = \left( \frac{\text{difference}}{180} \right) \times 100$$
     - `100%`: Wind travels opposite the stand facing, carrying scent behind the hunter.
     - `0%`: Wind travels along the stand facing, carrying scent in front of the hunter.

3. **Weather Subsystem (`app/weather.py`)**:
   - `WeatherManager` interfaces with the free **U.S. National Weather Service (NWS) API** (`api.weather.gov`).
   - Uses a three-step query workflow:
     1. `GET /points/{lat},{lng}` $\rightarrow$ retrieves grid and observation station endpoint.
     2. `GET /stations` $\rightarrow$ identifies the nearest active weather station.
     3. `GET /stations/{id}/observations/latest` $\rightarrow$ parses current `windDirection.value`.
   - **Caching Layer**: In-memory dictionary `_WEATHER_CACHE` keyed by `(lat, lng)` with a 3600-second (1-hour) TTL to prevent API rate limits.
   - **Fault Tolerance**: Catches network, timeout, and parsing exceptions, returning `None` gracefully instead of throwing unhandled 500 errors.

4. **Routing & Controllers (`app/routes.py`)**:
   - Blueprint `main` handles authentication (`/register`, `/login`, `/logout`), account self-deletion (`/profile/delete`), property CRUD, and stand CRUD.
   - Strict authorization checks ensure users can only view, edit, or delete entities they own (aborting with HTTP `403 Forbidden` on unauthorized access).

5. **Presentation & UI (`app/templates/`, Pure.css)**:
   - Built with Jinja2 templating extending `base.html`.
   - Styled using **Pure.css** for a minimalist, responsive layout.
   - Custom dynamic CSS compass: Rotates stand facing arrow (black) and live wind vector arrow (blue) based on computed degrees.
   - Color-coded visual badges: Green ($\ge 80\%$), Yellow ($50\% - 79\%$), Red ($< 50\%$), and Gray (Unavailable).

---

## 2. Completed Features

| Category | Feature | Description | Status |
| :--- | :--- | :--- | :---: |
| **Authentication & Security** | User Registration & Login | Secure signup and login with hashed passwords via Werkzeug and Flask-Login session tracking. | Completed |
| | Data Isolation | Multi-tenant isolation ensuring users cannot view or manipulate other users' properties or stands. | Completed |
| | Account & Data Erasure | Privacy-compliant account deletion that cascades and cleans up all user properties and stands. | Completed |
| **Property Management** | Property CRUD | Create, read, update, and delete hunting properties. | Completed |
| | Geolocation Integration | Optional latitude/longitude coordinates with browser HTML5 Geolocation API auto-detection. | Completed |
| **Stand Management** | Stand CRUD | Create, view, edit, and delete hunting stands within designated properties. | Completed |
| | Facing Heading (0–360°) | Configurable directional orientation for each hunting stand. | Completed |
| | Cascading Delete | Deleting a property automatically deletes all associated stands. | Completed |
| | Interactive Map Stand Placement | Satellite/street map, click-to-place stand forms, draggable editor pins, and saved-pin management (`Requirements_Doc.md` Req 6). | Completed |
| **Weather & Analytics** | NWS API Integration | Real-time wind heading retrieval based on property coordinates. | Completed |
| | Weather Data Caching | 1-hour in-memory cache to reduce network overhead and prevent NWS rate limiting. | Completed |
| | Automated Scoring | Dynamic calculation converting wind angle difference to a 0–100% usability grade. | Completed |
| | Intelligent Stand Ranking | Stands on property dashboard are automatically sorted from most favorable to least favorable. | Completed |
| **Visual UI Components** | Interactive CSS Compass | Dual-needle visual compass indicating stand orientation vs. wind direction on stand cards. | Completed |
| | Color-Coded Badges | Immediate visual indication of stand favorability (Green / Yellow / Red). | Completed |
| **Quality Assurance** | Automated Test Suite | 51 passing tests including map persistence, validation, ownership, CSRF, and legacy schema upgrades. Browser UAT remains pending. | Automated checks passed |

---

## 3. Known Bugs, Technical Debt & Limitations

1. **Map Imagery Availability**:
   - Satellite imagery and street tiles are supplied by external services. Their availability and imagery resolution vary by location.
   - If tiles or the map library cannot load, forms remain available for coordinate entry. Existing stands without coordinates stay in the ranked list until the user places them.
   - Desktop/mobile visual checks and real map interaction still need browser verification; automated checks and simulated JavaScript events passed.
2. **Pytest Root Discovery (`src/database_test.py`)**:
   - *Issue*: Running bare `pytest` in the root directory causes an error because `pytest` attempts to collect legacy prototype script `src/database_test.py` (which expects an unconfigured SQLite table).
   - *Workaround*: Execute tests targeting the `tests/` directory explicitly:
     ```powershell
     py -m pytest tests/
     ```
   - *Recommended Fix*: Add a `pytest.ini` or `pyproject.toml` file setting `testpaths = ["tests"]`.

3. **SQLAlchemy 2.0 `Query.get()` Deprecation Warning**:
   - *Issue*: `User.query.get(...)` and `Property.query.get_or_404(...)` trigger `LegacyAPIWarning` in SQLAlchemy 2.0+ during test runs.
   - *Impact*: Non-breaking warning in current versions, but will become incompatible in future major SQLAlchemy releases.
   - *Recommended Fix*: Transition to `db.session.get(User, user_id)` and modern select syntax.

4. **In-Memory Cache Volatility & Multi-Process Concurrency**:
   - *Issue*: `_WEATHER_CACHE` in `app/weather.py` is stored in a process-level Python dictionary.
   - *Impact*: Cache resets every time the application restarts. In multi-worker production servers (such as Gunicorn or uWSGI), workers maintain separate, unsynchronized caches.
   - *Recommended Fix*: For multi-worker production deployment, migrate to an SQLite-backed cache table.

4. **NWS API Calm Wind Conditions**:
   - *Edge Case*: When wind is completely calm, NWS observation stations report `windDirection.value = None`. The application handles this safely by falling back to "Unavailable", but a future enhancement could explicitly label this as "Calm Wind (Variable)".

6. **Resolved: Stand and Coordinate Form Validation**:
   - Stand facing is now an IntegerField with server-side range checks from 0 to 360, including 0.
   - Property and stand coordinates use finite numeric fields, latitude/longitude bounds, and paired-entry validation. Invalid submissions display field errors and do not save.
---

## 4. Remaining Tasks & Future Roadmap

### High Priority & Remaining Core Requirements
- [x] **Interactive Map Interface for Stand Creation (`Requirements_Doc.md` Req 6)**:
  - Satellite imagery with a street-map toggle on the dashboard and stand form.
  - Click-to-place forms, draggable editor pins, and saved markers with grade, edit, and delete actions.
  - Nullable stand coordinates and a preserving SQLite schema upgrade. See [Map Feature](MAP_FEATURE.md).
- [ ] **Configure Pytest Config File**: Add `pytest.ini` at repository root:
  ```ini
  [pytest]
  testpaths = tests
  ```



### Future Feature Enhancements (Post-MVP)
1. **Dark Mode / Night Vision Theme**:
   - High-contrast red/dark theme to preserve night vision during early morning preparation.
2. **Hourly & Multi-Day Forecast Planner**:
   - Integrate NWS hourly forecast endpoints (`/gridpoints/{office}/{gridX},{gridY}/forecast/hourly`) allowing hunters to plan afternoon and next-day hunts rather than only viewing current conditions.
3. **Solar/Lunar & Solunar Activity Cycles**:
   - Incorporate sunrise, sunset, dawn/dusk twilight times, and lunar phase tables to correlate wind favorability with peak deer movement hours.
4. **Hunting Club Stand Sharing (Many-to-Many Relationships)**:
   - Extend the `Property` model to support membership tables, enabling clubs to grant multiple user accounts shared access to viewing stand ratings.

---

## 5. Development & Running Guide

### Running Locally
```powershell
# 1. Initialize Database (first-time setup)
py init_db.py

# 2. Run the Development Server
py run.py
# Server runs at http://127.0.0.1:5000
```

### Running Test Suite
```powershell
# Run all automated tests
py -m pytest tests/ -v
```
