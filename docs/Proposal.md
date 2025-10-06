Hunting Stand Project
===================================================

**Student Name(s)**: Andrew Taylor (put your name here, followed by two spaces)  
**Degree and Major**: B.A. Applied Computing Cybersecurity (put your name here, followed by two spaces)  
**Project Advisor Name**: Dr. Hayes (put your name here, followed by two spaces)  
**Expected Graduation Date**: Spring 2027 (put the correct month and day here)


Problem Statement
-----------------

When planning a hunting trip, success is never guaranteed. Hunters face the uncertainty of whether they
will even see an animal, much less harvest one. The challenge lies in the unpredictable nature of wildlife,
making it dificult to ensure a sucessful hunt. Although no hunting strategy can guarantee results, hunters can 
increase their chances of encountering game by carefully selecting ideal weather conditions.


Project Description
-------------------

This project will collect and analyze weather data, primarily wind data, to 
determine the best times and locations to hunt in a given area set by the user.


Proposed Implementation Language(s) 
-----------------------------------

Python, HTML, CSS, Javascript, SQLite


Libraries, Packages, Development Kits, etc., to be used in the proposed implementation language(s)
--------------------------------------------------------------------------------------------------

Flask, MapBox JS, Requests, Pure.css, Bootstrap, Node.JS


Additional Software/Equipment Needed
------------------------------------

Equipment:
  Personal Laptop for Development, Personal Phone/Laptop for Testing, Personal Laptop/Raspberry PI to Host Web Server

Software: 
  Visual Studio Code for Project Coding

Alternative Solutions and Rationale 🔍
--------------------------------------

> **Purpose**: Describe at least two alternative solutions or approaches to your project. Compare these with your chosen solution based on relevant criteria (e.g., feasibility, scalability, cost, performance, usability). Explain why you selected your final approach.

### Alternative 1
  Physical Weather Station
- **Description**:  
  This alternative would use a pre-built or custom-built weather station in order to collect real-time weather data instead of relying on weather data APIs.
  
- **Pros**:  
  - _(List strengths or advantages)_
  - Very accurate local weather readings
  - Less reliant on APIs
  - Cool Factor
- **Cons**:  
  - _(List weaknesses or limitations)_
  - Weather readings are only accurate within a certain radius of the station.
  - Scalibility is limited by needing physical weather stations at each location.
  - Maintenance / Troubleshooting of the weather station hardware.
  - Weather stations at geographically remote hunting locations are less feasible
  - Communicating with a station is limited to LoRaWAN and or Satelite data transfer, effecting performance and cost.
### Alternative 2
  Meteor Tech Stack
- **Description**:
  This alternative proposes using the Meteor framework, a all in one JavaScript stack, to build the web application instead of a Python based stack.
  
- **Pros**:  
  - _(List strengths or advantages)_
  - Frontend, Backend, and database are integrated together
  - Asynchronous Data/Live updates are built in.
- **Cons**:  
  - _(List weaknesses or limitations)_
  - Spotty development could lead to future issues with scalabiliity
  - Meteor has a small userbase, less online guides and documentation
  - Less flexible, forced to use the conventions of the Meteor framework

### Chosen Solution and Rationale
- **Chosen Solution**:  
  _(Restate your selected solution.)_
  My chosen solution for solving the problem statement is to use a standard Python stack that takes advantage of the many powerful weather API's already available.
- **Rationale**:  
  _(Justify your choice in comparison with the alternatives. Highlight key reasons for its selection.)_

