# User Acceptance Testing (UAT) Plan & Scripts

## Overview
The goal of this User Acceptance Testing is to ensure that the "Hunting Stand Weather Manager" application is intuitive and easy to use. The testing consists of two simulated scenarios for participants to complete, followed by a brief questionnaire.

## Scenario 1: Property Setup
**Objective**: Verify the ease of creating a property, using the map (or data entry) logic, and placing a stand.

**Instructions for Participant**:
> "You are scouting a new piece of land to hunt on. Please log into the application, create a new Property/Stand Group for this land, and place a new hunting stand at a location you have identified."

**Success Criteria**:
- Participant successfully navigates to the "New Property" page.
- Participant successfully creates the property.
- Participant navigates to the property and successfully creates a new Stand, assigning it a degree facing.

## Scenario 2: Hunt Planning
**Objective**: Verify the utility of the Dashboard and Grader logic.

**Instructions for Participant**:
> "You are preparing for a hunt. Use the dashboard for the property you just created to determine the highest-ranking stand based on current wind conditions."

**Success Criteria**:
- Participant can easily identify which stand is best.
- Participant understands what the grade/percentage means.

## Post-Test Questionnaire
*To be filled out by the participant after completing both scenarios.*

1. On a scale of 1-5, how easy was it to create a stand using the map interface? (1 = Very Difficult, 5 = Very Easy)
2. Does the Dashboard communicate immediately which stand is best to hunt? (Yes/No, please explain)
3. Were there any features that felt unnecessary?
4. What is one feature or tool you wish was included?

## Recorded Questionnaire Findings

Map-based stand creation received a 5/5 ease-of-use rating. Feedback indicated that the dashboard immediately communicated which stand was best to hunt, and no features were identified as unnecessary. Requested additions included precipitation probability, advance stand planning, stand photos, camera integration, and property-boundary mapping.

The findings support perceived usability of the core workflows. See [Test Results](Test_Results.md#user-questionnaire-results) for the questionnaire summary and proposed future enhancements.

---
*Presenter note: The questionnaire summary is recorded in the Test Results report and reflected in the Defense Documentation and presentation outline. Keep reported usability findings distinct from functional test results.*
