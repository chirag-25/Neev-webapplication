create database login_auth2;

use login_auth2;

create table admin_password(
	EmployeeID varchar(8),
    EmployeePassword varchar(64)
);

create table staff_password(
	EmployeeID varchar(8),
    EmployeePassword varchar(64)
);

insert into admin_password(EmployeeID,EmployeePassword) 
values ("20110052","$2b$12$WM7Kx22qnkTjYVAAtpbYB.zgfmzHIO/OSwluCvTJhhtGsnLOVwuge");

insert into staff_password(EmployeeID,EmployeePassword)
values ("20110056","$2b$12$BYo0FKv92IMLuUWtMXiiAeL1aDGtgdsBcW.Q9rlqD3ZOE1.URjjQ6");

select * from admin_password;

select * from staff_password;