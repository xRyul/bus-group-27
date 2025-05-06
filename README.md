# GreenCampus

<img width="1062" alt="image" src="https://github.com/user-attachments/assets/f7bbd2db-f173-446a-9723-d47d64429664" />


## System Description
GreenCampus is an integrated digital platform that helps universities track, manage, and reduce their environmental impact while engaging the campus community in sustainability efforts. The system bridges the gap between institutional sustainability reporting and community engagement by combining building energy monitoring with user-submitted sustainable activities and incentives. This prototype demonstrates the feasibility of three core features: Building Energy Monitoring Dashboard (FR2), Sustainable Activity Submission (FR5), and Point/GreenScore Awarding (FR6).

## How to run

### Live Demo
The live version of the project is accessible through two URLs:
- [http://green-campus.me/](http://green-campus.me/)
- [https://bus-group-27.onrender.com/](https://bus-group-27.onrender.com/)

It is deployed using a custom domain `green-campus.me` registered through Namecheap, hosted on Render.com with automatic SSL certificate management. CI/CD pipeline is configured to build and deploy on commits to the `main` branch.

### Local Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/xRyul/bus-group-27.git
   cd bus-group-27
   ```

2. **Set up the environment** (two options):

   **Option 1: Using conda (recommended)**:
    Make sure you have `conda` installed and added into PATH, then simply install the dependencies and activate newly created environment by using below two commands:

   ```bash
   conda env create -f environment.yml
   conda activate BUS-prototype-env
   ```

   **Option 2: Using pip and venv**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: source venv/Scripts/activate
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   flask run # On Windows you might need to run: python -m flask run
   ```
   
   The application should be available at http://127.0.0.1:5000/

4. **Reset the database** (if needed):
   ```bash
   flask shell
   ```
   
   Then in the flask shell:
   ```python
   reset_db()
   exit()
   ```

5. Login details: 

Admin: `amy`
Password: `p123`

Student: `tom`
Password: `p123`

### Running Tests

We used pytest with Behavior-Driven Development (BDD) for testing (pytest-bdd). Each core feature has both positive and negative test cases.

To run all tests with verbose output:
```bash
python -m pytest -v
```

## Technologies Used
- **Backend**: Python 3.11, Flask (Web Framework), SQLAlchemy (ORM)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5, Chart.js
- **Database**: SQLite, SQLAlchemy ORM
- **Testing**: Pytest, pytest-bdd
- **Version Control**: Git
- **Deployment**: Render.com (hosting platform), Namecheap (domain registration)

## Implemented Features
1. **Building Energy Monitoring Dashboard (FR2)**
   - Displays building energy consumption data with visualizations
   - Identifies and displays anomalies in energy usage patterns
   - Shows historical data and trends

2. **Sustainable Activity Submission & Verification (FR5)**
   - Allows users to submit sustainable activities
   - Provides an interface for admin verification
   - Manages activity status (pending, verified, rejected)

3. **Point/GreenScore Awarding for Activities (FR6)**
   - Awards points to users based on verified activities
   - Calculates carbon impact (GreenScore)
   - Displays user rankings and leaderboards


## Contribution table based on commit history

| Contributor               | Percentage | Work Completed (Prioritized by Assignment Requirements)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| :------------------------ | :--------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Daniel Alesko (xRyul)** | **60%**    | - System architecture design (MVCS), base model definition & ORM relationships (Association/Aggregation).<br>- Implemented positive & negative tests for FR2, FR5, FR6 using BDD<br>- UI and Data Visualization for Building Energy Monitoring Dashboard (FR2); Landing Page.<br>- FR5/FR6: Refactoring for MVCS architecture, Integration into views, Bug fixes.<br>- Overall project frontend development (HTML, CSS, JS).<br>- Project and CI/CD pipeline setup; Domain registration `green-campus.me` ; Automated deployment via `render.com`.<br> |
| **Charley Ottey (Yztto)** | **20%**    | - Green Score UI implementation  <br>- Admin interface and user management  <br>- User Submission functionality  <br>- Activity tracking and leaderboard  <br>- Form handling and validation                                                                                                                                                                                                                                                                                                                                                           |
| **Jessiah Buamah**        | **10%**    | - Community Engagement logic (FR5, FR6)  <br>- Activity submission and verification  <br>- Points calculation logic  <br>- Data model design for sustainable activities                                                                                                                                                                                                                                                                                                                                                                                |
| **Jamie Chappell**        | **10%**    | - Backend logic implementation for Building Energy Monitoring.<br>- Implemented Singleton pattern for `BuildingEnergyMonitoring`.<br>- Anomaly detection algorithm development<br>- Mock data generation & DB population for FR2.                                                                                                                                                                                                                                                                                                                      |




# ALL BELOW IS NOT PART OF SUBMISSION: DELETE

<details><summary><b>Assignment 2 Requirements:</b></summary>

- **THREE** core features.
- **ONE** design pattern.
- **TWO** class relationships (Association, Inheritance, etc.).  
- **ONE positive** & **ONE negative** test case per feature.  
- Use Git for version control (mandatory, log needed).  
- Simulate external systems (mocking/hard-coding).  

**Submission Deliverables:**
-   **Source Code:** Well-organized, commented.
-   **README.md:**
    -   Brief system description & purpose (max 200 words).
    -   Step-by-step run instructions.
    -   List of languages, frameworks, tools used.
    -   Summary of implemented functionalities.
    -   Contribution table (percentage, specific work, signed).
-   **Git Log:** Exported log (`git log > gitlog.txt`).
-   **Demo Video:** Max 4 mins (AVI, MP4, MOV). Explain implementation, show key aspects satisfaction, discuss methodology/design principles/architecture.

</details>


<details>
<summary><b>FAQ by Wendy</b></summary>

Originally posted by Wendy on [TEAMS](https://teams.microsoft.com/l/message/19:c7e55754082d45c794c3479aa0668614@thread.tacv2/1743249969522?tenantId=b024cacf-dede-4241-a15c-3c97d553e9f3&groupId=57e159d8-1648-4d26-a608-848d07a94a88&parentMessageId=1743249969522&teamName=BUS%202024%20Support%20Students%20-%20Teaching&channelName=Assignment%20-Part2%20Queries&createdTime=1743249969522)

![image](https://github.com/user-attachments/assets/6e9a73c8-d74b-4f35-afeb-699b51a7c623)

1.  **Do I have to implement the entire system described in Assignment 1?**
    No. You only need to implement a working prototype of the most critical three features of your design to demonstrate feasibility.

2.  **What are considered "critical features"?**
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


<details>
<summary><b>Architecture</b></summary>

### MVC Architecture with Service Layer (MVCS)
- **Model** (app/models/): Data structures using SQLAlchemy ORM, entity relationships and defines database schema
- **View** (app/templates/): HTML templates with Jinja2, presents data to users and handles UI
- **Controller** (app/views.py): Flask routes that handle HTTP requests, coordination between components, manages form submission and validation, renders templates with appropriate data
- **Service** (app/logic.py): Contains the actual logic for operaitions for BuildingEnergyMonitoring and CommunityEngagement; Processes data transformations. 
</details>

<details>
<summary><b>Design Patterns and Relationships</b></summary>

### Design Pattern
- **Singleton** implemented in `BuildingEnergyMonitoring` class to ensure a single instance manages energy data across the application
  - Aligns with Building-Energy one-to-many association by providing centralized control over energy data
- Note: `CommunityEngagement` intentionally does not use Singleton as it needs multiple instances (one per user) to handle user-specific activities
  - Aligns with User-Activity one-to-many association and User-Points one-to-one aggregation

### Relationship types:
- **Association:** Defined the following bidirectional relationships using `ForeignKey` and `relationship()` with `back_populates`:
	- **One-to-many** between Buildings and BuildingEnergy:
		- Building can have multiple energy readings. Each BuildingEnergy reading belongs to exactly one Building.
		- `Building.energy_readings` references all associated energy readings.
		- `BuildingEnergy.building` references the parent building.
		- Managed by Singleton `BuildingEnergyMonitoring` class for centralized control
	- **One-to-many** between Users and SustainableActivities:
		- User can have multiple sustainable activities. Each SustainableActivity belongs to exactly one User
		- `User.activities` references all associated activities
		- `SustainableActivity.user` references the parent user
		- Managed by multiple `CommunityEngagement` instances (one per user)
- **Aggregation**:
	- **One-to-one** between Users and UserPoints:
		- User can have one associated UserPoints record. Each UserPoints record belongs to exactly one User.
		- `User.points` references the associated UserPoints record.
		- `UserPoints.user` references the parent user.
		- Managed by user-specific `CommunityEngagement` instances
</details>