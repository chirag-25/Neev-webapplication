# Neev Web app
## Initial Setup

Clone this project

Run this on terminal
```bash
pip3 install -r requirements.txt
```
Change the password in db.yaml to that of your MySQL's password

Run the database.sql file in your MySQL database. it will create the NEEV2 database 

Go to app folder by
```bash
cd app
```

Run the application by executing the command 
``` bash
python3 app.py
```

Click on login link and give the below details to login as admin

We have created the admin user in our database with 

```text
id = 1
password: GFfK65EW785wzCKaAA
```

This admin can only add other members. For other members option for adding the new member is denied



