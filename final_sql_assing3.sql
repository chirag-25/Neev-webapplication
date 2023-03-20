create database NEEV2;
use NEEV2;

create table admin_password(
	EmployeeID varchar(8) primary key,
    EmployeePassword varchar(64)
);

create table staff_password(
	EmployeeID varchar(8) primary key,
    EmployeePassword varchar(64)
);

insert into admin_password(EmployeeID,EmployeePassword)
values ("16","GFfK65EW785wzCKaAA");

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