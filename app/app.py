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