# Project Evaluation and Grading System

A Python Tkinter + MySQL desktop application to manage student projects, evaluations, marks, and grades.[3]

## 👥 Team Members

- PES2UG23CS270 — Kavyasree Panganamala
- PES2UG23CS269 — Kavyashree M

## 📌 Features

- CRUD for Students, Teams, Projects, Evaluations, Marks, Grades
- Auto percentage calculation (MySQL Trigger)
- Percentage recalculation (Stored Procedure)
- Reports with SQL Views
- Nested, Join, Aggregate queries (GUI)
- MySQL user creation and privilege management
- Tkinter TreeView for full GUI output

## 🛠 Tech Stack

- Python 3.x
- Tkinter
- MySQL
- mysql-connector-python

## 📂 Project Structure

```
MINI_PROJECT/
│── project_eval_gui.py
│── README.md
│── review_queries.sql
└── schema_tables.sql
```
*SQL files contain the schema and example queries; main app is in project_eval_gui.py.*

## ⚙️ Setup Instructions

1. **Install dependencies**
   ```
   pip install mysql-connector-python
   ```
2. **Database setup**
   ```
   CREATE DATABASE project_eval;
   USE project_eval;
   ```
3. **Create tables**
   Use `schema_tables.sql` to create *Student, Team, Project, Evaluation, Marks, Grade* tables.
4. **Configure credentials in `project_eval_gui.py`**
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': 'YOUR_PASSWORD',
       'database': 'project_eval'
   }
   ```
5. **Run the application**
   ```
   python project_eval_gui.py
   ```

## 🧩 Database Components

**Trigger**
```sql
CREATE TRIGGER trg_marks_set_percentage
BEFORE INSERT ON Marks
FOR EACH ROW
BEGIN
    IF NEW.MaxMarks <> 0 THEN
        SET NEW.Percentage = (NEW.MarksObtained / NEW.MaxMarks) * 100;
    END IF;
END;
```
**Stored Procedure**
```sql
CREATE PROCEDURE sp_recalc_percentage(IN p_eid INT)
BEGIN
    UPDATE Marks
    SET Percentage = (MarksObtained / MaxMarks) * 100
    WHERE EvaluationID = p_eid;
END;
```
**Views**
```sql
CREATE VIEW vw_project_summary AS
SELECT p.ProjectID, p.Title, p.Domain, p.Technology, p.Duration,
       t.TeamName, t.Members, g.Grade, g.FinalScore
FROM Project p
LEFT JOIN Team t ON p.TeamID = t.TeamID
LEFT JOIN Grade g ON p.ProjectID = g.ProjectID;

CREATE VIEW vw_top_projects AS
SELECT p.ProjectID, p.Title, g.FinalScore
FROM Project p
JOIN Grade g ON p.ProjectID = g.ProjectID
ORDER BY g.FinalScore DESC;
```

## 📊 Queries Implemented (GUI)

- **Nested Query:** FinalScore > Average FinalScore
- **Join Query:** Student ↔ Team
- **Aggregate Query:** Count projects per domain

## ✔ Project Status

- Fully functional ✔
- All DBMS requirements met ✔
- Triggers, procedures, views, and advanced queries ✔

