create database NEEV2;
use NEEV2;

-- done
create table Trainers (
email_id varchar(50) primary key,
fee int default null,
name varchar(50) not null,
age int not null,
gender enum('Male', 'Female', 'Others') not null
);

-- drop table Trainers;


create table Beneficiary (
aadhar_id bigint primary key,
name varchar(50) not null,
date_of_birth date not null,
gender enum('Male', 'Female', 'Others') not null,
marital_status varchar(10) not null,
education varchar(50) not null,
photo longblob default null,
employed varchar(20) default null,
photo_caption VARCHAR(255) DEFAULT NULL
);


create table Teams (
employee_id varchar(20) primary key,
name varchar(50) not null,
email_id varchar(50) unique,
salary int not null,
position varchar(50) not null,
year_of_joining date not null,
year_of_leaving date default null,
reason_of_leaving text default null
);

create table Projects (
event_name varchar(50),
start_date date,
primary key (event_name, start_date),
types varchar(50) not null,
budget int not null,
no_of_participants int not null,
duration int not null,
collection int default null,
total_expense int not null
);

CREATE TABLE ProjectPhotos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  project_event_name VARCHAR(50),
  project_start_date DATE,
  photo_url longblob NOT NULL,
  caption VARCHAR(255) DEFAULT NULL,
  FOREIGN KEY (project_event_name, project_start_date)
	REFERENCES Projects(event_name, start_date)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);


create table Volunteers (
email_id varchar(50) primary key,
name varchar(50) not null,
phone_number bigint not null,
date_of_birth date default null,
gender enum('Male', 'Female', 'Others') not null
);

create table Funding (
email_id varchar(50) primary key,
amount int not null,
funder_name varchar(50) not null,
date date not null
);

create table Venue (
venue_id varchar(20) primary key,
place varchar(100) not null,
pincode int not null,
district varchar (50) not null,
state varchar (50) not null
);

create table VillageProfile (
pincode int primary key,
name varchar(50) not null,
no_of_beneficiaries int not null,
no_of_primary_health_center int not null,
no_of_primary_school int not null,
transport varchar(100) default null,
infrastructure varchar(100) default null,
major_occupation varchar(100) default null,
technical_literacy text default null,
year date not null
);

-- create table EmployeePhoneEntity (
-- phone_number int primary key,
-- location
-- );


create table Goods (
event_name varchar(50),
start_date date,
item_name varchar(50),
quantity int,
amount int,
primary key (event_name, start_date, item_name, quantity, amount),
foreign key (event_name, start_date) 
references Projects(event_name, start_date) on delete cascade on update cascade
);

create table ProjectExpense (
event_name varchar(50),
start_date date,
description varchar(255),
amount int,
primary key (event_name, start_date, description, amount),
foreign key (event_name, start_date) 
references Projects(event_name, start_date) on delete cascade on update cascade
);

create table TrainerPhoneEntity (
email_id varchar(50),
phone_number bigint not null,
primary key (email_id, phone_number),
foreign key (email_id) references Trainers(email_id) on delete cascade on update cascade
);

create table BeneficiaryPhoneEntity (
aadhar_id bigint not null,
phone_number bigint not null,
primary key (aadhar_id, phone_number),
foreign key (aadhar_id) references Beneficiary(aadhar_id) on delete cascade on update cascade
);


# Relation Tables 

create table TeamPhone (
employee_id varchar(20) not null,
phone_number bigint not null,
location text default null,
primary key (employee_id, phone_number),
foreign key (employee_id) references Teams(employee_id) on delete cascade on update cascade
);




create table Organize (
employee_id varchar(20),
event_name varchar(50),
start_date date,
role varchar(50) not null,
primary key (employee_id, event_name, start_date),
foreign key(employee_id) references Teams(employee_id) on delete cascade on update cascade,
foreign key(event_name, start_date) references Projects(event_name, start_date) on delete cascade 
on update cascade
);

create table sponsors(
email_id varchar(50),
event_name varchar(50),
start_date date,
primary key (email_id, event_name, start_date),
foreign key(email_id) references Funding(email_id) on delete cascade on update cascade,
foreign key(event_name, start_date) references Projects(event_name, start_date) on delete cascade 
on update cascade
);

