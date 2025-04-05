# GreenCampus

## Assignment 2 Requirements: 
* **THREE** core features.
  * Building Energy Monitoring (FR2), Community Engagement (FR5, FR6)
* **ONE** design pattern.
  * Singleton
* **TWO** class relationships (Association, Inheritance, etc.).  
* **ONE positive** & **ONE negative** test case per feature.  
* Use Git for version control (mandatory, log needed).  
* Simulate external systems (mocking/hard-coding).  

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