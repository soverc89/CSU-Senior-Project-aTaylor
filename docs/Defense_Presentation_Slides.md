---
marp: true
theme: default
paginate: true
---

# Hunting Stand Weather Manager
**Senior Project Defense**
**Student**: Andrew Taylor
**Major**: Computer Science

---

# 1. The Problem
- Managing multiple hunting stands requires tracking wind directions.
- Whitetail deer have an acute sense of smell; wind blowing from the hunter to the game ruins the hunt.
- Checking weather apps and manually comparing them to stand facings is tedious and error-prone.

---

# 2. The Solution
- **Hunting Stand Weather Manager**: A web application that automates this process.
- **Key Feature**: Retrieves live National Weather Service data and mathematically grades stands (A-F) based on optimal wind direction.
- Allows hunters to make fast, data-driven decisions on where to hunt.

---

# 3. Technologies Used
- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **Testing**: Pytest (Unit, Integration, Regression)
- **External APIs**: U.S. National Weather Service (Weather.gov) API

---

# 4. Core Requirements
- **Functional**: Create/Edit/Delete Properties & Stands, API Integration, Grading Algorithm
- **Usability**: Color-coded, intuitive dashboard rankings
- **Performance**: One-to-Many cascading database relations, local weather data caching
- **Security**: Password hashing, strict data isolation by User ID

---

# 5. Application Walkthrough
*(Presenter: Show live demo or screenshots here)*
- Registration and Secure Login
- Dashboard (Ranked Stands)
- Creating a Property
- Creating a Stand (Degree facing)

---

# 6. Testing Strategy & Results
- **Unit Testing**: Validated grading logic and database models.
- **Integration Testing**: Mocked API responses to ensure graceful error handling and caching validation.
- **Regression Testing**: End-to-end user flows.
- **Results**: 17 Automated Tests, 100% Pass Rate.
- **User Acceptance Testing (UAT)**: Validated usability through simulated property setup and hunt planning scenarios.

---

# 7. Challenges Overcome
- **NWS API Navigation**: The free API required a complex 3-step query process (Coordinate -> Grid Point -> Station -> Observation).
- **Test Automation**: Intercepting network calls using `unittest.mock` to prevent tests from failing during API downtime.
- **Grading Math**: Normalizing the absolute angular difference between 0-360 degrees to a clean 0-100 percentile score.

---

# 8. Future Enhancements
- **Dark Mode**: Prevent screen glare during early morning pre-dawn hunts.
- **Long Range Planner**: Using historical weather trends to predict viability months in advance.
- **Shared Stand Groups**: Converting database to Many-to-Many relationships to allow hunting clubs to share access to stands.

---

# 9. Conclusion
- The application successfully meets the core requirements for managing and optimizing hunting stand selection based on real-time wind data.
- The project demonstrates full-stack development, API integration, and comprehensive test-driven development (TDD).

---

# Q & A
**Thank you for your time.**
*(Open the floor for questions from the faculty and guests)*