create table volunteering(
email_id varchar(50),
event_name varchar(50),
start_date date,
primary key (email_id, event_name, start_date),
foreign key(email_id) references Volunteers(email_id) on delete cascade on update cascade,
foreign key(event_name, start_date) references Projects(event_name, start_date) on delete cascade 
on update cascade
);

create table HeldAt(
venue_id varchar(20),
event_name varchar(50),
start_date date,
primary key (venue_id, event_name, start_date),
foreign key(venue_id) references Venue(venue_id) on delete cascade on update cascade,
foreign key(event_name, start_date) references Projects(event_name, start_date) on delete cascade
on update cascade
);

create table trains(
email_id varchar(50),
event_name varchar(50),
start_date date,
primary key (email_id, event_name, start_date),
foreign key(email_id) references Trainers(email_id) on delete cascade on update cascade,
foreign key(event_name, start_date) references Projects(event_name, start_date) on delete cascade
on update cascade
);

create table participants(
aadhar_id bigint, 
event_name varchar(50),
start_date date,
primary key (aadhar_id, event_name, start_date),
foreign key(aadhar_id) references Beneficiary(aadhar_id) on delete cascade on update cascade,
foreign key(event_name, start_date) references Projects(event_name, start_date) on delete cascade
on update cascade
);

create table TrainerBeneficiary(
aadhar_id bigint, 
email_id varchar(50),
primary key (aadhar_id),
foreign key(aadhar_id) references Beneficiary(aadhar_id) on delete cascade on update cascade,
foreign key(email_id) references Trainers(email_id) on delete cascade
on update cascade
);

create table assessment(
aadhar_id bigint, 
event_name varchar(50),
start_date date,
Date date NOT NULL, 
present_or_absent enum('Present', 'Absent') NOT NULL,
primary key (aadhar_id),
foreign key(aadhar_id) references Beneficiary(aadhar_id) on delete cascade on update cascade,
foreign key(event_name, start_date) references Projects(event_name, start_date) on delete cascade
on update cascade
);

create table belongs(
aadhar_id bigint, 
pincode int,
primary key (aadhar_id),
foreign key(aadhar_id) references Beneficiary(aadhar_id) on delete cascade on update cascade,
foreign key(pincode) references VillageProfile(pincode) on delete cascade
on update cascade
);





# Data Population
#Adding dummy values to Beneficiary
INSERT INTO Beneficiary (aadhar_id, name, date_of_birth, gender, marital_status, education, photo, employed, photo_caption)
VALUES
(123456789011, 'Asha Sharma', '1980-05-12', 'Female', 'Married', 'Master of Business Administration', 'https://example.com/photo1.jpg', 'Yes', 'Photo of Asha Sharma'),
(234567890121, 'Rahul Singh', '1995-08-02', 'Male', 'Unmarried', 'Bachelor of Engineering', 'https://example.com/photo1.jpg', 'Yes', 'Photo of Rahul Singh'),
(345678901231, 'Priya Patel', '1988-12-25', 'Female', 'Married', 'Doctor of Medicine', 'https://example.com/photo1.jpg', 'No', NULL),
(456789012341, 'Rajesh Kumar', '1976-09-18', 'Male', 'Married', 'Bachelor of Science', 'https://example.com/photo1.jpg', 'Yes', 'Photo of Rajesh Kumar'),
(567890123451, 'Sneha Gupta', '1992-04-01', 'Female', 'Unmarried', 'Master of Computer Applications', 'https://example.com/photo1.jpg', 'No', NULL),
(678901234561, 'Vikram Singh', '1985-06-21', 'Male', 'Married', 'Bachelor of Commerce', 'https://example.com/photo1.jpg', 'Yes', 'Photo of Vikram Singh'),
(789012345671, 'Anjali Reddy', '1990-03-15', 'Female', 'Unmarried', 'Bachelor of Arts', 'https://example.com/photo1.jpg', 'No', NULL),
(890123456781, 'Amit Sharma', '1983-11-08', 'Male', 'Married', 'Master of Science', 'https://example.com/photo1.jpg', 'Yes', 'Photo of Amit Sharma'),
(901234567891, 'Shalini Verma', '1987-07-14', 'Female', 'Married', 'Bachelor of Business Administration', NULL, 'No', NULL),
(123450987651, 'Sanjay Kumar', '1979-01-31', 'Male', 'Married', 'Master of Arts', 'https://example.com/photo1.jpg', 'Yes', 'Photo of Sanjay Kumar');

 
#Adding dummy values to Funding
INSERT INTO Funding (email_id, amount, funder_name, date) VALUES
('abc@gmail.com', 50000, 'Rohit Sharma', '2022-02-01'),
('def@gmail.com', 25000, 'Neha Gupta', '2022-02-03'),
('ghi@gmail.com', 100000, 'Rajesh Singh', '2022-02-06'),
('jkl@gmail.com', 75000, 'Priya Patel', '2022-02-10'),
('mno@gmail.com', 30000, 'Siddharth Reddy', '2022-02-12'),
('pqr@gmail.com', 150000, 'Amit Kumar', '2022-02-15'),
('stu@gmail.com', 5000, 'Shreya Gupta', '2022-02-17'),
('vwx@gmail.com', 80000, 'Anjali Sharma', '2022-02-20'),
('yz@gmail.com', 20000, 'Suresh Patel', '2022-02-22'),
('abc1@gmail.com', 40000, 'Manisha Singh', '2022-02-25');

