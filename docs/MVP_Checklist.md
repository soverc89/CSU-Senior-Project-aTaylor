# Hunting Stand Project - MVP Checklist

Based on the project proposal, the requirements document, and the current state of the source code (which contains basic Python models and weather fetching logic), the following is a sequenced checklist of tasks required to build the Minimum Viable Product (MVP) web application.

## Phase 1: Environment & Project Setup
The current codebase has Python scripts but lacks a formal web application structure.
- [x] Initialize formal Flask project structure (e.g., `app/`, `templates/`, `static/`, `routes/`).
- [x] Set up the Flask application factory or main app initialization in an `app.py` or `__init__.py`.

## Phase 2: Database Integration
The `models.py` file has a basic schema but needs to be formally integrated with Flask.
- [x] Integrate Flask-SQLAlchemy for database connection management.
- [x] Refine `models.py` to ensure `User`, `Property` (Stand Group), and `Stand` models have the correct relationships and cascading deletes.
- [x] Implement secure password hashing for the `User` model (e.g., using `Werkzeug` security helpers).
- [x] Create database initialization scripts to easily build or reset the `hunting.db`.

## Phase 3: User Authentication (Security & Privacy)
- [x] Implement user registration logic and UI form.
- [x] Implement user login and logout logic.
- [x] Protect routes using Flask-Login to ensure only authenticated users can access the dashboard.
- [x] Add session management so users can only view, edit, or delete their own properties and stands.

## Phase 4: Frontend Foundations & UI
- [x] Create a base HTML template (`base.html`) that includes a navigation bar and sets up the chosen CSS framework (Pure.css / Bootstrap).
- [x] Create basic template structures for the Dashboard, Login/Register pages, and Stand Management.

## Phase 5: Core Application Logic (Stand Management CRUD)
- [x] **Properties / Stand Groups:**
  - [x] Create routes & UI to Add, View, Edit, and Delete Properties.
- [x] **Stands:**
  - [x] Create routes & UI to Add, View, Edit, and Delete Stands within a specific Property.
  - [x] Build the "Create Stand" form, including fields for Name, Degree (facing direction), and optional coordinates.
  - [x] Incorporate browser Geolocation API for the "Find My Location" button on the stand creation form to autofill coordinates.

## Phase 6: Weather Integration & Stand Grader
The current `Weather_Manager` is hardcoded to a specific weather station. This needs to be dynamic.
- [x] Integrate the weather API (weather.gov) into the backend so it dynamically fetches wind data based on a Property's latitude and longitude.
- [x] Adapt the `Stand_Evaluation.py` math logic to calculate a "Grade" for each stand based on the live wind data vs the stand's specific degree heading.
- [x] Update the Stands dashboard to display this Grade.
- [x] Implement simple caching (e.g., dictionary or database) to store recent weather data for a location and avoid API rate limits (updates 6-12 hrs).
- [x] Ensure the grading math in `Stand_Evaluation.py` works robustly with the new dynamic weather data.

## Phase 7: The Dashboard (Property-Level)
Per user request, the dashboard is at the property level to avoid excessive API calls. The property's Stands view operates as this dashboard.
- [x] Run the evaluator algorithm against the current weather data.
- [x] Apply color-coding (Green for good, Red for bad) to the stand list based on the calculated grade.
- [x] Sort the stands on the property dashboard so that the highest graded stands appear first.
- [x] (Optional MVP Polish) Add a visual compass icon indicating stand direction vs. wind direction on each stand's dashboard card.

## Phase 8: Testing, Verification & Cleanup
- [ ] Conduct manual testing of the user flow: Register -> Add Property -> Add Stand -> View Dashboard Grade.
- [ ] Verify that permissions prevent users from accessing each other's data via URL spoofing.
- [ ] Ensure API error handling is robust (e.g., what happens if the weather API is down? display a relevant error).
- [x] **Account Management (Privacy):** Implement a way for users to delete their account and associated data.
- [x] **Frontend Input Validation constraints:** Ensure degree fields in the Stand Form only accept values 0-360.
- [ ] Prepare final MVP presentation and commit code.
