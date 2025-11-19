CREATE DATABASE projecteval;
USE projecteval;

CREATE TABLE Student (
    StudentID INT PRIMARY KEY,
    Dept VARCHAR(50) NOT NULL,
    Year INT NOT NULL,
    Fname VARCHAR(50),
    Lname VARCHAR(50),
    Age INT CHECK (Age > 15),
    PhoneNo VARCHAR(15) UNIQUE
);

CREATE TABLE Team (
    TeamID INT PRIMARY KEY,
    TeamName VARCHAR(100) NOT NULL,
    Members INT CHECK (Members > 0),
    StudentID INT,
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE Project (
    ProjectID INT PRIMARY KEY,
    Title VARCHAR(100) NOT NULL,
    Domain VARCHAR(50),
    Technology VARCHAR(50),
    Duration VARCHAR(30),
    TeamID INT,
    FOREIGN KEY (TeamID) REFERENCES Team(TeamID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE Grade (
    Grade CHAR(2) NOT NULL,
    FinalScore DECIMAL(5,2),
    ProjectID INT,
    PRIMARY KEY (ProjectID),
    FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE Evaluation (
    EvaluationID INT PRIMARY KEY,
    TotalMarks INT,
    Rounds INT DEFAULT 1,
    EvalDate DATE DEFAULT (CURRENT_DATE),
    Comments VARCHAR(255)
);

CREATE TABLE Marks (
    MarksObtained INT,
    MaxMarks INT NOT NULL,
    Percentage DECIMAL(5,2),
    EvaluationID INT,
    FOREIGN KEY (EvaluationID) REFERENCES Evaluation(EvaluationID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE Faculty (
    FacultyID INT PRIMARY KEY,
    Name VARCHAR(50),
    Email VARCHAR(100) UNIQUE,
    PhoneNo VARCHAR(15),
    ProjectID INT,
    EvaluationID INT,
    FOREIGN KEY (ProjectID) REFERENCES Project(ProjectID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (EvaluationID) REFERENCES Evaluation(EvaluationID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);


INSERT INTO Student VALUES
(1, 'CSE', 3, 'Aarav', 'Sharma', 20, '9876543210'),
(2, 'CSE', 3, 'Meera', 'Iyer', 21, '9876543211'),
(3, 'ECE', 2, 'Rohit', 'Verma', 19, '9876543212'),
(4, 'ISE', 4, 'Sneha', 'Patil', 22, '9876543213'),
(5, 'EEE', 3, 'Karan', 'Rao', 20, '9876543214'),
(6, 'CSE', 2, 'Tanya', 'Reddy', 19, '9876543215');



INSERT INTO Team VALUES
(101, 'Alpha Innovators', 3, 1),
(102, 'Tech Pioneers', 2, 2),
(103, 'Robo Squad', 4, 3),
(104, 'Data Dynamos', 3, 4),
(105, 'Cloud Ninjas', 2, 5),
(106, 'Code Masters', 3, 6);



INSERT INTO Project VALUES
(201, 'Smart Attendance System', 'AI', 'Python, OpenCV', '6 months', 101),
(202, 'IoT Weather Monitor', 'IoT', 'Arduino, MQTT', '5 months', 102),
(203, 'Autonomous Robot', 'Robotics', 'ROS, C++', '8 months', 103),
(204, 'Stock Price Predictor', 'ML', 'Python, TensorFlow', '4 months', 104),
(205, 'Cloud File Manager', 'Cloud', 'Java, AWS', '6 months', 105),
(206, 'AI Chatbot', 'AI', 'Python, NLP', '5 months', 106);



INSERT INTO Evaluation VALUES
(301, 100, 2, '2025-08-01', 'Good progress'),
(302, 90, 1, '2025-08-02', 'Needs improvement'),
(303, 95, 3, '2025-08-03', 'Excellent work'),
(304, 85, 2, '2025-08-04', 'Average performance'),
(305, 92, 2, '2025-08-05', 'Strong execution'),
(306, 98, 2, '2025-10-23', 'Excellent concept!');



INSERT INTO Grade VALUES
('A', 95.00, 201),
('B+', 88.00, 202),
('A+', 98.00, 203),
('B', 82.00, 204),
('A', 90.00, 205);


INSERT INTO Marks VALUES
(90, 100, 90.00, 301),
(70, 90, 77.78, 302),
(95, 100, 95.00, 303),
(68, 85, 80.00, 304),
(85, 92, 92.39, 305);


INSERT INTO Faculty VALUES
(401, 'Prof. Ramesh', 'ramesh@college.edu', '9000000001', 201, 301),
(402, 'Dr. Priya', 'priya@college.edu', '9000000002', 202, 302),
(403, 'Dr. Nikhil', 'nikhil@college.edu', '9000000003', 203, 303),
(404, 'Prof. Kavita', 'kavita@college.edu', '9000000004', 204, 304),
(405, 'Dr. Sameer', 'sameer@college.edu', '9000000005', 205, 305);

CALL sp_add_evaluation_with_marks(307, 100, 3, '2025-10-24', 'Final Evaluation', 96, 100);

-- List all projects with their teams and domains
SELECT p.ProjectID, p.Title, t.TeamName, p.Domain
FROM Project p
JOIN Team t ON p.TeamID = t.TeamID;

-- Show students with their teams
SELECT s.Fname, s.Lname, t.TeamName
FROM Student s
JOIN Team t ON s.StudentID = t.StudentID;

-- Update total marks for a specific evaluation
UPDATE Evaluation
SET TotalMarks = 99
WHERE EvaluationID = 306;

-- Update grade if performance improved
UPDATE Grade
SET FinalScore = 93.5
WHERE ProjectID = 205;

-- Delete a project and check cascading deletes
DELETE FROM Project WHERE ProjectID = 204;

SELECT p.Title, f.Name AS Faculty, g.Grade, g.FinalScore
FROM Project p
JOIN Faculty f ON p.ProjectID = f.ProjectID
JOIN Grade g ON p.ProjectID = g.ProjectID
ORDER BY g.FinalScore DESC;

SELECT Fname, Lname
FROM Student
WHERE StudentID IN (
    SELECT StudentID FROM Team
    WHERE TeamID IN (
        SELECT TeamID FROM Project
        WHERE Domain = 'AI'
    )
);