#Adding dummy values to teams
INSERT INTO Teams (employee_id, name, email_id, salary, position, year_of_joining, year_of_leaving, reason_of_leaving) VALUES
('E001', 'Ravi Kumar', 'ravi.kumar@example.com', 50000, 'Manager', '2015-01-01', null, null),
('E002', 'Priya Sharma', 'priya.sharma@example.com', 40000, 'Developer', '2016-02-01', null, null),
('E003', 'Amit Singh', 'amit.singh@example.com', 45000, 'Developer', '2017-03-01', null, null),
('E004', 'Neha Gupta', 'neha.gupta@example.com', 55000, 'Designer', '2018-04-01', null, null),
('E005', 'Rajesh Khanna', 'rajesh.khanna@example.com', 60000, 'Manager', '2019-05-01', null, null),
('E006', 'Anjali Verma', 'anjali.verma@example.com', 35000, 'Developer', '2020-06-01', null, null),
('E007', 'Suresh Menon', 'suresh.menon@example.com', 45000, 'Developer', '2021-07-01', null, null),
('E008', 'Nisha Rawat', 'nisha.rawat@example.com', 50000, 'Designer', '2014-08-01', '2022-08-31', 'Personal reasons'),
('E009', 'Rahul Singhania', 'rahul.singhania@example.com', 60000, 'Manager', '2015-09-01', null, null),
('E010', 'Komal Agarwal', 'komal.agarwal@example.com', 40000, 'Developer', '2016-10-01', '2022-02-28', 'Better opportunity');


#Adding dummy values to projects 
INSERT INTO Projects (event_name, start_date, types, budget, no_of_participants, duration, collection, total_expense) VALUES
('Project A', '2022-01-01', 'Conference', 500000, 100, 5, 600000, 400000),
('Project B', '2022-02-01', 'Workshop', 300000, 50, 3, null, 200000),
('Project C', '2022-03-01', 'Seminar', 200000, 30, 2, null, 150000),
('Project D', '2022-04-01', 'Exhibition', 800000, 200, 7, 900000, 700000),
('Project E', '2022-05-01', 'Hackathon', 400000, 80, 4, null, 300000),
('Project F', '2022-06-01', 'Training', 600000, 120, 6, 700000, 500000),
('Project G', '2022-07-01', 'Competition', 500000, 50, 2, null, 400000),
('Project H', '2022-08-01', 'Expo', 1000000, 300, 10, 1200000, 900000),
('Project I', '2022-09-01', 'Webinar', 100000, 200, 1, null, 80000),
('Project J', '2022-10-01', 'Symposium', 700000, 150, 8, 800000, 600000);

