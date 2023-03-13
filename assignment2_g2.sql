show databases;
USE NEEV;
SHOW tables;

-- Question 1
CREATE USER 'user1'@'localhost' IDENTIFIED BY 'password1';
SELECT user FROM mysql.user;
SELECT user FROM mysql.user WHERE user = 'user1';


-- Question 2
# for view 1
CREATE TABLE temp_table as SELECT v.email_id AS v_email_id, vg.* FROM volunteers v INNER JOIN volunteering vg ON v.email_id = vg.email_id;
SELECT * FROM temp_table;
ALTER TABLE temp_table ADD pre_volunteering ENUM("Yes", "No");
SELECT * FROM temp_table;
UPDATE temp_table SET pre_volunteering = "Yes" WHERE event_name = "Project A";
UPDATE temp_table SET pre_volunteering = "No" WHERE event_name != "Project A";
SELECT * FROM temp_table;
CREATE VIEW view1 AS SELECT * FROM temp_table;
SELECT * FROM view1;

# for view 2
CREATE TABLE temp_table2 as SELECT t.email_id AS t_email_id, tr.* FROM trains t INNER JOIN Trainers tr ON t.email_id = tr.email_id;
SELECT * FROM temp_table2;
ALTER TABLE temp_table2 ADD rating ENUM("1","2","3","4","5");
UPDATE temp_table2 SET rating = "1" WHERE fee < 2001;
UPDATE temp_table2 SET rating = "2" WHERE fee < 3001 AND fee > 2001;
UPDATE temp_table2 SET rating = "3" WHERE fee < 4001 AND fee > 3001;
SELECT * FROM temp_table2;
CREATE VIEW view2 AS SELECT * FROM temp_table2;
SELECT * FROM view2;

-- Question 3
# Assuming the teams as table1
# Query for Granting the persmission to the user1 
GRANT SELECT, UPDATE, DELETE ON teams to 'user1'@'localhost';
SHOW GRANTS FOR 'user1'@'localhost';


-- Question 4
GRANT SELECT ON view1 to 'user1'@'localhost';
SHOW GRANTS FOR 'user1'@'localhost';

-- Question 5
# Queries were in the files of user


-- Question 6
# Revoke UPDATE and DELETE permissions on "table1" for "user1"
REVOKE UPDATE, DELETE ON teams FROM 'user1'@'localhost';

-- Question 7
# Queries were in the files of user







