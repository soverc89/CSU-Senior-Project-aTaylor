# Test Results Report

## Automated Testing Summary
**Date of Execution**: September 1, 2026  
**Framework Used**: `pytest` and `pytest-flask`  
**Total Tests Run**: 17  
**Pass Rate**: 100%

### Unit Tests
| Objective | Status | Notes |
| :--- | :--- | :--- |
| Grading Logic Perfect | PASS | Validated that a stand facing 0° with 180° wind returns 100% |
| Grading Logic Worst | PASS | Validated that a stand facing 0° with 0° wind returns 0% |
| Grading Logic Mid | PASS | Validated that a 45° offset returns 25% |
| User Creation | PASS | User securely created with hashed password |
| Property Creation | PASS | Validated correct data storage and relationship |
| Stand Creation | PASS | Validated correct data storage and relationship |
| User -> Property One-to-Many | PASS | Validated User can have multiple properties |
| Property -> Stand One-to-Many | PASS | Validated Property can have multiple stands |
| Cascading Delete | PASS | Validated deleting a user wipes properties and stands |
| User Login | PASS | Authentication via Flask-Login succeeds |
| User Isolation | PASS | User A cannot see User B's properties |
| Password Security | PASS | Plain text passwords are not stored in the database |

### Integration & Regression Tests
| Objective | Status | Notes |
| :--- | :--- | :--- |
| Weather API Connection Mocking | PASS | Validated parsing logic for points, stations, and observations |
| Weather API Error Handling | PASS | Gracefully returns `None` on timeout, preventing crash |
| Weather Data Caching | PASS | Validated that consecutive requests within duration use cache |
| Grader Refresh | PASS | Dashboard recalculates scores when page loads with mock data |
| End-to-End Registration Flow | PASS | Can successfully register, login, create property, create stand |

## Manual & User Acceptance Testing
*Status: Pending execution by users.*