#Adding dummy values to ProjectPhotos
INSERT INTO ProjectPhotos (project_event_name, project_start_date, photo_url, caption) 
VALUES 
  ('Project A', '2022-01-01', 'https://example.com/photo1.jpg', 'Conference photo 1'),
  ('Project A', '2022-01-01', 'https://example.com/photo2.jpg', 'Conference photo 2'),
  ('Project B', '2022-02-01', 'https://example.com/photo3.jpg', 'Workshop photo 1'),
  ('Project C', '2022-03-01', 'https://example.com/photo4.jpg', NULL),
  ('Project D', '2022-04-01', 'https://example.com/photo5.jpg', 'Exhibition photo 1'),
  ('Project E', '2022-05-01', 'https://example.com/photo6.jpg', NULL),
  ('Project F', '2022-06-01', 'https://example.com/photo7.jpg', 'Training photo 1'),
  ('Project G', '2022-07-01', 'https://example.com/photo8.jpg', NULL),
  ('Project H', '2022-08-01', 'https://example.com/photo9.jpg', 'Expo photo 1'),
  ('Project I', '2022-09-01', 'https://example.com/photo10.jpg', NULL);
  
  
INSERT INTO ProjectPhotos (project_event_name, project_start_date, photo_url, caption)
VALUES
    ('Project A', '2022-01-01', 'E:/6th Sem/OneDrive - iitgn.ac.in/6th Sem/dbms/Assignment2/image2.jpg', 'Photo of project A'),
    ('Project A', '2022-01-01', 'E:/6th Sem/OneDrive - iitgn.ac.in/6th Sem/dbms/Assignment2/image1.jpg', 'Another photo of project A'),
    ('Project B', '2022-02-01', 'E:/6th Sem/OneDrive - iitgn.ac.in/6th Sem/dbms/Assignment2/image2.jpg', 'Photo of project B'),
    ('Project B', '2022-02-01', 'E:/6th Sem/OneDrive - iitgn.ac.in/6th Sem/dbms/Assignment2/image1.jpg', NULL);


#Adding dummy values to Venue
INSERT INTO Venue (venue_id, place, pincode, district, state) VALUES
('VEN001', 'Maharashtra Nagar', 400010, 'Mumbai', 'Maharashtra'),
('VEN002', 'Shalimar Bagh', 110088, 'North Delhi', 'Delhi'),
('VEN003', 'Park Street', 700016, 'Kolkata', 'West Bengal'),
('VEN004', 'Whitefield', 560066, 'Bangalore', 'Karnataka'),
('VEN005', 'Banjara Hills', 500034, 'Hyderabad', 'Telangana'),
('VEN006', 'Gomti Nagar', 226010, 'Lucknow', 'Uttar Pradesh'),
('VEN007', 'Alwarpet', 600018, 'Chennai', 'Tamil Nadu'),
('VEN008', 'Bodakdev', 380054, 'Ahmedabad', 'Gujarat'),
('VEN009', 'Race Course', 390007, 'Vadodara', 'Gujarat'),
('VEN010', 'Ravipuram', 682016, 'Kochi', 'Kerala');





#Adding dummy values to Volunteers
INSERT INTO Volunteers (email_id, name, phone_number, date_of_birth, gender) VALUES
('john.doe@example.com', 'John Doe', 9876543210, '1990-05-15', 'Male'),
('jane.doe@example.com', 'Jane Doe', 9876543211, '1992-08-25', 'Female'),
('rohit.sharma@example.com', 'Rohit Sharma', 9876543212, '1987-04-30', 'Male'),
('priya.rai@example.com', 'Priya Rai', 9876543213, '1995-11-20', 'Female'),
('amit.kumar@example.com', 'Amit Kumar', 9876543214, '1991-02-10', 'Male'),
('divya.mishra@example.com', 'Divya Mishra', 9876543215, '1993-07-05', 'Female'),
('rahul.gupta@example.com', 'Rahul Gupta', 9876543216, '1994-09-12', 'Male'),
('pooja.shah@example.com', 'Pooja Shah', 9876543217, '1996-12-18', 'Female'),
('avinash.singh@example.com', 'Avinash Singh', 9876543218, '1992-03-22', 'Male'),
('neha.patel@example.com', 'Neha Patel', 9876543219, '1997-06-08', 'Female');


