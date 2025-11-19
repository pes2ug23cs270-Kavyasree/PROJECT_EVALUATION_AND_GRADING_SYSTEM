-- STEP 1: use your database
USE projecteval;

-- STEP 2: create TeamMember table (if not already)
CREATE TABLE IF NOT EXISTS TeamMember (
  TeamID INT NOT NULL,
  StudentID INT NOT NULL,
  Role VARCHAR(50),
  PRIMARY KEY (TeamID, StudentID),
  FOREIGN KEY (TeamID) REFERENCES Team(TeamID) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (StudentID) REFERENCES Student(StudentID) ON DELETE CASCADE ON UPDATE CASCADE
);


INSERT IGNORE INTO TeamMember(TeamID, StudentID, Role)
SELECT TeamID, StudentID, NULL FROM Team WHERE StudentID IS NOT NULL;

-- STEP 3: Trigger to update Members count when TeamMember changes
DELIMITER $$

CREATE TRIGGER trg_teammember_after_insert
AFTER INSERT ON TeamMember
FOR EACH ROW
BEGIN
  UPDATE Team SET Members = COALESCE(Members,0) + 1 WHERE TeamID = NEW.TeamID;
END$$

CREATE TRIGGER trg_teammember_after_delete
AFTER DELETE ON TeamMember
FOR EACH ROW
BEGIN
  UPDATE Team SET Members = COALESCE(Members,0) - 1 WHERE TeamID = OLD.TeamID;
END$$

CREATE TRIGGER trg_teammember_after_update
AFTER UPDATE ON TeamMember
FOR EACH ROW
BEGIN
  IF NEW.TeamID <> OLD.TeamID THEN
    UPDATE Team SET Members = COALESCE(Members,0) + 1 WHERE TeamID = NEW.TeamID;
    UPDATE Team SET Members = COALESCE(Members,0) - 1 WHERE TeamID = OLD.TeamID;
  END IF;
END$$

DELIMITER ;

-- STEP 4: Trigger to auto-calc percentage in Marks table
DELIMITER $$

CREATE TRIGGER trg_marks_before_insert
BEFORE INSERT ON Marks
FOR EACH ROW
BEGIN
  IF NEW.MaxMarks > 0 THEN
    SET NEW.Percentage = ROUND((NEW.MarksObtained*100.0)/NEW.MaxMarks,2);
  ELSE
    SET NEW.Percentage = NULL;
  END IF;
END$$

CREATE TRIGGER trg_marks_before_update
BEFORE UPDATE ON Marks
FOR EACH ROW
BEGIN
  IF NEW.MaxMarks > 0 THEN
    SET NEW.Percentage = ROUND((NEW.MarksObtained*100.0)/NEW.MaxMarks,2);
  ELSE
    SET NEW.Percentage = NULL;
  END IF;
END$$

DELIMITER ;

-- STEP 5: Function to return grade label
DELIMITER $$

CREATE FUNCTION get_grade_label(score DECIMAL(5,2)) RETURNS CHAR(2)
DETERMINISTIC
BEGIN
  DECLARE g CHAR(2);
  IF score >= 98 THEN
    SET g = 'A+';
  ELSEIF score >= 90 THEN
    SET g = 'A';
  ELSEIF score >= 80 THEN
    SET g = 'B+';
  ELSEIF score >= 70 THEN
    SET g = 'B';
  ELSE
    SET g = 'C';
  END IF;
  RETURN g;
END$$

DELIMITER ;

-- STEP 6: Trigger to auto-fill Grade table
DELIMITER $$

CREATE TRIGGER trg_grade_before_insert
BEFORE INSERT ON Grade
FOR EACH ROW
BEGIN
  SET NEW.Grade = get_grade_label(NEW.FinalScore);
END$$

CREATE TRIGGER trg_grade_before_update
BEFORE UPDATE ON Grade
FOR EACH ROW
BEGIN
  SET NEW.Grade = get_grade_label(NEW.FinalScore);
END$$

DELIMITER ;

-- STEP 7: Stored procedure to add evaluation with marks (transaction)
DELIMITER $$

CREATE PROCEDURE sp_add_evaluation_with_marks(
  IN p_EvalID INT, IN p_TotalMarks INT, IN p_Rounds INT,
  IN p_EvalDate DATE, IN p_Comments VARCHAR(255),
  IN p_MarksObtained INT, IN p_MaxMarks INT)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    SELECT 'Error: transaction rolled back' AS msg;
  END;

  START TRANSACTION;
    INSERT INTO Evaluation (EvaluationID, TotalMarks, Rounds, EvalDate, Comments)
    VALUES (p_EvalID, p_TotalMarks, p_Rounds, p_EvalDate, p_Comments);

    INSERT INTO Marks (MarksObtained, MaxMarks, Percentage, EvaluationID)
    VALUES (p_MarksObtained, p_MaxMarks, NULL, p_EvalID);
  COMMIT;

  SELECT 'Success: evaluation and marks added' AS msg;
END$$

DELIMITER ;

-- STEP 8: Function to compute average percentage for a project
DELIMITER $$

CREATE FUNCTION fn_project_avg_percentage(p_ProjectID INT) RETURNS DECIMAL(5,2)
DETERMINISTIC
BEGIN
  DECLARE avg_pct DECIMAL(5,2);
  SELECT ROUND(AVG(m.Percentage),2) INTO avg_pct
  FROM Marks m
  JOIN Evaluation e ON m.EvaluationID = e.EvaluationID
  JOIN Faculty f ON e.EvaluationID = f.EvaluationID
  WHERE f.ProjectID = p_ProjectID;
  RETURN IFNULL(avg_pct, 0);
END$$

DELIMITER ;

-- STEP 9: Create sample views
CREATE OR REPLACE VIEW vw_project_summary AS
SELECT p.ProjectID, p.Title, p.Domain, p.Technology, p.Duration,
       t.TeamName, COALESCE(t.Members,0) AS Members, g.Grade, g.FinalScore
FROM Project p
LEFT JOIN Team t ON p.TeamID = t.TeamID
LEFT JOIN Grade g ON p.ProjectID = g.ProjectID;

CREATE OR REPLACE VIEW vw_top_projects AS
SELECT p.ProjectID, p.Title, g.FinalScore
FROM Project p JOIN Grade g ON p.ProjectID = g.ProjectID
ORDER BY g.FinalScore DESC;

-- STEP 10: test runs
-- (replace IDs with ones that exist in your DB)

-- test percentage trigger
INSERT INTO Marks (MarksObtained, MaxMarks, Percentage, EvaluationID)
VALUES (88, 100, NULL, 301);
SELECT * FROM Marks WHERE EvaluationID = 301;

-- test grade trigger
INSERT INTO Grade (Grade, FinalScore, ProjectID)
VALUES (NULL, 92, 206);
SELECT * FROM Grade WHERE ProjectID = 206;

-- test procedure
CALL sp_add_evaluation_with_marks(399, 100, 1, '2025-10-20', 'Test Eval', 87, 100);
SELECT * FROM Evaluation WHERE EvaluationID = 399;
SELECT * FROM Marks WHERE EvaluationID = 399;

-- test function
SELECT fn_project_avg_percentage(201) AS avg_pct;

-- test views
SELECT * FROM vw_project_summary LIMIT 5;
SELECT * FROM vw_top_projects LIMIT 5;