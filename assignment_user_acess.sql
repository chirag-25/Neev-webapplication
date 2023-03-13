# Select Operations on the granted table(teams)

show databases;
use NEEV; 
SELECT * FROM teams;

--  Question 5
# Changing the developer salary to 60000 from 50000
UPDATE teams SET salary = 60000 WHERE position = "Developer";
SELECT * FROM teams;

# Deleting the member whose reason_of_leaving is better opportunity
DELETE FROM teams WHERE reason_of_leaving = "Better opportunity";
SELECT * FROM teams;

# Operations on view1 by user1
SELECT * FROM view1;
UPDATE view1 SET pre_volunteering = "Yes" WHERE event_name = "Project B";
DELETE FROM view1 WHERE event_name = "Project A";

-- Question 7
	# table
SELECT * FROM teams;
UPDATE teams SET salary = 60000 WHERE position = "Developer";
DELETE FROM teams WHERE reason_of_leaving = "Better opportunity";

	# view1
SELECT * FROM view1;
UPDATE view1 SET pre_volunteering = "Yes" WHERE event_name = "Project B";
DELETE FROM view1 WHERE event_name = "Project A";




