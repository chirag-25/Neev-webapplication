from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import yaml

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

@app.route("/login",methods=['GET','POST'])
def login():
    if(request.method=='POST'):
        employee_form=request.form
        print(employee_form)
    return render_template("admin/login.html")

@app.route("/admin")
def admin():
    return render_template("admin/dashboard.html")


@app.route("/admin/user", methods=['POST', 'GET'])
def user():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Beneficiary")

    if result_value > 0:
        userDetails = cur.fetchall()


    # Generate the user profile details
    profile_details = []
    for user in userDetails:
        user_profile = {'aadhar':user[0], 'name':user[1], 'dob':user[2], 'gender':user[3], 'martial':user[4], 'education':user[5], 'photo':user[6], 'employed':user[7], 'photo_caption':user[8]}
        calculate_age_query = f"SELECT TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) FROM Beneficiary WHERE aadhar_id = \'{user[0]}\'"
        extract_village_query = f"SELECT pincode, name FROM VillageProfile WHERE pincode = (SELECT pincode FROM belongs WHERE aadhar_id = \'{user[0]}\')"
        extract_enrolled_projects_query = f"SELECT * FROM participants WHERE aadhar_id = \'{user[0]}\'"
        extract_phone_query = f"SELECT phone_number FROM BeneficiaryPhoneEntity WHERE aadhar_id = \'{user[0]}\'"

        calculate_age = cur.execute(calculate_age_query)
        calculate_age = cur.fetchall()

        extract_village = cur.execute(extract_village_query)
        extract_village = cur.fetchall()

        extract_enrolled_projects = cur.execute(extract_enrolled_projects_query)
        extract_enrolled_projects = cur.fetchall()

        extract_phone = cur.execute(extract_phone_query)
        extract_phone = cur.fetchall()

        if len(calculate_age) > 0:
            user_profile['age'] = calculate_age[0][0]
        else:
            user_profile['age'] = 'NA'

        if len(extract_village) > 0:
            user_profile['village'] = extract_village[0][1]
            user_profile['pincode'] = extract_village[0][0]
        else:
            user_profile['village'] = 'NA'
            user_profile['pincode'] = 'NA'

        if len(extract_enrolled_projects) > 0:
            user_profile['projects'] = extract_enrolled_projects
        else:
            user_profile['projects'] = ()

        if len(extract_phone) > 0:
            user_profile['phone'] = extract_phone[0][0]
        else:
            user_profile['phone'] = 'NA'


        profile_details.append(user_profile)

    # Generate projects list
    projects_query = f"SELECT event_name FROM Projects"
    projects_query = cur.execute(projects_query)
    projects = cur.fetchall()

    # Generate village list
    village_query = f"SELECT name FROM VillageProfile"
    village_query = cur.execute(village_query)
    villages = cur.fetchall()

    # Generate education list
    education_list_query = f"SELECT DISTINCT education FROM Beneficiary"
    education_list_query_query = cur.execute(education_list_query)
    education_list = cur.fetchall()

    if (request.method == 'POST'):
        if request.form['signal'] == 'search':
            name = request.form['name']
            aadhar = request.form['aadhar']
            dob = request.form['dob']
            age = request.form['age']
            employed = request.form['employed']
            gender = request.form['gender']
            martial = request.form['martial']
            education = request.form['education']
            village = request.form['village']
            project = request.form['project']
            phone_number = request.form['phone_number']

            # First extract all the beneficiaries from table Beneficiary
            where_query = f"SELECT aadhar_id FROM Beneficiary "
            flag = False
            if name != '':
                if flag == False:
                    where_query += f"WHERE name = \"{name}\""
                else:
                    where_query += f"name = \"{name}\""
                flag = True

            if aadhar != '':
                if flag == False:
                    where_query += f"WHERE aadhar_id = \'{aadhar}\'"
                else:
                    where_query += f" AND aadhar_id = \'{aadhar}\'"
                flag = True

            if dob != '':
                if flag == False:
                    where_query += f"WHERE date_of_birth = \'{dob}\'"
                else:
                    where_query += f" AND date_of_birth = \'{dob}\'"
                flag = True

            if age != '':
                if flag == False:
                    where_query += f"WHERE TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) = \'{age}\'"
                else:
                    where_query += f" AND TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) = \'{age}\'"
                flag = True

            if employed != '':
                if flag == False:
                    where_query += f"WHERE employed = \'{employed}\'"
                else:
                    where_query += f" AND employed = \'{employed}\'"
                flag = True

            if gender != '':
                if flag == False:
                    where_query += f"WHERE gender = \'{gender}\'"
                else:
                    where_query += f" AND gender = \'{gender}\'"
                flag = True

            if martial != '':
                if flag == False:
                    where_query += f"WHERE marital_status = \'{martial}\'"
                else:
                    where_query += f" AND marital_status = \'{martial}\'"
                flag = True

            if education != '':
                if flag == False:
                    where_query += f"WHERE education = \'{education}\'"
                else:
                    where_query += f" AND education = \'{education}\'"
                flag = True

            # Combine the results of the above query with the results of the village and project search
            if village != '':
                if flag == False:
                    where_query += f"WHERE aadhar_id IN (SELECT aadhar_id FROM belongs WHERE pincode = (SELECT pincode FROM VillageProfile WHERE name = \"{village}\"))"
                else:
                    where_query += f" AND aadhar_id IN (SELECT aadhar_id FROM belongs WHERE pincode = (SELECT pincode FROM VillageProfile WHERE name = \"{village}\"))"
                flag = True
            if project != '':
                if flag == False:
                    where_query += f"WHERE aadhar_id IN (SELECT aadhar_id FROM participants WHERE event_name = \"{project}\")"
                else:
                    where_query += f" AND aadhar_id IN (SELECT aadhar_id FROM participants WHERE event_name = \"{project}\")"
                flag = True

            # Combine the results of the above query with the results of the phone number search
            if phone_number != '':
                if flag == False:
                    where_query += f"WHERE aadhar_id IN (SELECT aadhar_id FROM BeneficiaryPhoneEntity WHERE phone_number = \"{phone_number}\")"
                else:
                    where_query += f" AND aadhar_id IN (SELECT aadhar_id FROM BeneficiaryPhoneEntity WHERE phone_number = \"{phone_number}\")"
                flag = True

            exec_query = cur.execute(where_query)
            search_results = cur.fetchall()

            updated_profile_details = []
            for user in profile_details:
                for result in search_results:
                    if user['aadhar'] == result[0]:
                        updated_profile_details.append(user)
            profile_details = updated_profile_details

        elif request.form['signal'] == 'add':
            aadhar = request.form['aadhar']
            name = request.form['name']
            dob = request.form['dob']
            education = request.form['education']
            martial = request.form['martial']
            gender = request.form['gender']
            employed = request.form['employed']
            phone_number = request.form['phone_number']
            village = request.form['village']
            project = request.form['project']

            add_query = f"INSERT INTO Beneficiary (aadhar_id, name, date_of_birth, gender, marital_status, education, photo, employed, photo_caption) "
            add_query = add_query + f"VALUES ({aadhar}, \"{name}\", \'{dob}\', \'{gender}\', \'{martial}\', \'{education}\', NULL, \"{employed}\", NULL)"
            exec_query = cur.execute(add_query)
            mysql.connection.commit()

            # Add phone_number query
            add_phone_query = f"INSERT INTO BeneficiaryPhoneEntity (aadhar_id, phone_number) "
            add_phone_query = add_phone_query + f"VALUES ({aadhar}, \"{phone_number}\")"
            exec_query = cur.execute(add_phone_query)
            mysql.connection.commit()

            # Add village query
            add_village_query = f"INSERT INTO belongs (aadhar_id, pincode) "
            add_village_query = add_village_query + f"VALUES ({aadhar}, (SELECT pincode FROM VillageProfile WHERE name = \"{village}\"))"
            exec_query = cur.execute(add_village_query)
            mysql.connection.commit()

            # Add project query
            add_project_query = f"INSERT INTO participants (aadhar_id, event_name, start_date) "
            # assumption is taken here that beneficiary can only participate in current year's project
            add_project_query = add_project_query + f"VALUES ({aadhar}, \"{project}\", (SELECT start_date FROM Projects WHERE event_name = \"{project}\" AND YEAR(start_date) = YEAR(CURDATE())))"
            exec_query = cur.execute(add_project_query)
            mysql.connection.commit()

            return redirect('/admin/user')

        elif request.form['signal'] == 'edit':
            aadhar = request.form['aadhar']
            name = request.form['name']
            dob = request.form['dob']
            education = request.form['education']
            martial = request.form['martial']
            gender = request.form['gender']
            employed = request.form['employed']
            phone_number = request.form['phone_number']
            village = request.form['village']
            project = request.form['project']

            edit_query = f"UPDATE Beneficiary "
            edit_query = edit_query + f"SET name = \'{name}\', date_of_birth = \'{dob}\', gender = \'{gender}\', marital_status = \'{martial}\', education = \'{education}\', photo = NULL, employed = \"{employed}\", photo_caption = NULL "
            edit_query = edit_query + f"WHERE aadhar_id = {aadhar}"
            exec_query = cur.execute(edit_query)
            mysql.connection.commit()

            # Update phone_number, village and project if provided
            if phone_number != '':
                add_phone_query = f"INSERT INTO BeneficiaryPhoneEntity (aadhar_id, phone_number) "
                add_phone_query = add_phone_query + f"VALUES ({aadhar}, \"{phone_number}\")"
                exec_query = cur.execute(add_phone_query)
                mysql.connection.commit()

            if village != '':
                edit_village_query = f"UPDATE belongs "
                edit_village_query = edit_village_query + f"SET pincode = (SELECT pincode FROM VillageProfile WHERE name = \"{village}\") "
                edit_village_query = edit_village_query + f"WHERE aadhar_id = {aadhar}"
                exec_query = cur.execute(edit_village_query)
                mysql.connection.commit()

            if project != '':
                add_project_query = f"INSERT INTO participants (aadhar_id, event_name, start_date) "
                # assumption is taken here that beneficiary can only participate in current year's project
                add_project_query = add_project_query + f"VALUES ({aadhar}, \"{project}\", (SELECT start_date FROM Projects WHERE event_name = \"{project}\" AND YEAR(start_date) = YEAR(CURDATE())))"
                exec_query = cur.execute(add_project_query)
                mysql.connection.commit()

            return redirect('/admin/user')

        elif request.form['signal'] == 'delete':
            aadhar = request.form['aadhar']
            delete_query = f"DELETE FROM Beneficiary WHERE aadhar_id = {aadhar}"

            exec_query = cur.execute(delete_query)
            mysql.connection.commit()
            return redirect('/admin/user')

    return render_template('admin/user.html', searchResults=tuple(), profile_details=profile_details, projects=projects, villages=villages, education_list=education_list)
    # return render_template('admin/user.html')

