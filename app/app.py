from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import yaml
from datetime import date


app=Flask(__name__)

# Configure the database
db = yaml.load(open('db.yaml'), Loader=yaml.Loader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route("/")
def home():
    return render_template("home.html")
    # return render_template("admin/volunteers.html")

@app.route("/login", methods=['GET','POST'])
def login():
    if(request.method=='POST'):
        employee_form=request.form
        print(employee_form)
    return render_template("admin/login.html")

@app.route("/admin")
def admin():
    return render_template("admin/dashboard.html")

@app.route("/admin/funding")
def funding():
    return render_template("admin/funding.html")

@app.route("/admin/trainers", methods=['GET','POST'])
def trainers():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Trainers")

    if result_value > 0:
        userDetails = cur.fetchall()

    # Adding trainers (done)
    if (request.method == 'POST'):
        if request.form['signal'] == 'addUser':
            print(request.form)
            print("addDetails filled!")

            name = request.form['name']
            email_id = request.form['email_id']
            phoneNumber = request.form['phoneNumber']
            gender = request.form['gender']
            age = request.form['age']
            fee = request.form['fee']
            projectEventName = request.form['projectEventName']
            beneficiaryAadharId = request.form['beneficiaryAadharId']
            beneficiaryName = request.form['beneficiaryName']

            print(name)


            # project = request.form['']

            add_query = f"INSERT INTO Trainers (email_id, fee, name, age, gender) "
            add_query = add_query + f"VALUES (\'{email_id}\', \'{fee}\', \'{name}\', \'{age}\', \'{gender}\');"
            print(add_query)

            exec_query = cur.execute(add_query)
            mysql.connection.commit()

            return redirect('/admin/trainers')


        # editing trainers (done)
        elif request.form['signal'] == 'editUser':
            name = request.form['name']
            email_id = request.form['email_id']
            phoneNumber = request.form['phoneNumber']
            gender = request.form['gender']
            age = request.form['age']
            fee = request.form['fee']
            projectEventName = request.form['projectEventName']
            beneficiaryAadharId = request.form['beneficiaryAadharId']
            beneficiaryName = request.form['beneficiaryName']

            # updated based on email_id
            edit_query = f"UPDATE Trainers "
            edit_query = edit_query + f"SET email_id = \'{email_id}\', fee = \'{fee}\', name = \'{name}\', age = \'{age}\', gender = \'{gender}\'"
            edit_query = edit_query + f"WHERE email_id = \'{email_id}\';"
            print(edit_query)

            exec_query = cur.execute(edit_query)
            mysql.connection.commit()
            return redirect('/admin/trainers')
            print("edit")

        # delete the trainer (done)
        elif request.form['signal'] == 'delete':
            print("delete filled!")
            email_id = request.form['email_id']

            # delete operation considering event_name and start_date
            delete_query = f"DELETE FROM Trainers WHERE email_id = \'{email_id}\';"

            print(delete_query)

            exec_query = cur.execute(delete_query)
            mysql.connection.commit()
            return redirect('/admin/trainers')


    return render_template("admin/trainers.html", userDetails=userDetails)



@app.route("/admin/village_profile", methods=['POST', 'GET'])
def village_profile():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM VillageProfile")

    if result_value > 0:
        userDetails = cur.fetchall()

    # Adding village profile (deal with the year variable)
    if (request.method == 'POST'):
        if request.form['signal'] == 'addUser':
            print(request.form)
            print("addDetails filled!")

            pinCode = request.form['pinCode']
            name = request.form['name']
            noOfBeneficiaries = request.form['noOfBeneficiaries']
            noOfHealthCenters = request.form['noOfHealthCenters']
            noOfSchools = request.form['noOfSchools']
            transport = request.form['transport']
            infrastructure = request.form['infrastructure']
            occupation = request.form['occupation']
            technical_literacy = request.form['technical_literacy']
            year = request.form['year']
            beneficiaryAadharId = request.form['beneficiaryAadharId']
            beneficiaryName = request.form['beneficiaryName']

            print(pinCode)


            # project = request.form['']

            add_query = f"INSERT INTO VillageProfile (pincode, name, no_of_beneficiaries, no_of_primary_health_center, no_of_primary_school, transport, infrastructure, major_occupation, technical_literacy, year) "
            add_query = add_query + f"VALUES (\'{pinCode}\', \'{name}\', \'{noOfBeneficiaries}\', \'{noOfHealthCenters}\', \'{noOfSchools}\', \'{transport}\', \'{infrastructure}\', \'{occupation}\', \'{technical_literacy}\', \'{year}\');"
            print(add_query)

            exec_query = cur.execute(add_query)
            mysql.connection.commit()

            return redirect('/admin/village_profile')


        # editing village profile (deal with the year variable)
        elif request.form['signal'] == 'editUser':
            pinCode = request.form['pinCode']
            name = request.form['name']
            noOfBeneficiaries = request.form['noOfBeneficiaries']
            noOfHealthCenters = request.form['noOfHealthCenters']
            noOfSchools = request.form['noOfSchools']
            transport = request.form['transport']
            infrastructure = request.form['infrastructure']
            occupation = request.form['occupation']
            technical_literacy = request.form['technical_literacy']
            year = request.form['year']
            beneficiaryAadharId = request.form['beneficiaryAadharId']
            beneficiaryName = request.form['beneficiaryName']


            # updated based on pincode
            edit_query = f"UPDATE VillageProfile "
            edit_query = edit_query + f"SET pincode = \'{pinCode}\', name = \'{name}\', no_of_beneficiaries = \'{noOfBeneficiaries}\', no_of_primary_health_center = \'{noOfHealthCenters}\', no_of_primary_school = \'{noOfSchools}\', transport = \'{transport}\', infrastructure = \'{infrastructure}\', major_occupation = \'{occupation}\', technical_literacy = \'{technical_literacy}\', year = \'{year}\'"
            edit_query = edit_query + f"WHERE pincode = \'{pinCode}\';"
            print(edit_query)

            exec_query = cur.execute(edit_query)
            mysql.connection.commit()
            return redirect('/admin/village_profile')
            print("edit")

        # delete the village profile (completed)
        elif request.form['signal'] == 'delete':
            print("delete filled!")
            pinCode = request.form['pinCode']

            # delete operation considering event_name and start_date
            delete_query = f"DELETE FROM VillageProfile WHERE pincode = \'{pinCode}\';"

            print(delete_query)

            exec_query = cur.execute(delete_query)
            mysql.connection.commit()
            return redirect('/admin/village_profile')        


    return render_template("admin/village_profile.html", userDetails=userDetails)


@app.route("/admin/projects", methods=['POST', 'GET'])
def projects():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Projects")

    if result_value > 0:
        userDetails = cur.fetchall()

    # Adding volunteer
    if (request.method == 'POST'):
        if request.form['signal'] == 'addProject':
            print(request.form)
            print("addDetails filled!")

            event_name = request.form['event_name']
            date = request.form['date']
            budget = request.form['budget']
            participants = request.form['participants']
            duration = request.form['duration']
            collection = request.form['collection']
            expense = request.form['expense']
            venue_id = request.form['venue_id']
            aadhar = request.form['aadhar']
            volunteer_email_id = request.form['volunteer_email_id']
            donor_email_id = request.form['donor_email_id']
            trainer_email_id = request.form['trainer_email_id']
            EmployID = request.form['EmployID']
            Types = request.form['types']

            print(event_name)

            add_query = f"INSERT INTO Projects (event_name, start_date, types, budget, no_of_participants, duration, collection, total_expense) "
            add_query = add_query + f"VALUES (\'{event_name}\', \'{date}\', \'{Types}\', \'{budget}\', \'{participants}\', \'{duration}\', \'{collection}\', \'{expense}\');"
            print(add_query)

            exec_query = cur.execute(add_query)
            mysql.connection.commit()

            return redirect('/admin/projects')

        # editing user info
        elif request.form['signal'] == 'editProject':
            event_name = request.form['event_name']
            date = request.form['date']
            budget = request.form['budget']
            participants = request.form['participants']
            duration = request.form['duration']
            collection = request.form['collection']
            expense = request.form['expense']
            venue_id = request.form['venue_id']
            aadhar = request.form['aadhar']
            volunteer_email_id = request.form['volunteer_email_id']
            donor_email_id = request.form['donor_email_id']
            trainer_email_id = request.form['trainer_email_id']
            EmployID = request.form['EmployID']
            Types = request.form['types']


            # updated based on event_name and start_date
            edit_query = f"UPDATE Projects "
            edit_query = edit_query + f"SET event_name = \'{event_name}\', start_date = \'{date}\', types = \'{Types}\', budget = \'{budget}\', no_of_participants = \'{participants}\', duration = \'{duration}\', collection = \'{collection}\', total_expense = \'{expense}\'"
            edit_query = edit_query + f"WHERE event_name = \'{event_name}\' and start_date = \'{date}\';"
            print(edit_query)

            exec_query = cur.execute(edit_query)
            mysql.connection.commit()
            return redirect('/admin/projects')
            print("edit")

        # delete the user info
        elif request.form['signal'] == 'delete':
            print("delete filled!")
            event_name = request.form['event_name']
            start_date = request.form['date']

            # delete operation considering event_name and start_date
            delete_query = f"DELETE FROM Projects WHERE event_name = \'{event_name}\' and start_date = \'{start_date}\';"

            print(delete_query)

            exec_query = cur.execute(delete_query)
            mysql.connection.commit()
            return redirect('/admin/projects')        


    
    return render_template("admin/projects.html", userDetails=userDetails)


@app.route("/admin/volunteers", methods = ['POST', 'GET'])
def volunteers():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Volunteers")

    if result_value > 0:
        userDetails = cur.fetchall()

    # Adding volunteer
    if (request.method == 'POST'):
        if request.form['signal'] == 'addUser':
            print(request.form)
            print("addDetails filled!")

            volunteers_name = request.form['name']
            email = request.form['email']
            date_of_birth = request.form['dob']
            gender = request.form['gender']
            phone = request.form['phone']

            print(volunteers_name)


            # project = request.form['']

            add_query = f"INSERT INTO Volunteers (email_id, name, phone_number, date_of_birth, gender) "
            add_query = add_query + f"VALUES (\'{email}\', \'{volunteers_name}\', \'{phone}\', \'{date_of_birth}\', \'{gender}\')"
            print(add_query)

            exec_query = cur.execute(add_query)
            mysql.connection.commit()

            return redirect('/admin/volunteers')

        # editing user info
        elif request.form['signal'] == 'editUser':
            volunteers_name = request.form['volunteer_name']
            email = request.form['email']
            date_of_birth = request.form['dob']
            gender = request.form['gender']
            phone = request.form['phone']

            edit_query = f"UPDATE Volunteers "
            edit_query = edit_query + f"SET name = \'{volunteers_name}\', email_id = \'{email}\', date_of_birth = \'{date_of_birth}\', gender = \'{gender}\', phone_number = \'{phone}\'"
            edit_query = edit_query + f"WHERE email_id = \'{email}\';"
            print(edit_query)

            exec_query = cur.execute(edit_query)
            mysql.connection.commit()
            return redirect('/admin/volunteers')
            print("edit")

        # delete the user info
        elif request.form['signal'] == 'delete':
            print("delete filled!")
            email = request.form['email']
            delete_query = f"DELETE FROM Volunteers WHERE email_id = \'{email}\'"

            print(delete_query)

            exec_query = cur.execute(delete_query)
            mysql.connection.commit()
            return redirect('/admin/volunteers')

    return render_template("admin/volunteers.html", userDetails=userDetails)


@app.route("/admin/user",methods=['POST','GET'])
def user():
    if(request.method=='POST'):
        print(request.json)
        form_data=request.json
        if(form_data['signal']=='search'):
            print("this is search query")
        elif(form_data['signal']=='editUser'):
            print("this is edit query")  
        elif(form_data['signal']=='addUser'):
            print("add new data")     
    return render_template('admin/user.html')

if __name__=='__main__':
    app.run(debug=True)