#Adding dummy values to VillageProfile
INSERT INTO VillageProfile (pincode, name, no_of_beneficiaries, no_of_primary_health_center, no_of_primary_school, transport, infrastructure, major_occupation, technical_literacy, year) VALUES 
(380001, 'Ambawadi', 2500, 2, 3, 'Bus, Train', 'Electricity, Water, Roads', 'Agriculture', 'Basic Computer Knowledge', '2022-01-01'),
(380002, 'Vastrapur', 3500, 1, 4, 'Bus, Auto', 'Electricity, Water, Drainage', 'Education', 'Basic Computer Knowledge', '2022-01-01'),
(380003, 'Navrangpura', 4000, 3, 2, 'Bus, Train, Auto', 'Electricity, Water, Roads', 'Manufacturing', 'Advanced Computer Knowledge', '2022-01-01'),
(380004, 'Naranpura', 3000, 2, 3, 'Bus, Auto', 'Electricity, Water, Roads', 'Service', 'Basic Computer Knowledge', '2022-01-01'),
(380005, 'Satellite', 5000, 1, 4, 'Bus, Auto', 'Electricity, Water, Roads', 'Software Development', 'Advanced Computer Knowledge', '2022-01-01'),
(382330, 'Gandhinagar', 4500, 3, 2, 'Bus, Train', 'Electricity, Water, Roads', 'Agriculture', 'Basic Computer Knowledge', '2022-01-01'),
(382340, 'Kalol', 2000, 1, 4, 'Bus, Auto', 'Electricity, Water, Drainage', 'Education', 'Basic Computer Knowledge', '2022-01-01'),
(382345, 'Adalaj', 3000, 2, 3, 'Bus, Auto', 'Electricity, Water, Roads', 'Service', 'Basic Computer Knowledge', '2022-01-01'),
(382350, 'Dehgam', 4000, 3, 2, 'Bus, Auto', 'Electricity, Water, Roads', 'Manufacturing', 'Advanced Computer Knowledge', '2022-01-01'),
(382355, 'Vadsar', 3500, 1, 4, 'Bus, Auto', 'Electricity, Water, Roads', 'Software Development', 'Advanced Computer Knowledge', '2022-01-01');

#Adding dummy values to Goods
INSERT INTO Goods (event_name, start_date, item_name, quantity, amount)
VALUES 
  ('Project A', '2022-01-01', 'Laptop', 10, 100000),
  ('Project A', '2022-01-01', 'Projector', 2, 50000),
  ('Project B', '2022-02-01', 'Marker', 50, 1000),
  ('Project C', '2022-03-01', 'Notebook', 30, 500),
  ('Project D', '2022-04-01', 'Painting', 5, 1000000),
  ('Project E', '2022-05-01', 'Raspberry Pi', 20, 20000),
  ('Project F', '2022-06-01', 'Whiteboard', 2, 30000),
  ('Project G', '2022-07-01', 'Chess Set', 5, 5000),
  ('Project H', '2022-08-01', 'Microphone', 10, 50000),
  ('Project I', '2022-09-01', 'Webcam', 5, 20000);


#Adding dummy values to Trainers
INSERT INTO Trainers (email_id, fee, name, age, gender)
VALUES
('trainer1@gmail.com', 2000, 'Rajesh Kumar', 35, 'Male'),
('trainer2@gmail.com', 2500, 'Anjali Sharma', 28, 'Female'),
('trainer3@gmail.com', 1800, 'Vikram Singh', 42, 'Male'),
('trainer4@gmail.com', 3000, 'Sneha Patel', 31, 'Female'),
('trainer5@gmail.com', 2200, 'Gaurav Chauhan', 29, 'Male'),
('trainer6@gmail.com', 2700, 'Priya Gupta', 27, 'Female'),
('trainer7@gmail.com', 1900, 'Ravi Mishra', 36, 'Male'),
('trainer8@gmail.com', 2800, 'Neha Singh', 33, 'Female'),
('trainer9@gmail.com', 2400, 'Rahul Sharma', 30, 'Male'),
('trainer10@gmail.com', 3200, 'Meera Shah', 26, 'Female');

#Adding dummy values to ProjectExpense
INSERT INTO ProjectExpense (event_name, start_date, description, amount)
VALUES
    ('Project A', '2022-01-01', 'Catering expenses', 150000),
    ('Project A', '2022-01-01', 'Speaker fees', 200000),
    ('Project B', '2022-02-01', 'Venue rental', 100000),
    ('Project B', '2022-02-01', 'Equipment rental', 50000),
    ('Project C', '2022-03-01', 'Printing and design', 80000),
    ('Project C', '2022-03-01', 'Speaker fees', 70000),
    ('Project D', '2022-04-01', 'Shipping expenses', 150000),
    ('Project E', '2022-05-01', 'Prize money', 100000),
    ('Project F', '2022-06-01', 'Speaker fees', 300000),
    ('Project G', '2022-07-01', 'Marketing expenses', 50000);