@app.route("/admin/volunteers", methods = ['POST', 'GET'])
def volunteers():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Volunteers")

    if result_value > 0:
        userDetails = cur.fetchall()

    # Generate the user profile details
    profile_details = []
    for user in userDetails:
        # (email_id, name, phone_number, date_of_birth, gender)
        # INSERT INTO volunteering(email_id, event_name, start_date)
        user_profile = {'email_id': user[0], 'name': user[1], 'phone_number': user[2], 'date_of_birth': user[3], 'gender': user[4]}
        calculate_age_query = f"SELECT TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) FROM Volunteers WHERE email_id = \'{user[0]}\'"
        extract_enrolled_projects_query = f"SELECT * FROM volunteering WHERE email_id = \'{user[0]}\'"

        calculate_age = cur.execute(calculate_age_query)
        calculate_age = cur.fetchall()

        extract_enrolled_projects = cur.execute(extract_enrolled_projects_query)
        extract_enrolled_projects = cur.fetchall()

        if len(calculate_age) > 0:
            user_profile['age'] = calculate_age[0][0]
        else:
            user_profile['age'] = 'NA'

        if len(extract_enrolled_projects) > 0:
            user_profile['projects'] = extract_enrolled_projects
        else:
            user_profile['projects'] = ()

        profile_details.append(user_profile)

    # Generate projects list
    projects_query = f"SELECT event_name FROM Projects"
    projects_query = cur.execute(projects_query)
    projects = cur.fetchall()

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

        elif request.form['signal'] == 'delete':
            print("delete filled!")
            email = request.form['email']
            delete_query = f"DELETE FROM Volunteers WHERE email_id = \'{email}\'"

            print(delete_query)

            exec_query = cur.execute(delete_query)
            mysql.connection.commit()
            return redirect('/admin/volunteers')

    return render_template("admin/volunteers.html", profile_details=profile_details, projects=projects)

