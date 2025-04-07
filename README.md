# GreenCampus

<img width="1062" alt="image" src="https://github.com/user-attachments/assets/f7bbd2db-f173-446a-9723-d47d64429664" />


## Assignment 2 Requirements: 
* **THREE** core features.
  * Building Energy Monitoring (FR2), Community Engagement (FR5, FR6)
* **ONE** design pattern.
  * Singleton
* **TWO** class relationships (Association, Inheritance, etc.).  
* **ONE positive** & **ONE negative** test case per feature.  
* Use Git for version control (mandatory, log needed).  
* Simulate external systems (mocking/hard-coding).  

<details>
<summary><h2>  FAQ</h2></summary>

Originally posted by Wendy on [TEAMS](https://teams.microsoft.com/l/message/19:c7e55754082d45c794c3479aa0668614@thread.tacv2/1743249969522?tenantId=b024cacf-dede-4241-a15c-3c97d553e9f3&groupId=57e159d8-1648-4d26-a608-848d07a94a88&parentMessageId=1743249969522&teamName=BUS%202024%20Support%20Students%20-%20Teaching&channelName=Assignment%20-Part2%20Queries&createdTime=1743249969522)

![image](https://github.com/user-attachments/assets/6e9a73c8-d74b-4f35-afeb-699b51a7c623)

1.  **Do I have to implement the entire system described in Assignment 1?**
    No. You only need to implement a working prototype of the most critical three features of your design to demonstrate feasibility.

2.  **What are considered “critical features”?**
    These are the core functionalities your system can't work without, those that form the backbone of your application and were emphasised in your design.

3.  **Can I change my original design from Assignment 1?**
    Minor refinements are acceptable, especially if they improve feasibility, but the core design should still reflect your original proposal.

4.  **Can I use a language other than Python?**
    Yes, but you must ensure that you are knowledgeable in the language since the support provided will be available only for Python.  Moreover, you need to clearly document it in your submission what language you choose.

5.  **Am I required to build a user interface?**
    Not necessarily. A command-line interface (CLI) or minimal UI is acceptable as long as it clearly demonstrates functionality.

6.  **What kind of design pattern should I use?**
    You can use any of the taught in the lecture or any other that you feel is suitable for your work.

7.  **What kinds of class relationships are required?**
    At least two of the following: inheritance, association, aggregation or composition.

8.  **What do positive and negative test cases mean?**
    For each feature:
    A positive test shows the system behaves as expected with valid input. A negative test demonstrates how the system handles invalid input or error conditions.
    Use pytest code to run the test and include it in the code.

9.  **Can I simulate APIs or database interactions?**
    Yes, you can hardcode values to simulate your database, mock functions or classes or use random/user-generated data.

10. **Do I have to use Git?**
    Yes. Git is required to demonstrate version control practices.
    https://canvas.bham.ac.uk/courses/78939/pages/building-useable-software?module_item_id=4088755

11. **What should the Git log show?**
    The Git log should show clean commit history, contribution breakdown (every group member contribution) and meaningful commit messages.

12. How should I include the Git log in my submission?
    Export your Git log to a text file (git log > gitlog.txt) and include it with your submission.

13. What files should I submit?
    Your submission should include:
    - Source code for the prototype.
    - README file that includes:
      1) A brief description of the system and its purpose (max 200 words);
      2) step-by-step instructions on how to run the project;
      3) list of programming languages, frameworks, or tools used;
      4) a summary of implemented functionalities; and
      5) describe the contribution percentage to the project and describe the specific work done. Make sure to add test cases for each feature (positive + negative) and
      6) Git log file.
    - Video

14. When is the deadline for this submission?
    May 8th 2025, 17:00 UK time on Canvas.

More information about the submission in the following link.
https://canvas.bham.ac.uk/courses/78939/assignments/512861

</details>

## Dependencies:
- Frontend: Bootstrap + Charts.js/ Plotly
- Backend: Python + Flask
- Database: SQL + SQLAlchemy ORM

### Relationship types:
- **Association:** Defined the following bidirectional relationships using `ForeignKey` and `relationship()` with `back_populates`:
	- **One-to-many** between Buildings and BuildingEnergy:
		- Building can have multiple energy readings. Each BuildingEnergy reading belongs to exactly one Building.
		- `Building.energy_readings` references all associated energy readings.
		- `BuildingEnergy.building` references the parent building.
	- **One-to-many** between Users and SustainableActivities:
		- User can have multiple sustainable activities. Each SustainableActivity belongs to exactly one User
		- `User.activities` references all associated activities
		- `SustainableActivity.user` references the parent user
- **Aggregation**:
	- **One-to-one** between Users and UserPoints:
		- User can have one associated UserPoints record. Each UserPoints record belongs to exactly one User.
		- `User.points` references the associated UserPoints record.
		- `UserPoints.user` references the parent user.