#Adding dummy values to TrainerPhoneEntity
INSERT INTO TrainerPhoneEntity (email_id, phone_number)
VALUES
('trainer1@gmail.com', 9876543210),
('trainer1@gmail.com', 8765432109),
('trainer2@gmail.com', 7654321098),
('trainer2@gmail.com', 6543210987),
('trainer3@gmail.com', 5432109876),
('trainer4@gmail.com', 4321098765),
('trainer5@gmail.com', 3210987654),
('trainer6@gmail.com', 2109876543),
('trainer8@gmail.com', 1098765432),
('trainer10@gmail.com', 1234567890);


#Adding dummy values to BeneficiaryPhoneEntity
INSERT INTO BeneficiaryPhoneEntity (aadhar_id, phone_number)
VALUES
(123456789012, 9876543210),
(234567890123, 8765432109),
(345678901234, 7654321098),
(456789012345, 6543210987),
(567890123456, 5432109876),
(678901234567, 4321098765),
(789012345678, 3210987654),
(890123456789, 2109876543),
(901234567890, 1098765432),
(123450987654, 1234567890);


#Adding dummy values to EmployeePhoneEntity
INSERT INTO TeamPhone (employee_id, phone_number, location) VALUES
('E001', 9876543210, 'Delhi'),
('E001', 9898989898, 'Mumbai'),
('E002', 8765432109, 'Kolkata'),
('E003', 7894561230, 'Bangalore'),
('E003', 9865327410, 'Chennai'),
('E004', 9876543210, 'Pune'),
('E005', 8765432109, 'Hyderabad'),
('E006', 7894561230, 'Mumbai'),
('E007', 9865327410, 'Chennai'),
('E010', 9876543210, 'Delhi');


-- Relational Tables 

#Adding dummy values to Organize
INSERT INTO Organize (employee_id, event_name, start_date, role)
VALUES 
('E001', 'Project A', '2022-01-01', 'Manager'),
('E002', 'Project A', '2022-01-01', 'Developer'),
('E003', 'Project A', '2022-01-01', 'Developer'),
('E004', 'Project A', '2022-01-01', 'Designer'),
('E005', 'Project B', '2022-02-01', 'Manager'),
('E006', 'Project B', '2022-02-01', 'Developer'),
('E007', 'Project B', '2022-02-01', 'Developer'),
('E008', 'Project C', '2022-03-01', 'Designer'),
('E009', 'Project D', '2022-04-01', 'Manager'),
('E010', 'Project D', '2022-04-01', 'Developer'),
('E001', 'Project E', '2022-05-01', 'Manager'),
('E002', 'Project E', '2022-05-01', 'Developer'),
('E003', 'Project E', '2022-05-01', 'Developer'),
('E004', 'Project E', '2022-05-01', 'Designer'),
('E005', 'Project F', '2022-06-01', 'Manager'),
('E006', 'Project F', '2022-06-01', 'Developer'),
('E007', 'Project F', '2022-06-01', 'Developer'),
('E008', 'Project G', '2022-07-01', 'Designer'),
('E009', 'Project H', '2022-08-01', 'Manager'),
('E010', 'Project H', '2022-08-01', 'Developer'),
('E001', 'Project I', '2022-09-01', 'Manager'),
('E002', 'Project I', '2022-09-01', 'Developer'),
('E003', 'Project I', '2022-09-01', 'Developer'),
('E004', 'Project I', '2022-09-01', 'Designer'),
('E005', 'Project J', '2022-10-01', 'Manager'),
('E006', 'Project J', '2022-10-01', 'Developer'),
('E007', 'Project J', '2022-10-01', 'Developer');

