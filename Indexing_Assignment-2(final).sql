create database Neev3;
use NEEV3;


create table Beneficiary (
aadhar_id bigint primary key,
name varchar(50) not null,
date_of_birth date not null,
gender varchar(20) not null,
marital_status varchar(10) not null,
education varchar(50) not null,
photo longblob default null,
employed varchar(20) default null,
photo_caption VARCHAR(255) DEFAULT NULL
);

-- Indexing on Beneficiary --
CREATE INDEX bene_name_index
ON Beneficiary (name);

DROP INDEX bene_aadhar_index ON Beneficiary;


select * 
from Beneficiary 
where name = 'Amit';

select * 
from Beneficiary 
where name = "Amit" 
and gender = "Male";

select * 
from Beneficiary
where name = "Amit" and
date_of_birth 
between '1990-01-01' 
and '2000-12-31';


-- Indexing on Beneficiary Ends --




create table Volunteers (
email_id varchar(50) primary key,
name varchar(50) not null,
phone_number bigint not null,
date_of_birth date default null,
gender enum('Male', 'Female', 'Others') not null
);


-- Indexing on Volunteers --
CREATE INDEX volunteer_name_index
ON Volunteers (name);

DROP INDEX volunteer_name_index ON Volunteers;


select * 
from Volunteers 
where name = 'Asha';

select * 
from Volunteers 
where name = "Asha" 
and gender = "Female";

select * 
from Volunteers
where name = "Asha" and
date_of_birth 
between '1990-01-01' 
and '2000-12-31';

-- Indexing on Volunteers Ends --