|          | Physical Weather Station | Meteor Stack | Standard Python Stack using Weather APIs |
|----------|--------------------------|--------------|------------------------------------------|
| Feasibility | A physical weather station is not feasible given the scope of this project. Doing meaningful testing with a physical station would require many trips out to distant locations. Not to mention maintanance, troubleshooting, and debugging the physical hardware while it is physically several hours away| A Meteor stack is a fairly feasible option for this project, especially with it's built in live updates. However due to the spotty development, small userbase, and limited documentation, going with this option introduces a steap learning curve that decreases it's feasibility.| A standard Python stack offers many lightweight libraries and tools that make this project very feasible. Additionally, there are many free to use weather data APIs that offer all the information needed for the scale of this project.
| Cost | The cost of a durable and accurate pre-built or custom-built weather station can cost hundreds of dollars each. Access to a 3D printer can bring the price down, but at that point it starts to move beyond the scope of this project.| The only extra cost this alternative poses is the amount of additional time and effort it could take to learn.| Since a python stack is more flexible in terms of how modular it is, it will take some time to learn all of the different libraries and tools I will need, making it more time costly. However, the weather API's are completely free, unlike a physical weather station. |
| Scalability | Scalability is the biggest weakness of going with a physical weather station. A phyiscal station only provides accurate weather data for the specific area around the station, decreasing in quality the farther you move away. For that reason, each additional hunting location would require another weather station, and weather information about that location could not be gathered until the station is set up. | Due to the inconsistant development of Meteor, scaling the project larger as time goes on could be limited by the slow development time. | A standard Python stack that uses weather data APIs provides the most scalability in comparison to the other alternatives. Due to how modular and flexible it is, parts of the application such as the database can be swapped out for more robust options. Projects built with all-in-one options like Meteor have to be rebuilt from the ground up if it stops being supported, not so with modular python stack. Going with a Weather API, increased scale just means more API calls which is far easier to scale then providing more physical weather stations. |
| Performance | Performance is where a physical weather station shines. Once set up and running a physical weather station would provide the most accurate and up to date weather data for a given area. | Using Meteor comes with Live Web Updates and asynchronous data, probably its biggest strength| The standard python stack suffers from a lack of built in web application support for live updates. However this can be remedied by additional libraries such as SocketIO. Weather API's provide fairly accurate weather data in a timely manner that is suitalbe for this project. The incredibly precise data that a weather station would provide is not needed for a project like this. |
| Usability | A physical weather station adds a great deal of extra testing and set up. It also adds another major point of failure into the system, where if a component in the physical station fails, the entire application will fail, rendering it useless to the user. | From my research, Meteor is not the most intuitive framework to learn. In addition, it is limited in terms of guides and documentation.| I am already familiar with Python and a lot of the libraries included with it, which makes starting a project like this much easier than learning a new framework like Meteor. Weather API's typically come with documentation and tools on how to obtain and parse specific data which make them very easy to incoroporate into this project.|

  

> 💡 *Tip: Consider using a comparison table to evaluate trade-offs across multiple criteria such as feasibility, performance, scalability, cost, and usability.*


Personal Motivation
-------------------

I deer hunt during the spring/winter and there is always a lot of planning that
goes into each aspect of a hunt. Planning a successful hunt relies on having 
a variety of up to date and accurate information. 

Outline of Future Research Efforts
----------------------------------

(What do you need to learn or figure out to complete this project? What tasks are you going to do the do?)

Frontend
 - 

Web Hosting

Maps and JavaScript Integration

Weather APIl

Schedule 📅
-----------

> Update the dates and add your tasks by replacing the examples. Remove this note.

*   Fall 2025 - CSCI 497
    -   October 1 - Meet with Dr. Hayes and finish final proposal details. 
    -   October 6 - Submit Proposal draft 
    -   October 27 - Have general list of project requirements
    -   November 10 - Work on Requirements Document
    -   November 25 - Turn in completed Proposal and Requirements Document
    -   December 8 - Make final corrections and changes

*   Spring 2026 - CSCI 498
    -   Week 1-4 - Begin core development: set up basic application structure, web framework, and database
    -   Week 5-6 - Start building out core features of the product
    -   Week 7 - Draft Test Plan
    -   Week 8-9 - Run initial tests and debug
    -   Week 10-11 - Continue to iron out core features 
    -   Week 12-13 - Work on Minimal Viable Product
    -   Week 14 - Complete Minimal Viable Product
 
*   Summer 2026 - Independent/Optional Project Work
    -   June 1 - Work on Viable Product to make it less Minimal

*   Fall 2026 - CSCI 499 (more details will be added here once you are closer)
    -   Weeks 1-4 - Implement test plan
    -   Week 5 - Elvaluate test results
    -   Week 6-10 - Apply updates and bug fixes based on the results
    -   Week 8 - Complete the first 4 chapters of the defense documentation.
    -   Week 9-12 - Finish Defense Documentation 
    -   Week 13 - Work on and Practice Project Presentation, make final adjustments to project and documentation
    -   Week 14 - Project Presentation


References 📚
-------------

> List any references you cited in this proposal.