#Adding dummy values to Sponsors
INSERT INTO sponsors (email_id, event_name, start_date)
VALUES ('abc@gmail.com', 'Project B', '2022-02-01'),
       ('def@gmail.com', 'Project B', '2022-02-01'),
       ('ghi@gmail.com', 'Project B', '2022-02-01'),
       ('jkl@gmail.com', 'Project B', '2022-02-01'),
       ('mno@gmail.com', 'Project B', '2022-02-01'),
       ('pqr@gmail.com', 'Project B', '2022-02-01'),
       ('stu@gmail.com', 'Project B', '2022-02-01'),
       ('vwx@gmail.com', 'Project B', '2022-02-01'),
       ('yz@gmail.com', 'Project B', '2022-02-01'),
       ('abc1@gmail.com', 'Project B', '2022-02-01'),
		('abc@gmail.com', 'Project C', '2022-03-01'),
       ('def@gmail.com', 'Project C', '2022-03-01'),
       ('ghi@gmail.com', 'Project C', '2022-03-01'),
       ('jkl@gmail.com', 'Project C', '2022-03-01'),
       ('mno@gmail.com', 'Project C', '2022-03-01'),
       ('pqr@gmail.com', 'Project C', '2022-03-01'),
       ('stu@gmail.com', 'Project C', '2022-03-01'),
       ('vwx@gmail.com', 'Project C', '2022-03-01'),
       ('yz@gmail.com', 'Project C', '2022-03-01'),
       ('abc1@gmail.com', 'Project C', '2022-03-01'),
		('abc@gmail.com', 'Project F', '2022-06-01'),
       ('def@gmail.com', 'Project F', '2022-06-01'),
       ('ghi@gmail.com', 'Project F', '2022-06-01'),
       ('jkl@gmail.com', 'Project F', '2022-06-01'),
       ('mno@gmail.com', 'Project F', '2022-06-01'),
       ('pqr@gmail.com', 'Project F', '2022-06-01'),
       ('stu@gmail.com', 'Project F', '2022-06-01'),
       ('vwx@gmail.com', 'Project F', '2022-06-01'),
       ('yz@gmail.com', 'Project F', '2022-06-01'),
       ('abc1@gmail.com', 'Project F', '2022-06-01');

#Adding dummy values to Volunteering
INSERT INTO volunteering (email_id, event_name, start_date) VALUES
('john.doe@example.com', 'Project A', '2022-01-01'),
('john.doe@example.com', 'Project D', '2022-04-01'),
('john.doe@example.com', 'Project E', '2022-05-01'),
('jane.doe@example.com', 'Project B', '2022-02-01'),
('jane.doe@example.com', 'Project C', '2022-03-01'),
('jane.doe@example.com', 'Project G', '2022-07-01'),
('rohit.sharma@example.com', 'Project D', '2022-04-01'),
('rohit.sharma@example.com', 'Project E', '2022-05-01'),
('rohit.sharma@example.com', 'Project H', '2022-08-01'),
('priya.rai@example.com', 'Project A', '2022-01-01'),
('priya.rai@example.com', 'Project B', '2022-02-01'),
('amit.kumar@example.com', 'Project A', '2022-01-01'),
('amit.kumar@example.com', 'Project F', '2022-06-01'),
('divya.mishra@example.com', 'Project H', '2022-08-01'),
('rahul.gupta@example.com', 'Project C', '2022-03-01'),
('pooja.shah@example.com', 'Project B', '2022-02-01'),
('avinash.singh@example.com', 'Project G', '2022-07-01'),
('neha.patel@example.com', 'Project J', '2022-10-01');

#Adding dummy values to HeldAt
INSERT INTO HeldAt (venue_id, event_name, start_date)
VALUES
('VEN001', 'Project A', '2022-01-01'),
('VEN002', 'Project B', '2022-02-01'),
('VEN003', 'Project C', '2022-03-01'),
('VEN004', 'Project D', '2022-04-01'),
('VEN005', 'Project E', '2022-05-01'),
('VEN006', 'Project F', '2022-06-01'),
('VEN007', 'Project G', '2022-07-01'),
('VEN008', 'Project H', '2022-08-01'),
('VEN009', 'Project I', '2022-09-01'),
('VEN010', 'Project J', '2022-10-01');