@app.route("/admin/villageprofile", methods=['POST','GET'])
def village_profile():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM VillageProfile")

    if result_value > 0:
        userDetails = cur.fetchall()

    print(userDetails)
    # Generate the user profile details
    profile_details = []
    for user in userDetails:
        # VillageProfile(pincode, name, no_of_beneficiaries, no_of_primary_health_center, no_of_primary_school, transport,
        #                infrastructure, major_occupation, technical_literacy, year)
        user_profile = {'pincode': user[0], 'name': user[1], 'no_of_beneficiaries': user[2], 'no_of_primary_health_center': user[3],
                        'no_of_primary_school': user[4], 'transport': user[5], 'infrastructure': user[6], 'major_occupation': user[7], 'technical_literacy': user[8], 'year': user[9]}

        extract_beneficiaries_list_query = f"SELECT name,aadhar_id FROM Beneficiary WHERE aadhar_id IN (SELECT aadhar_id FROM belongs WHERE pincode = \'{user[0]}\')"

        extract_beneficiaries_list_query = cur.execute(extract_beneficiaries_list_query)
        extract_beneficiaries_list = cur.fetchall()

        if len(extract_beneficiaries_list) > 0:
            user_profile['beneficiaries'] = extract_beneficiaries_list
        else:
            user_profile['beneficiaries'] = ()

        profile_details.append(user_profile)

    print(profile_details)

    if(request.method=='POST'):
        print(request.json)
        form_data=request.json
        if(form_data['signal']=='search'):
            print("this is search query")
        elif(form_data['signal']=='editUser'):
            print("this is edit query")
        elif(form_data['signal']=='addUser'):
            print("add new data")
    return render_template('admin/village_profile.html', profile_details=profile_details)

