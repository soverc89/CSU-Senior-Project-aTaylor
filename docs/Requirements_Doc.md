Write Requirements Here.

1. Functional
2. Usability
3. Performance
4. Maintainability
5. Security



Requirment #
Requirement Type:
Description:
Rationale:
Fit Criterion:
Priority:
Dependencies: 


Functional
----------------

1.  Requirement Type: Functional
    -  Description: The user will be able to create, edit, and delete stands. Each stand will have a name, set of coordinates, and stand degree associated with it.
    -  Rationale: So that the user is able to have full control over their list of stands and their associated information.
    -  Fit Criterion: The user can successfully create a a new stand, edit an existing stands data, and delete a stand. Any additions or changes made will be reflected immediately in the user's stand list.
    -  Priority: Necessary
    -  Dependencies: Requirements 2-4

2. Requirement Type: Functional  
    -  Description: The User will be able to create stands.  
    -  Rationale: So that the user can add new stand locations to their list.  
    -  Fit Criterion: The user can successfully create a new stand in the system. Any additions made will be reflected immediately in the user's stand list.  
    -  Priority: Necessary  
    -  Dependencies: 

3. Requirement Type: Functional

    -  Description: The user will be able to edit stands.
    -  Rationale: So that the user can modify the information of their current stands.  
    -  Fit Criterion: The user can successfully edit an existing stand's information. Any changes made will be reflected immediately in the user's stand list.  
    -  Priority: Necessary  
    -  Dependencies: 

4. Requirement Type: Functional
    -  Description: The user will be able to delete stands.
    -  Rationale: So that the user can remove unwanted or unnecessary stands in their stand list.
    -  Fit Criterion: The user can successfully remove an existing stand from their list. Any removals made will be reflected immediately in the user's stand list. 
    -  Priority: Necessary
    -  Dependencies: 

5. Requirement Type: Functional
    -  Description: The user will be able to manually create stands by entering in relevant stand information into a form interface.
    -  Rationale: So that the user is able to create a new stand location through an easy to use form.
    -  Fit Criterion: The user can successfully create a stand by navigating to the stand creation form, entering in the releveant stand data, and clicking "Create Stand". The users stand list will be updated immediately
    -  Priority: Necessary
    -  Dependencies:

6. Requirement Type: Functional
    -  Description: Within the form interface, the user will have the option to fill the coordinate part of the form through a "Use my location" button.
    -  Rationale: If they are present at the stand, some users might find it more accessible to have coordinate data populated automatically using their devices geolocation. 
    -  Fit Criterion: Assuming the web app has proper permissions, the user will be able to click the "Use My Location" button on the Stand form and have the coordinate data form autofilled by requesting the devices                  geolocation in longitude/latitude format.
    -  Priority: Recommended
    -  Dependencies: 

7. Requirement Type: Functional
    -  Description: The User will be able to manage their stands through a map interface.
    -  Rationale: So that the user is able to create a new stand location through a map interface and form.
    -  Fit Criterion: The user will be able to click a map interface
    -  Priority: Necessary
    -  Dependencies: 

8. Requirement Type: Functional
    -  Description: The user will be able to manage and edit stands through a basic and easy to use UI.
    -  Rationale: So that the user can easily edit existing stands in their list.
    -  Fit Criterion: From the user's stand list page the will be able to click a "Manage Stands" button. Which will navigate them to a page where they can edit existing stands belonging to the user. Any changes made to a            stand will be immediately reflected in their stand list.
    -  Priority: Necessary
    -  Dependencies: 

9. Requirement Type: Functional
    -  Description: Within the stand editor UI, the user will be able to a stands coordinate data using a "Find my Location" button
    -  Rationale: If they are present at the stand, some users might find it more accessible to have coordinate data populated automatically using their device's geolocation. 
    -  Fit Criterion: The user can successfully populate the stand coordinate form entry by using the "Find my Location" button. Any changes made to a stands data will be be immediately reflected in the user's stand list.
    -  Priority: Recommended
    -  Dependencies: 

10. Requirement Type: Usability
    -  Description: The user's homepage/dashboard will display a user's stands in a ranked format with a grade and color associated with each stand.
    -  Rationale: Displaying a users stands in a graded and colored format makes it easy for the user to check their stands at a glance.
    -  Fit Criterion: When viewing the user's dashboard the display for for stands will correctly rank them by grade and color them appropriatly based on their given grade.
    -  Priority: Necessary
    -  Dependencies: 

11. Requirement Type: Functional
    -  Description: The System uses OpenWeatherMap/Weather.gov API to request windage data local to the user.
    -  Rationale: For the system to display accurate and timely data for the user, it needs to pull updated data for a user's location.
    -  Fit Criterion: The system can succesfully request accurate data from the API for a users location. If it cannot it will display a relevant error message.
    -  Priority: Necessary
    -  Dependencies: 

12. Requirement Type: Functional
    -  Description: The system generates a stand grade by comparing a stand's degree with the most recent wind data.
    -  Rationale: A grading system for stands is an intuitive way for the user to know which stands are advantagous.
    -  Fit Criterion: The system can correctly manipulate weather data so that it displays an accurate grade for a stand. Passes tests?
    -  Priority: Necessary
    -  Dependencies:

13. Requirement Type: Functional
    -  Description: The dashboard will allow the user to select a future data and time for up to 7 days in advance to view projected stand grades. When a future time is selected, the system will recalculate stand rankings            based on the weather forecast for that specific timestamp.
    -  Rationale: This functionality gives users the ability to plan hunting trips ahead of time.
    -  Fit Criterion: (A) The user changes the dashboard time to Wednesday at 7:00 AM. (B) The system updates the dashboard to show stand grades based on Wednesday mornings' wind forecast and not the current one. (C) The             user is prevented from selecting a date outside of a week.
    -  Priority: Recommended
    -  Dependencies: 

14. Requirement Type: Functional
    -  Description: The system will provide a "Long Range Planner" that allows users to estimate stand advantages months in advance. This feature will rank stands based on aggregated historical weather data for a selected            date range rather than a live forecast.  
    -  Rationale: Major hunting opportunities such as the rutting season for whitetail deer often require planning farther ahead than just a week. Since accurate forecasts do not exist months ahead of time, the system would          need to rely on historical trends to provide the user with a probability of a stand being advantageous 
    -  Fit Criterion: (A) A user selects a date range 3 months in the future. (B) The system retrieves historical wind data for those specific days from previous years. (C) The system displays the stands ranked by their              historical advantageousness probability.
    -  Priority: Optional / Future Capability
    -  Dependencies: 

15. Requirement Type: Functional
    -  Description: If I do 19, the system will need to manipulate past weather data in a meaningful way.
    -  Rationale:
    -  Fit Criterion:
    -  Priority:
    -  Dependencies:


**Look and Feel**

16. Requirement Type: Look and Feel?
    -  Description: I may or may not include a calendar function
    -  Rationale:
    -  Fit Criterion:
    -  Priority:
    -  Dependencies: 

17. Requirement Type: Look and Feel
    -  Description: I may or may not include a solar calendar
    -  Rationale:
    -  Fit Criterion:
    -  Priority:
    -  Dependencies: 

18. Requirement Type: Look and Feel
    -  Description: I may or may not include a lunar calendar
    -  Rationale:
    -  Fit Criterion:
    -  Priority:
    -  Dependencies: 

**Usability**

19. Requirement Type:
    -  Description: 
    -  Rationale:
    -  Fit Criterion:
    -  Priority:
    -  Dependencies: 

**Performance**

20. Requirement Type: Performance
    -  Description: If needed, relevant weather information will be updated every 6-12 hours.
    -  Rationale: Typically, Weather API Providers update their weather data every 6-12 hours. If there is a present need in the system to update weather data for a location, its weather data will be updated automatically            without prompting by the user.
    -  Fit Criterion: The system can successfully make an API call for updated weather data. If unsuccessful, the system will provide a relevant error message.
    -  Priority: Necessary
    -  Dependencies: 

21. Requirement Type: Performance
    -  Description: Data of some sort will have to be saved for the users.
    -  Rationale:
    -  Fit Criterion:
    -  Priority:
    -  Dependencies: 

22. Requirement Type: Performance
    -  Description: I will store weather data of some sort. Some long-term, some short term.
    -  Rationale:
    -  Fit Criterion:
    -  Priority:
    -  Dependencies: 

23. Requirement Type:
    -  Description: Two options (1/2) The system keeps track of weather locations and updates those at a set interval and that is what the user pulls from. Or, the weather for an area only updates once a user needs it
       then that information is cached for other users.
    -  Rationale:
    -  Fit Criterion:
    -  Priority:
    -  Dependencies: 

24. Requirement Type: Constraint ??
    -  Description: The project will be limited to being a web application.
    -  Rationale:
    -  Fit Criterion:
    -  Priority:
    -  Dependencies: 

**Security**

25. Requirement Type: Security
    -  Description: The system will store all user passwords using a secure hashing algorithm.
    -  Rationale: To protect user credentials from a data breach or an unauthorized database access
    -  Fit Criterion: Inspecting the datbase of user information will verify that the password field contains hashed strings rather than the user's actual password.
    -  Priority: Necessary
    -  Dependencies: 

26. Requirement Type: Security
    -  Description: The system will require users to authenticate via a login page using a valid username/email and password before accessing the dashboard or stand management features.
    -  Rationale: To prevent unauthorized users from acceessing the application and user data
    -  Fit Criterion: A user entering valid credentials is redirected to their account and dashboard. A user entering invalid credentials recieves an error message and remains on the login page.
    -  Priority: Necessary
    -  Dependencies: 

27. Requirement Type: Security
    -  Description: The System will restrict data access so that a logged in user can only view, edit, or delete stands associated with their specific User ID.
    -  Rationale: To ensure user privacy and data integrity, and prevent users from modifying or viewing other users' data.
    -  Fit Criterion: If a user attempts to access the data of another user, the system denies access.
    -  Priority: Necessary.
    -  Dependencies: 




 