#Adding dummy values to trains
INSERT INTO trains (email_id, event_name, start_date)
VALUES
('trainer1@gmail.com', 'Project A', '2022-01-01'),
('trainer2@gmail.com', 'Project A', '2022-01-01'),
('trainer3@gmail.com', 'Project B', '2022-02-01'),
('trainer4@gmail.com', 'Project B', '2022-02-01'),
('trainer5@gmail.com', 'Project C', '2022-03-01'),
('trainer6@gmail.com', 'Project C', '2022-03-01'),
('trainer7@gmail.com', 'Project D', '2022-04-01'),
('trainer8@gmail.com', 'Project D', '2022-04-01'),
('trainer9@gmail.com', 'Project E', '2022-05-01'),
('trainer10@gmail.com', 'Project F', '2022-06-01'),
('trainer1@gmail.com', 'Project G', '2022-07-01'),
('trainer2@gmail.com', 'Project G', '2022-07-01'),
('trainer3@gmail.com', 'Project H', '2022-08-01'),
('trainer4@gmail.com', 'Project H', '2022-08-01'),
('trainer5@gmail.com', 'Project I', '2022-09-01'),
('trainer6@gmail.com', 'Project I', '2022-09-01'),
('trainer7@gmail.com', 'Project J', '2022-10-01'),
('trainer8@gmail.com', 'Project J', '2022-10-01');



#Adding dummy values to trains
INSERT INTO participants (aadhar_id, event_name, start_date)
VALUES
(123456789012, 'Project A', '2022-01-01'),
(234567890123, 'Project A', '2022-01-01'),
(345678901234, 'Project A', '2022-01-01'),
(456789012345, 'Project B', '2022-02-01'),
(567890123456, 'Project B', '2022-02-01'),
(678901234567, 'Project C', '2022-03-01'),
(789012345678, 'Project D', '2022-04-01'),
(890123456789, 'Project E', '2022-05-01'),
(901234567890, 'Project F', '2022-06-01'),
(123450987654, 'Project G', '2022-07-01'),
(234567890123, 'Project H', '2022-08-01'),
(345678901234, 'Project H', '2022-08-01'),
(456789012345, 'Project H', '2022-08-01'),
(567890123456, 'Project I', '2022-09-01'),
(678901234567, 'Project J', '2022-10-01'),
(789012345678, 'Project J', '2022-10-01'),
(123456789012, 'Project J', '2022-10-01'),
(890123456789, 'Project J', '2022-10-01');


#Adding dummy values to TrainerBeneficiary
INSERT INTO TrainerBeneficiary (aadhar_id, email_id) VALUES
(123456789012, 'trainer1@gmail.com'),
(234567890123, 'trainer9@gmail.com'),
(456789012345, 'trainer5@gmail.com'),
(678901234567, 'trainer3@gmail.com'),
(890123456789, 'trainer4@gmail.com'),
(123450987654, 'trainer7@gmail.com');


#Adding dummy values to assessment
INSERT INTO assessment (aadhar_id, event_name, start_date, Date, present_or_absent)
VALUES
(123456789012, 'Project A', '2022-01-01', '2022-01-01', 'Present'),
(234567890123, 'Project A', '2022-01-01', '2022-01-01', 'Absent'),
(345678901234, 'Project B', '2022-02-01', '2022-02-01', 'Present'),
(456789012345, 'Project B', '2022-02-01', '2022-02-01', 'Absent'),
(567890123456, 'Project C', '2022-03-01', '2022-03-01', 'Present'),
(678901234567, 'Project D', '2022-04-01', '2022-04-01', 'Present'),
(789012345678, 'Project D', '2022-04-01', '2022-04-01', 'Absent'),
(890123456789, 'Project E', '2022-05-01', '2022-05-01', 'Absent'),
(901234567890, 'Project E', '2022-05-01', '2022-05-01', 'Present'),
(123450987654, 'Project F', '2022-06-01', '2022-06-01', 'Present');



#Adding dummy values to belongs
INSERT INTO belongs (aadhar_id, pincode)
VALUES 
(123456789012, 380002),
(234567890123, 380005),
(345678901234, 380002),
(456789012345, 380004),
(567890123456, 382330),
(678901234567, 382350),
(789012345678, 382340),
(890123456789, 380002),
(901234567890, 382340),
(123450987654, 382330);


-- All Entity sets and Relational Table Populated --


-- Indexing --

-- select * 
-- from Beneficiary 
-- where name = 'Amit';

-- select * 
-- from Beneficiary 
-- where name = "Amit" 
-- and gender = "Male";


-- select * 
-- from Beneficiary
-- where name = "Amit" and
-- date_of_birth 
-- between '1990-01-01' 
-- and '2000-12-31';

-- create index bene_name_index on Beneficiary (name);


-- -- Indexing Ends --