@app.route("/admin/projects", methods=['POST','GET'])
def projects():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Projects")

    if result_value > 0:
        projectDetails = cur.fetchall()

    project_details = []
    for project in projectDetails:
        project_profile = {'event_name': project[0], 'start_date': project[1], 'types': project[2], 'budget': project[3], 'no_of_participants': project[4], 'duration': project[5], 'collection': project[6], 'total_expense': project[7]}

        even_name = project_profile['event_name']
        start_date = project_profile['start_date']

        extract_venue_id_query = f"SELECT venue_id FROM HeldAt WHERE event_name = \'{even_name}\' AND start_date = \'{start_date}\'"
        extract_beneficiaries_enrolled_query = f"SELECT name,aadhar_id FROM Beneficiary WHERE aadhar_id IN (SELECT aadhar_id FROM participants WHERE event_name = \'{even_name}\' AND start_date = \'{start_date}\')"
        extract_volunteers_enrolled_query = f"SELECT name,email_id FROM Volunteers WHERE email_id IN (SELECT email_id FROM volunteering WHERE event_name = \'{even_name}\' AND start_date = \'{start_date}\')"
        extract_donors_enrolled_query = f"SELECT funder_name,email_id FROM Funding WHERE email_id IN (SELECT email_id FROM Sponsors WHERE event_name = \'{even_name}\' AND start_date = \'{start_date}\')"
        extract_trainers_query = f"SELECT name,email_id FROM Trainers WHERE email_id IN (SELECT email_id FROM trains WHERE event_name = \'{even_name}\' AND start_date = \'{start_date}\')"
        extract_employee_query = f"SELECT name,employee_id FROM Teams WHERE employee_id IN (SELECT employee_id FROM Organize WHERE event_name = \'{even_name}\' AND start_date = \'{start_date}\')"
        extract_goods_query = f"SELECT item_name,quantity,amount FROM Goods WHERE event_name = \'{even_name}\' AND start_date = \'{start_date}\'"
        extract_expense_query = f"SELECT amount,description FROM ProjectExpense WHERE event_name = \'{even_name}\' AND start_date = \'{start_date}\'"

        extract_venue_id_query = cur.execute(extract_venue_id_query)
        extract_venue_id_query = cur.fetchall()
        if len(extract_venue_id_query) > 0:
            project_profile['venue_id'] = extract_venue_id_query[0][0]
        else:
            project_profile['venue_id'] = 'NA'

        extract_beneficiaries_enrolled_query = cur.execute(extract_beneficiaries_enrolled_query)
        extract_beneficiaries_enrolled_query = cur.fetchall()
        if len(extract_beneficiaries_enrolled_query) > 0:
            project_profile['beneficiaries'] = extract_beneficiaries_enrolled_query
        else:
            project_profile['beneficiaries'] = ()

        extract_volunteers_enrolled_query = cur.execute(extract_volunteers_enrolled_query)
        extract_volunteers_enrolled_query = cur.fetchall()
        if len(extract_volunteers_enrolled_query) > 0:
            project_profile['volunteers'] = extract_volunteers_enrolled_query
        else:
            project_profile['volunteers'] = ()

        extract_donors_enrolled_query = cur.execute(extract_donors_enrolled_query)
        extract_donors_enrolled_query = cur.fetchall()
        if len(extract_donors_enrolled_query) > 0:
            project_profile['donors'] = extract_donors_enrolled_query
        else:
            project_profile['donors'] = ()

        extract_trainers_query = cur.execute(extract_trainers_query)
        extract_trainers_query = cur.fetchall()
        if len(extract_trainers_query) > 0:
            project_profile['trainers'] = extract_trainers_query
        else:
            project_profile['trainers'] = ()

        extract_employee_query = cur.execute(extract_employee_query)
        extract_employee_query = cur.fetchall()
        if len(extract_employee_query) > 0:
            project_profile['employees'] = extract_employee_query
        else:
            project_profile['employees'] = ()

        extract_goods_query = cur.execute(extract_goods_query)
        extract_goods_query = cur.fetchall()
        if len(extract_goods_query) > 0:
            project_profile['goods'] = extract_goods_query
        else:
            project_profile['goods'] = ()

        extract_expense_query = cur.execute(extract_expense_query)
        extract_expense_query = cur.fetchall()
        if len(extract_expense_query) > 0:
            project_profile['expenses'] = extract_expense_query
        else:
            project_profile['expenses'] = ()

        project_details.append(project_profile)

    if(request.method=='POST'):
        print(request.json)
        form_data=request.json
        if(form_data['signal']=='search'):
            print("this is search query")
        elif(form_data['signal']=='editUser'):
            print("this is edit query")
        elif(form_data['signal']=='addUser'):
            print("add new data")
    return render_template('admin/projects.html', project_details=project_details)

@app.route("/admin/trainers", methods=['GET','POST'])
def trainers():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Trainers")

    if result_value > 0:
        userDetails = cur.fetchall()

    profile_details = []
    for user in userDetails:
        # Trainers(email_id, fee, name, age, gender)
        user_profile = {'email_id': user[0], 'fee': user[1], 'name': user[2], 'age': user[3], 'gender': user[4]}

        extract_phone_query = f"SELECT phone_number FROM TrainerPhoneEntity WHERE email_id = \'{user[0]}\'"
        extract_projects_query = f"SELECT event_name,start_date FROM trains WHERE email_id = \'{user[0]}\'"
        extract_beneficiaries_list_query = f"SELECT name, aadhar_id FROM Beneficiary WHERE aadhar_id IN (SELECT aadhar_id FROM TrainerBeneficiary WHERE email_id = \'{user[0]}\')"

        extract_phone_query = cur.execute(extract_phone_query)
        extract_phone_query = cur.fetchall()
        if len(extract_phone_query) > 0:
            user_profile['phone_number'] = extract_phone_query[0][0]
        else:
            user_profile['phone_number'] = 'NA'

        extract_projects_query = cur.execute(extract_projects_query)
        extract_projects_query = cur.fetchall()
        if len(extract_projects_query) > 0:
            user_profile['projects'] = extract_projects_query
        else:
            user_profile['projects'] = ()

        extract_beneficiaries_list_query = cur.execute(extract_beneficiaries_list_query)
        extract_beneficiaries_list = cur.fetchall()
        if len(extract_beneficiaries_list) > 0:
            user_profile['beneficiaries'] = extract_beneficiaries_list
        else:
            user_profile['beneficiaries'] = ()

        profile_details.append(user_profile)

    # Generate projects list
    projects_query = f"SELECT event_name FROM Projects"
    projects_query = cur.execute(projects_query)
    projects = cur.fetchall()

    # Adding trainers (done)
    if (request.method == 'POST'):
        if request.form['signal'] == 'addUser':
            print('add filled!@')
            name = request.form['name']
            email_id = request.form['email_id']
            phoneNumber = request.form['phoneNumber']
            gender = request.form['gender']
            age = request.form['age']
            fee = request.form['fee']

            projectEventName = request.form['project_name']
            project_start_year = request.form['project_year']

            beneficiaryAadharId = request.form['beneficiaryAadharId']
            beneficiaryName = request.form['beneficiaryName']

            add_query = f"INSERT INTO Trainers (email_id, fee, name, age, gender) "
            add_query = add_query + f"VALUES (\'{email_id}\', \'{fee}\', \'{name}\', \'{age}\', \'{gender}\')"
            exec_query = cur.execute(add_query)
            mysql.connection.commit()
            print("Trainer added")

            add_project_query = f"INSERT INTO trains (email_id, event_name, start_date) "
            add_project_query = add_project_query + f"VALUES (\'{email_id}\', \"{projectEventName}\", (SELECT start_date FROM Projects WHERE event_name = \"{projectEventName}\" AND YEAR(start_date) = \'{project_start_year}\'))"
            exec_query = cur.execute(add_project_query)
            mysql.connection.commit()
            print("Trainer added to project")

            if beneficiaryAadharId != '':
                # Insert intoTrainerBeneficiary
                add_beneficiary_query = f"INSERT INTO TrainerBeneficiary (email_id, aadhar_id) "
                add_beneficiary_query = add_beneficiary_query + f"VALUES (\'{email_id}\', \'{beneficiaryAadharId}\');"
                exec_query = cur.execute(add_project_query)
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


    return render_template("admin/trainers.html", profile_details=profile_details, projects=projects)


### Add new user
@app.route("/", methods=['POST'])
def insert():
    if (request.method == 'POST'):
        if 'addDetails' in request.form:
            print("addDetails filled!")
        # aadhar = request.form['aadhar']
        #
        # name = request.form['name']
        # dob = request.form['dob']
        # education = request.form['education']
        # martial = request.form['martial']
        # gender = request.form['gender']
        # employed = request.form['employed']
        #
        # cur = mysql.connection.cursor()
        #
        # query = "INSERT INTO Beneficiary (aadhar_id, name, date_of_birth, gender, marital_status, education, employed) VALUES (%s %s %s %s %s %s %s)"
        # # cur.execute(, (aadhar, name, dob, education, maritalstatus,  gender, employment_status) )
        # cur.execute(query, (aadhar, name, dob, gender, martial, education, employed))
        # mysql.connection.commit()
        # cur.close()

    return redirect('/admin/user')
    # return render_template('admin/user')
    # return render_template('admin/user.html')

if __name__=='__main__':
    app.run(debug=True)