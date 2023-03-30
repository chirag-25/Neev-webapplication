import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import yaml
from email_script import send_email
import secrets

app = Flask(__name__)
app.secret_key='secret_key'

# Configure the database
db = yaml.load(open('db.yaml'), Loader=yaml.Loader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

def if_admin():
    cursor = mysql.connection.cursor()
    id_search_query = f"SELECT * FROM admin_password WHERE EmployeeID=\'{session['id']}\'"
    cursor.execute(id_search_query)
    account = cursor.fetchone()
    if account:
        return True
    return False

def restrict_child_routes():
    print("restrict_child_routes")
    if 'loggedin' in session:
        if if_admin():
            return 'admin'
    elif ('loggedin' in session):
        return 'staff'
    else:
        return 'No_access'

def check_project_year_combination(project_name, year):
    #check in projects whether the project name and year combination exists
    cursor = mysql.connection.cursor()
    query = f"SELECT * FROM Projects WHERE event_name=\'{project_name}\' AND start_date IN (SELECT start_date FROM Projects WHERE YEAR(start_date)=\'{year}\')"
    exec_query = cursor.execute(query)
    exec_query = cursor.fetchall()
    if len(exec_query) > 0:
        return True
    return False

# @app.route("/admin")
# def admin():
#     if 'loggedin' in session and if_admin():
#         return render_template("admin/dashboard.html",type="admin")
#     elif('loggedin' in session ):
#         return render_template("admin/dashboard.html",type="staff")
#     else:
#         return redirect(url_for('login'))

def check_password(pass_word,id,table):
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query="SELECT * FROM" +" "+table +" " + "WHERE EmployeeID="+str(id)
    cursor.execute(query)
    account=cursor.fetchone()
    if(account):
        if(account['EmployeePassword']==pass_word):
            return True
    return False

def log_out():
    session.pop('loggedin', None)
    session.pop('id', None)
    return redirect(url_for('login'))

temp_id = 'E001'

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        employee_id = request.form["employeeID"]
        password = request.form["password"]
        global temp_id
        temp_id = employee_id

        if (check_password(password, employee_id, "admin_password")):
            session['loggedin'] = True
            session['id'] = employee_id
            # session['username']=account['username']
            # return render_template("admin/user.html")
            return redirect('/admin/user_profile?type=admin')
        elif (check_password(password, employee_id, "staff_password")):
            session['loggedin'] = True
            session['id'] = employee_id
            # session['username']=account['username']
            return redirect('/admin/user_profile?type=staff')
        else:
            msg = "Incorrect Employee ID/password"
            flash(msg)
    return render_template("admin/login.html")


@app.route("/admin/user_profile", methods=['POST', 'GET'])
def user_profile():
    print(f'in user profile')

    type = restrict_child_routes()

    cur = mysql.connection.cursor()
    result_value = cur.execute(f"SELECT * FROM Teams where employee_id = \'{temp_id}\'")
    profileDetails = []
    if result_value == 1:
        user = cur.fetchall()[0]
        user_profile = {
            'employ_id': user[0],
            'name': user[1],
            'email_id': user[2],
            'salary': user[3],
            'position': user[4],
            'join_date': user[5],
            'leave_date': user[6],
            'reason': user[7]
        }
        profileDetails.append(user_profile)

    if (request.method == 'POST'):
        if request.form['signal'] == 'edit':
            print("edit of profile")
            username = request.form['username']
            email = request.form['email']
            employ_id = temp_id
            edit_query = f"UPDATE Teams SET name = \'{username}\', email_id = \'{email}\' WHERE employee_id = \'{employ_id}\'"
            print(f"edit query: {edit_query}")
            exec_query = cur.execute(edit_query)
            mysql.connection.commit()

        elif request.form['signal'] == 'logout':
            return log_out()

    return render_template("admin/user_profile.html", profileDetails=profileDetails, type=type)

@app.route("/admin/dashboard", methods=['POST', 'GET'])
def dashboard():
    type = restrict_child_routes()

    if (request.method == 'POST'):
        if request.form['signal'] == 'logout':
            return log_out()

    return render_template("admin/dashboard.html", type=type)

@app.route("/admin/funding", methods=['POST', 'GET'])
def funding():
    type = restrict_child_routes()
    if type == 'No_access':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Funding")
    if result_value > 0:
        userDetails = cur.fetchall()

    profileDetails = []
    for user in userDetails:
        user_profile = {
            'email': user[0], 'amount': user[1], 'benefactor': user[2], 'date': user[3]}
        sponsors_table_query = f"SELECT * FROM Sponsors WHERE email_id = \'{user[0]}\'"
        events_table_query = f"SELECT * FROM Projects"
        # print("before query")

        calculate_sponsors = cur.execute(sponsors_table_query)
        calculate_sponsors = cur.fetchall()

        calculate_events = cur.execute(events_table_query)
        calculate_events = cur.fetchall()

        # print(len(calculate_sponsors))
        if len(calculate_sponsors) > 0:
            user_profile['projects'] = calculate_sponsors
        else:
            # user_profile['email_id'] = 'NA'
            # user_profile['event_name'] = 'NA'
            # user_profile['start_date'] = 'NA'
            user_profile['projects'] = ()

        if (len(calculate_events) > 0):
            user_profile['events'] = calculate_events
        else:
            user_profile['events'] = ()

        # print(len(calculate_events))
        # print(user_profile['events'])
        profileDetails.append(user_profile)
    if (request.method == 'POST'):
        if request.form['signal'] == 'search':
            # pass
            benefactor = request.form['benefactor']
            email = request.form['email']
            amount = request.form['max_amount']
            # date = request.form['funding_date']
            year = request.form['year']
            funding_to = request.form['project_name']
            min_amount = request.form['min_amount']
            max_amount = request.form['max_amount']

            where_query = f" SELECT * FROM Funding"
            flag = False

            if benefactor != '':
                if flag == False:
                    where_query += f" WHERE funder_name = \'{benefactor}\' "
                else:
                    where_query += f"funder_name = \"{benefactor}\""
                flag = True
            if email != '':
                if flag == False:
                    where_query += f" WHERE email_id = \'{email}\' "
                else:
                    where_query += f" AND email_id = \"{email}\""
                flag = True
            if min_amount != '' and max_amount != '':
                if flag == False:
                    where_query += f" WHERE amount BETWEEN \'{min_amount}\' AND \'{max_amount}\'"
                else:
                    where_query += f" AND amount BETWEEN \'{min_amount}\' AND \'{max_amount}\'"
                flag = True

            if funding_to != '':
                if flag == False:
                    where_query += f" WHERE email_id IN (SELECT email_id FROM Sponsors WHERE event_name = \'{funding_to}\')"
                else:
                    where_query += f" AND email_id IN (SELECT email_id FROM Sponsors WHERE event_name = \'{funding_to}\')"
                flag = True

            if year != '':
                if flag == False:
                    where_query += f" WHERE YEAR(date) = {year}"
                else:
                    where_query += f" AND YEAR(date) = {year}"
                flag = True

            exec_query = cur.execute(where_query)
            search_results = cur.fetchall()
            # print(search_results)

            updated_profile_details = []
            for user in profileDetails:
                for result in search_results:
                    # print("email", result[0])
                    if user['email'] == result[0]:
                        updated_profile_details.append(user)
            profileDetails = updated_profile_details

            return render_template('admin/funding.html', userDetails=userDetails, profileDetails=profileDetails, calculate_events=calculate_events)
        elif request.form['signal'] == 'add':
            # print(request.form)
            print("addDetails filled!")

            benefactor = request.form['name']
            amount = request.form['amount_add']
            email = request.form['email']
            date = request.form['funding_date']
            year = date.split('-')[0]
            funding_to = request.form['project']

            if check_project_year_combination(funding_to, year) == False:
                flash(f"Project {funding_to} is not available for year {year}", 'danger')
                return redirect('/admin/funding')

            add_query = f"INSERT INTO Funding (email_id, amount, funder_name, date) "
            add_query = add_query + \
                f"VALUES (\"{email}\", \"{amount}\", \'{benefactor}\', \"{date}\")"
            exec_query = cur.execute(add_query)
            mysql.connection.commit()

            # add_project_query = f"INSERT INTO Sponsors (email_id, event_name, start_date)"
            # add_project_query = add_project_query + f"VALUES (\"{email}\", \"{funding_to}\", \"{date}\" )"
            # add_project_query = add_project_query + f" WHERE email_id = \"{email}\" "

            add_project_query = f"INSERT INTO Sponsors (email_id, event_name, start_date) "
            # assumption is taken here that beneficiary can only participate in current year's project
            add_project_query = add_project_query + \
                f"VALUES (\"{email}\", \"{funding_to}\", (SELECT start_date FROM Projects WHERE event_name = \"{funding_to}\" AND YEAR(start_date) = YEAR(\'{date}\')))"
            exec_add_project_query = cur.execute(add_project_query)
            mysql.connection.commit()

            return redirect('/admin/funding')
        elif request.form['signal'] == 'edit':
            print("iN edit")
            benefactor = request.form['benefactor']
            amount = request.form['amount']
            email = request.form['email']
            date = request.form['funding_date']
            project_name = request.form['project_name']

            # check if project is available for the year
            year = date.split('-')[0]
            print(year)
            if project_name != '':
                if check_project_year_combination(project_name, year) == False:
                    flash(f"Project {project_name} is not available for year {year}", 'danger')
                    return redirect('/admin/funding')

            edit_query = f"UPDATE Funding "
            edit_query = edit_query + \
                f"SET funder_name = \'{benefactor}\', amount = \'{amount}\', email_id = \'{email}\', date = \'{date}\' "
            edit_query = edit_query + f"WHERE email_id = \'{email}\'"
            exec_query = cur.execute(edit_query)
            mysql.connection.commit()

            if project_name != '':
                #check if project is already defined for the user
                check_query = f"SELECT * FROM Sponsors WHERE email_id = \'{email}\' AND event_name = \"{project_name}\" AND start_date IN (SELECT start_date FROM Projects WHERE event_name = \"{project_name}\" AND YEAR(start_date) = YEAR(\'{date}\'));"
                exec_query = cur.execute(check_query)
                check_result = cur.fetchall()
                if len(check_result) == 0:
                    #insert project
                    add_project_query = f"INSERT INTO Sponsors (email_id, event_name, start_date) "
                    add_project_query = add_project_query + f"VALUES (\"{email}\", \"{project_name}\", (SELECT start_date FROM Projects WHERE event_name = \"{project_name}\" AND YEAR(start_date) = YEAR(\'{date}\')))"
                    exec_query = cur.execute(add_project_query)
                    mysql.connection.commit()

            return redirect('/admin/funding')
        elif request.form['signal'] == 'delete':
            email = request.form['email']
            delete_query = f"DELETE FROM Funding WHERE email_id = \'{email}\' "
            exec_query = cur.execute(delete_query)
            mysql.connection.commit()
            return redirect('/admin/funding')

        elif request.form['signal'] == 'logout':
            return log_out()
        # print(profileDetails)
    return render_template('admin/funding.html', userDetails=userDetails, profileDetails=profileDetails, calculate_events=calculate_events, calculate_sponsors=calculate_sponsors)


@app.route("/admin/villageprofile", methods=['POST', 'GET'])
def village_profile():
    type = restrict_child_routes()
    if type == 'No_access':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM VillageProfile")

    if result_value > 0:
        userDetails = cur.fetchall()

    village_names_query = f"SELECT DISTINCT name FROM VillageProfile"
    village_names_query_exec = cur.execute(village_names_query)
    village_names = cur.fetchall()

    occupation_name_query = f"SELECT DISTINCT major_occupation FROM VillageProfile"
    occupation_name_query_exec = cur.execute(occupation_name_query)
    occupation_names = cur.fetchall()

    technical_literacy_query = f"SELECT DISTINCT technical_literacy FROM VillageProfile"
    technical_literacy_query_exec = cur.execute(technical_literacy_query)
    technical_literacy_names = cur.fetchall()

    # print(userDetails)
    # Generate the user profile details
    profile_details = []
    for user in userDetails:
        # VillageProfile(pincode, name, no_of_beneficiaries, no_of_primary_health_center, no_of_primary_school, transport,
        #                infrastructure, major_occupation, technical_literacy, year)
        user_profile = {'pincode': user[0], 'name': user[1], 'no_of_beneficiaries': user[2], 'no_of_primary_health_center': user[3],
                        'no_of_primary_school': user[4], 'transport': user[5], 'infrastructure': user[6], 'major_occupation': user[7], 'technical_literacy': user[8], 'year': user[9]}

        extract_beneficiaries_list_query = f"SELECT name,aadhar_id FROM Beneficiary WHERE aadhar_id IN (SELECT aadhar_id FROM belongs WHERE pincode = \'{user[0]}\')"

        extract_beneficiaries_list_query = cur.execute(
            extract_beneficiaries_list_query)
        extract_beneficiaries_list = cur.fetchall()

        calculate_occupation = f"SELECT * FROM VillageProfile"
        calculate_occupation = cur.fetchall()

        if len(extract_beneficiaries_list) > 0:
            user_profile['beneficiaries'] = extract_beneficiaries_list
        else:
            user_profile['beneficiaries'] = ()

        if len(calculate_occupation) > 0:
            user_profile['occupation'] = calculate_occupation
        else:
            user_profile['occupation'] = "NA"

        profile_details.append(user_profile)

    # print(profile_details)

    if (request.method == 'POST'):
        if (request.form['signal'] == 'search'):
            print("this is search query")
            name = request.form['name']
            pinCode = request.form['pinCode']
            occupation = request.form['occupation']
            technical_literacy = request.form['technical_literacy']

            print(name)

            where_query = f" SELECT * FROM VillageProfile"
            flag = False

            if name != '':
                if flag == False:
                    where_query += f" WHERE name = \'{name}\' "
                else:
                    where_query += f"name = \"{name}\""
                flag = True
            if pinCode != '':
                if flag == False:
                    where_query += f" WHERE pincode = \'{pinCode}\' "
                else:
                    where_query += f" AND pincode = \"{pinCode}\""
                flag = True
            if occupation != '':
                if flag == False:
                    where_query += f" WHERE major_occupation = \'{occupation}\' "
                else:
                    where_query += f" AND major_occupation = \"{occupation}\""
                flag = True

            if technical_literacy != '':
                if flag == False:
                    where_query += f" WHERE technical_literacy = \'{technical_literacy}\' "
                else:
                    where_query += f" AND technical_literacy = \"{technical_literacy}\""
                flag = True

            exec_query = cur.execute(where_query)
            print("Search query executed")
            search_results = cur.fetchall()

            # print(search_results)

            updated_profile_details = []
            for user in profile_details:
                for result in search_results:
                    if user['name'] == result[1]:
                        updated_profile_details.append(user)
            profile_details = updated_profile_details
            # print(profileDetails)
        elif (request.form['signal'] == 'editUser'):
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

            # updated based on pincode
            edit_query = f"UPDATE VillageProfile "
            edit_query = edit_query + f"SET pincode = \'{pinCode}\', name = \'{name}\', no_of_beneficiaries = \'{noOfBeneficiaries}\', no_of_primary_health_center = \'{noOfHealthCenters}\', no_of_primary_school = \'{noOfSchools}\', transport = \'{transport}\', infrastructure = \'{infrastructure}\', major_occupation = \'{occupation}\', technical_literacy = \'{technical_literacy}\', year = \'{year}\'"
            edit_query = edit_query + f"WHERE pincode = \'{pinCode}\';"
            print(edit_query)

            exec_query = cur.execute(edit_query)
            mysql.connection.commit()
            return redirect('/admin/villageprofile')
            # return render_template('admin/village_profile.html')
            print("edit")

            print("this is edit query")
        elif (request.form['signal'] == 'addUser'):
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
            # beneficiaryAadharId = request.form['beneficiaryAadharId']
            # beneficiaryName = request.form['beneficiaryName']

            print(pinCode)

            # project = request.form['']

            add_query = f"INSERT INTO VillageProfile (pincode, name, no_of_beneficiaries, no_of_primary_health_center, no_of_primary_school, transport, infrastructure, major_occupation, technical_literacy, year) "
            add_query = add_query + \
                f"VALUES (\'{pinCode}\', \'{name}\', \'{noOfBeneficiaries}\', \'{noOfHealthCenters}\', \'{noOfSchools}\', \'{transport}\', \'{infrastructure}\', \'{occupation}\', \'{technical_literacy}\', \'{year}\');"
            print(add_query)

            exec_query = cur.execute(add_query)
            mysql.connection.commit()

            return redirect('/admin/villageprofile')
            print("add new data")

        elif (request.form['signal'] == 'delete'):
            pinCode = request.form['pinCode']
            # print(pinCode)

            # delete operation considering event_name and start_date
            delete_query = f"DELETE FROM VillageProfile WHERE pincode = \'{pinCode}\';"

            print("DELETE QUERY EXECUTED")

            exec_query = cur.execute(delete_query)
            print("delete query executed")
            mysql.connection.commit()

            return redirect('/admin/villageprofile')

        elif request.form['signal'] == 'logout':
            return log_out()

    return render_template('admin/village_profile.html', profile_details=profile_details, village_names=village_names, occupation_names=occupation_names, technical_literacy_names=technical_literacy_names)


@app.route("/admin/volunteers", methods=['POST', 'GET'])
def volunteers():
    type = restrict_child_routes()
    if type == 'No_access':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Volunteers")

    if result_value > 0:
        userDetails = cur.fetchall()

    # Generate the user profile details
    profile_details = []
    for user in userDetails:
        # (email_id, name, phone_number, date_of_birth, gender)
        # INSERT INTO volunteering(email_id, event_name, start_date)
        user_profile = {'email_id': user[0], 'name': user[1],
                        'phone_number': user[2], 'date_of_birth': user[3], 'gender': user[4]}
        calculate_age_query = f"SELECT TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) FROM Volunteers WHERE email_id = \'{user[0]}\'"
        extract_enrolled_projects_query = f"SELECT * FROM volunteering WHERE email_id = \'{user[0]}\'"

        calculate_age = cur.execute(calculate_age_query)
        calculate_age = cur.fetchall()

        extract_enrolled_projects = cur.execute(
            extract_enrolled_projects_query)
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
        if request.form['signal'] == 'search':
            name = request.form['name']
            email = request.form['email']
            gender = request.form['gender']
            project_name = request.form['project_name']
            year = request.form['year']

            where_query = f" SELECT * FROM Volunteers"

            flag = False

            if name != '':
                if flag == False:
                    where_query += f" WHERE name = \'{name}\' "
                else:
                    where_query += f"name = \"{name}\""
                flag = True

            if email != '':
                if flag == False:
                    where_query += f" WHERE email_id = \'{email}\' "
                else:
                    where_query += f" AND email_id = \"{email}\""
                flag = True

            if gender != '':
                if flag == False:
                    where_query += f" WHERE gender = \'{gender}\' "
                else:
                    where_query += f" AND gender = \'{gender}\'"
                flag = True

            if project_name != '':
                if flag == False:
                    where_query += f" WHERE email_id IN (SELECT email_id FROM volunteering WHERE event_name = \'{project_name}\') "
                else:
                    where_query += f" AND email_id IN (SELECT email_id FROM volunteering WHERE event_name = \"{project_name}\") "
                flag = True

            if year != '':
                if flag == False:
                    # where_query += f" WHERE YEAR(start_date) = {year}"
                    where_query += f" WHERE email_id IN (SELECT email_id FROM volunteering WHERE YEAR(start_date) = {year})"
                else:
                    # where_query += f" AND YEAR(start_date) = {year}"
                    where_query += f" AND email_id IN (SELECT email_id FROM volunteering WHERE YEAR(start_date) = {year})"
                flag = True

            exec_query = cur.execute(where_query)
            print("Search query executed")
            search_results = cur.fetchall()

            # print(search_results)

            updated_profile_details = []
            for user in profile_details:
                for result in search_results:
                    if user['email_id'] == result[0]:
                        updated_profile_details.append(user)
            profile_details = updated_profile_details

        elif request.form['signal'] == 'addUser':
            print(request.form)
            print("addDetails filled!")

            volunteers_name = request.form['name']
            email = request.form['email']
            date_of_birth = request.form['dob']
            gender = request.form['gender']
            phone = request.form['phone']

            projectEventName = request.form['project_name']
            project_start_year = request.form['project_year']

            # check if project is available for the year
            if check_project_year_combination(projectEventName, project_start_year) == False:
                flash(f"Project {projectEventName} is not available for year {project_start_year}", 'danger')
                return redirect('/admin/volunteers')

            add_query = f"INSERT INTO Volunteers (email_id, name, phone_number, date_of_birth, gender) "
            add_query = add_query + \
                f"VALUES (\'{email}\', \'{volunteers_name}\', \'{phone}\', \'{date_of_birth}\', \'{gender}\')"
            exec_query = cur.execute(add_query)
            mysql.connection.commit()

            add_project_query = f"INSERT INTO volunteering (email_id, event_name, start_date) "
            add_project_query = add_project_query + \
                f"VALUES (\'{email}\', \"{projectEventName}\", (SELECT start_date FROM Projects WHERE event_name = \"{projectEventName}\" AND YEAR(start_date) = \'{project_start_year}\'))"
            exec_query = cur.execute(add_project_query)
            mysql.connection.commit()

            return redirect('/admin/volunteers')

        elif request.form['signal'] == 'editUser':
            volunteers_name = request.form['volunteer_name']
            email = request.form['email']
            date_of_birth = request.form['dob']
            gender = request.form['gender']
            phone = request.form['phone']

            projectEventName = request.form['project_name']
            project_start_year = request.form['project_year']

            # check if project is available for the year
            if check_project_year_combination(projectEventName, project_start_year) == False:
                flash(f"Project {projectEventName} is not available for year {project_start_year}", 'danger')
                return redirect('/admin/volunteers')

            edit_query = f"UPDATE Volunteers "
            edit_query = edit_query + \
                f"SET name = \'{volunteers_name}\', email_id = \'{email}\', date_of_birth = \'{date_of_birth}\', gender = \'{gender}\', phone_number = \'{phone}\'"
            edit_query = edit_query + f"WHERE email_id = \'{email}\';"
            exec_query = cur.execute(edit_query)
            mysql.connection.commit()

            # check if the email_id, project, date exists
            check_query = f"SELECT * FROM volunteering WHERE email_id = \'{email}\' AND event_name = \"{projectEventName}\" AND start_date = (SELECT start_date FROM Projects WHERE event_name = \"{projectEventName}\" AND YEAR(start_date) = \'{project_start_year}\');"
            exec_query = cur.execute(check_query)
            check_result = cur.fetchall()
            if len(check_result) == 0:
                add_project_query = f"INSERT INTO volunteering (email_id, event_name, start_date) "
                add_project_query = add_project_query + \
                    f"VALUES (\'{email}\', \"{projectEventName}\", (SELECT start_date FROM Projects WHERE event_name = \"{projectEventName}\" AND YEAR(start_date) = \'{project_start_year}\'))"
                exec_query = cur.execute(add_project_query)
                mysql.connection.commit()
                print("Trainer added to project")

            return redirect('/admin/volunteers')

        elif request.form['signal'] == 'delete':
            print("delete filled!")
            email = request.form['email']
            delete_query = f"DELETE FROM Volunteers WHERE email_id = \'{email}\'"

            print(delete_query)

            exec_query = cur.execute(delete_query)
            mysql.connection.commit()
            return redirect('/admin/volunteers')

        elif request.form['signal'] == 'logout':
            return log_out()

    return render_template("admin/volunteers.html", profile_details=profile_details, projects=projects)


@app.route("/admin/projects", methods=['POST', 'GET'])
def projects():
    type = restrict_child_routes()
    if type == 'No_access':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Projects")

    if result_value > 0:
        projectDetails = cur.fetchall()

    project_name_query = f"SELECT DISTINCT event_name FROM Projects"
    project_name_query_exec = cur.execute(project_name_query)
    project_names = cur.fetchall()

    event_name_query = f"SELECT DISTINCT types FROM Projects"
    event_name_query_exec = cur.execute(event_name_query)
    event_names = cur.fetchall()

    # extract distinct venue ID
    venue_id_query = f"SELECT DISTINCT venue_id FROM Venue"
    venue_id_query_exec = cur.execute(venue_id_query)
    venue_ids = cur.fetchall()

    # extract distinct employee ID from teams table
    employee_id_query = f"SELECT DISTINCT employee_id FROM Teams"
    employee_id_query_exec = cur.execute(employee_id_query)
    employee_ids = cur.fetchall()

    project_details = []
    for project in projectDetails:
        project_profile = {'event_name': project[0], 'start_date': project[1], 'types': project[2],
                           'budget': project[3],
                           'no_of_participants': project[4], 'duration': project[5], 'collection': project[6],
                           'total_expense': project[7]}

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

        extract_beneficiaries_enrolled_query = cur.execute(
            extract_beneficiaries_enrolled_query)
        extract_beneficiaries_enrolled_query = cur.fetchall()
        if len(extract_beneficiaries_enrolled_query) > 0:
            project_profile['beneficiaries'] = extract_beneficiaries_enrolled_query
        else:
            project_profile['beneficiaries'] = ()

        extract_volunteers_enrolled_query = cur.execute(
            extract_volunteers_enrolled_query)
        extract_volunteers_enrolled_query = cur.fetchall()
        if len(extract_volunteers_enrolled_query) > 0:
            project_profile['volunteers'] = extract_volunteers_enrolled_query
        else:
            project_profile['volunteers'] = ()

        extract_donors_enrolled_query = cur.execute(
            extract_donors_enrolled_query)
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

    if (request.method == 'POST'):
        if (request.form['signal'] == 'search'):
            event_name = request.form['event_name']
            year = request.form['year']
            type_event = request.form['type_event']
            min_budget = request.form['min_budget']
            max_budget = request.form['max_budget']

            where_query = f" SELECT * FROM Projects"
            flag = False

            if event_name != '':
                if flag == False:
                    where_query += f" WHERE event_name = \'{event_name}\' "
                else:
                    where_query += f"event_name = \"{event_name}\""
                flag = True

            if year != '':
                if flag == False:
                    where_query += f" WHERE YEAR(start_date) = {year}"
                else:
                    where_query += f" AND YEAR(start_date) = {year}"
                flag = True
            if type_event != '':
                if flag == False:
                    where_query += f" WHERE types = \'{type_event}\' "
                else:
                    where_query += f" AND types = \"{type_event}\""
                flag = True

            if min_budget != '' and max_budget != '':
                if flag == False:
                    where_query += f" WHERE budget BETWEEN \'{min_budget}\' AND \'{max_budget}\'"
                else:
                    where_query += f" AND budget BETWEEN \'{min_budget}\' AND \'{max_budget}\'"
                flag = True

            exec_query = cur.execute(where_query)
            print("Search query executed")
            search_results = cur.fetchall()

            updated_profile_details = []
            for user in project_details:
                for result in search_results:
                    if user['event_name'] == result[0]:
                        updated_profile_details.append(user)
            project_details = updated_profile_details

            print("this is search query")

        # editing user info
        elif request.form['signal'] == 'editProject':
            event_name = request.form['event_name']
            date = request.form['date']
            budget = request.form['budget']
            participants = request.form['participants']
            duration = request.form['duration']
            collection = request.form['collection']
            expense = request.form['expense']
            Types = request.form['types']

            venue_id = request.form['venue_id']

            employee_id = request.form['employee_id']
            employee_role = request.form['role']

            # updated based on event_name and start_date
            edit_query = f"UPDATE Projects "
            edit_query = edit_query + \
                f"SET event_name = \'{event_name}\', start_date = \'{date}\', types = \'{Types}\', budget = \'{budget}\', no_of_participants = \'{participants}\', duration = \'{duration}\', collection = \'{collection}\', total_expense = \'{expense}\'"
            edit_query = edit_query + \
                f"WHERE event_name = \'{event_name}\' and start_date = \'{date}\';"
            exec_query = cur.execute(edit_query)
            mysql.connection.commit()

            if venue_id != '':
                edit_venue_query = f"UPDATE HeldAt "
                edit_venue_query = edit_venue_query + \
                    f"SET venue_id = \'{venue_id}\'"
                edit_venue_query = edit_venue_query + \
                    f"WHERE event_name = \'{event_name}\' and start_date = \'{date}\';"
                exec_query = cur.execute(edit_venue_query)
                mysql.connection.commit()

            if employee_id != '':
                check_query = f"SELECT * FROM Organize WHERE employee_id = \'{employee_id}\' AND event_name = \"{event_name}\" AND start_date = \'{date}\';"
                exec_query = cur.execute(check_query)
                check_result = cur.fetchall()
                if len(check_result) == 0:
                    add_project_query = f"INSERT INTO Organize (employee_id, event_name, start_date, role) "
                    add_project_query = add_project_query + f"VALUES (\'{employee_id}\', \"{event_name}\", \'{date}\', \'{employee_role}\');"
                    exec_query = cur.execute(add_project_query)
                    mysql.connection.commit()

            return redirect('/admin/projects')

        elif request.form['signal'] == 'addProject':
            event_name = request.form['event_name']
            date = request.form['date']
            budget = request.form['budget']
            participants = request.form['participants']
            duration = request.form['duration']
            collection = request.form['collection']
            expense = request.form['expense']
            Types = request.form['types']

            venue_id = request.form['venue_id']

            add_query = f"INSERT INTO Projects (event_name, start_date, types, budget, no_of_participants, duration, collection, total_expense) "
            add_query = add_query + \
                f"VALUES (\'{event_name}\', \'{date}\', \'{Types}\', \'{budget}\', \'{participants}\', \'{duration}\', \'{collection}\', \'{expense}\');"
            exec_query = cur.execute(add_query)
            mysql.connection.commit()

            if venue_id != '':
                # insert project in heldat
                add_query = f"INSERT INTO HeldAt (venue_id, event_name, start_date) "
                add_query = add_query + \
                    f"VALUES (\'{venue_id}\', \'{event_name}\', \'{date}\');"
                exec_query = cur.execute(add_query)
                mysql.connection.commit()

            return redirect('/admin/projects')

        # delete the user info
        elif request.form['signal'] == 'delete':
            event_name = request.form['event_name']
            start_date = request.form['date']

            # delete operation considering event_name and start_date
            delete_query = f"DELETE FROM Projects WHERE event_name = \'{event_name}\' and start_date = \'{start_date}\';"

            exec_query = cur.execute(delete_query)
            mysql.connection.commit()
            return redirect('/admin/projects')

        elif request.form['signal'] == 'logout':
            return log_out()

    return render_template('admin/projects.html', project_details=project_details, project_names=project_names,
                           event_names=event_names, venue_ids=venue_ids, employee_ids=employee_ids)


@app.route("/admin/trainers", methods=['GET', 'POST'])
def trainers():
    type = restrict_child_routes()
    if type == 'No_access':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Trainers")

    if result_value > 0:
        userDetails = cur.fetchall()

    profile_details = []
    for user in userDetails:
        # Trainers(email_id, fee, name, age, gender)
        user_profile = {'email_id': user[0], 'fee': user[1],
                        'name': user[2], 'age': user[3], 'gender': user[4]}

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

        extract_beneficiaries_list_query = cur.execute(
            extract_beneficiaries_list_query)
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
        if request.form['signal'] == 'search':
            name = request.form['name']
            email_id = request.form['email_id']
            gender = request.form['gender']
            min_fee = request.form['min_fee']
            max_fee = request.form['max_fee']
            min_age = request.form['min_age']
            max_age = request.form['max_age']

            where_query = f"SELECT email_id FROM Trainers "
            flag = False
            if name != '':
                if flag == False:
                    where_query += f"WHERE name = \"{name}\""
                else:
                    where_query += f"name = \"{name}\""
                flag = True

            if email_id != '':
                if flag == False:
                    where_query += f"WHERE email_id = \'{email_id}\'"
                else:
                    where_query += f" AND email_id = \'{email_id}\'"
                flag = True

            if gender != '':
                if flag == False:
                    where_query += f"WHERE gender = \'{gender}\'"
                else:
                    where_query += f" AND gender = \'{gender}\'"
                flag = True

            if min_fee != '' and max_fee != '':
                if flag == False:
                    where_query += f" WHERE fee BETWEEN \'{min_fee}\' AND \'{max_fee}\'"
                else:
                    where_query += f" AND fee BETWEEN \'{min_fee}\' AND \'{max_fee}\'"
                flag = True

            if min_age != '' and max_age != '':
                if flag == False:
                    where_query += f" WHERE age BETWEEN \'{min_age}\' AND \'{max_age}\'"
                else:
                    where_query += f" AND age BETWEEN \'{min_age}\' AND \'{max_age}\'"
                flag = True

            exec_query = cur.execute(where_query)
            search_results = cur.fetchall()

            updated_profile_details = []
            for user in profile_details:
                for result in search_results:
                    if user['email_id'] == result[0]:
                        updated_profile_details.append(user)
            profile_details = updated_profile_details

            pass
        elif request.form['signal'] == 'addUser':
            print('add filled!@')
            name = request.form['name']
            email_id = request.form['email_id']
            phoneNumber = request.form['phoneNumber']
            gender = request.form['gender']
            age = request.form['age']
            fee = request.form['fee']

            projectEventName = request.form['project_name']
            project_start_year = request.form['project_year']

            # check if project year combination exists
            if check_project_year_combination(projectEventName, project_start_year) == False:
                flash(f"Project {projectEventName} is not available for year {project_start_year}", 'danger')
                return redirect('/admin/trainers')

            beneficiaryAadharId = request.form['beneficiaryAadharId']
            beneficiaryName = request.form['beneficiaryName']

            add_query = f"INSERT INTO Trainers (email_id, fee, name, age, gender) "
            add_query = add_query + \
                f"VALUES (\'{email_id}\', \'{fee}\', \'{name}\', \'{age}\', \'{gender}\')"
            exec_query = cur.execute(add_query)
            mysql.connection.commit()
            print("Trainer added")

            add_project_query = f"INSERT INTO trains (email_id, event_name, start_date) "
            add_project_query = add_project_query + \
                f"VALUES (\'{email_id}\', \"{projectEventName}\", (SELECT start_date FROM Projects WHERE event_name = \"{projectEventName}\" AND YEAR(start_date) = \'{project_start_year}\'))"
            exec_query = cur.execute(add_project_query)
            mysql.connection.commit()
            print("Trainer added to project")

            if beneficiaryAadharId != '':
                # Insert intoTrainerBeneficiary
                add_beneficiary_query = f"INSERT INTO TrainerBeneficiary (email_id, aadhar_id) "
                add_beneficiary_query = add_beneficiary_query + \
                    f"VALUES (\'{email_id}\', \'{beneficiaryAadharId}\');"
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

            projectEventName = request.form['project_name']
            project_start_year = request.form['project_year']

            # check if project year combination exists
            if check_project_year_combination(projectEventName, project_start_year) == False:
                flash(f"Project {projectEventName} is not available for year {project_start_year}", 'danger')
                return redirect('/admin/trainers')

            beneficiaryAadharId = request.form['beneficiaryAadharId']
            beneficiaryName = request.form['beneficiaryName']

            # updated based on email_id
            edit_query = f"UPDATE Trainers "
            edit_query = edit_query + \
                f"SET email_id = \'{email_id}\', fee = \'{fee}\', name = \'{name}\', age = \'{age}\', gender = \'{gender}\'"
            edit_query = edit_query + f"WHERE email_id = \'{email_id}\';"
            exec_query = cur.execute(edit_query)
            mysql.connection.commit()

            # check if the email_id, project, date exists
            check_query = f"SELECT * FROM trains WHERE email_id = \'{email_id}\' AND event_name = \"{projectEventName}\" AND start_date = (SELECT start_date FROM Projects WHERE event_name = \"{projectEventName}\" AND YEAR(start_date) = \'{project_start_year}\');"
            exec_query = cur.execute(check_query)
            check_result = cur.fetchall()
            if len(check_result) == 0:
                add_project_query = f"INSERT INTO trains (email_id, event_name, start_date) "
                add_project_query = add_project_query + \
                    f"VALUES (\'{email_id}\', \"{projectEventName}\", (SELECT start_date FROM Projects WHERE event_name = \"{projectEventName}\" AND YEAR(start_date) = \'{project_start_year}\'))"
                exec_query = cur.execute(add_project_query)
                mysql.connection.commit()
                print("Trainer added to project")

            # #update project on email_id
            # edit_project_query = f"UPDATE trains "
            # edit_project_query = edit_project_query + f"SET event_name = \"{projectEventName}\", start_date = (SELECT start_date FROM Projects WHERE event_name = \"{projectEventName}\" AND YEAR(start_date) = \'{project_start_year}\') WHERE email_id = \'{email_id}\';"
            # print(edit_project_query)
            # exec_query = cur.execute(edit_project_query)
            # mysql.connection.commit()

            return redirect('/admin/trainers')

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

        elif request.form['signal'] == 'logout':
            return log_out()

    return render_template("admin/trainers.html", profile_details=profile_details, projects=projects)


@app.route("/admin/user", methods=['POST', 'GET'])
def user():
    type = restrict_child_routes()
    if type == 'No_access':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Beneficiary")

    if result_value > 0:
        userDetails = cur.fetchall()

    # Generate the user profile details
    profile_details = []
    for user in userDetails:
        user_profile = {'aadhar': user[0], 'name': user[1], 'dob': user[2], 'gender': user[3], 'martial': user[4],
                        'education': user[5], 'photo': user[6], 'employed': user[7], 'photo_caption': user[8]}
        calculate_age_query = f"SELECT TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) FROM Beneficiary WHERE aadhar_id = \'{user[0]}\'"
        extract_village_query = f"SELECT pincode, name FROM VillageProfile WHERE pincode = (SELECT pincode FROM belongs WHERE aadhar_id = \'{user[0]}\')"
        extract_enrolled_projects_query = f"SELECT * FROM participants WHERE aadhar_id = \'{user[0]}\'"
        extract_phone_query = f"SELECT phone_number FROM BeneficiaryPhoneEntity WHERE aadhar_id = \'{user[0]}\'"

        calculate_age = cur.execute(calculate_age_query)
        calculate_age = cur.fetchall()

        extract_village = cur.execute(extract_village_query)
        extract_village = cur.fetchall()

        extract_enrolled_projects = cur.execute(
            extract_enrolled_projects_query)
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

            project = request.form['project_name']
            project_start_year = request.form['project_year']

            # check if project is available for the year
            if check_project_year_combination(project, project_start_year) == False:
                flash(f"Project {project} is not available for year {project_start_year}", 'danger')
                return redirect('/admin/user')

            add_query = f"INSERT INTO Beneficiary (aadhar_id, name, date_of_birth, gender, marital_status, education, photo, employed, photo_caption) "
            add_query = add_query + \
                f"VALUES ({aadhar}, \"{name}\", \'{dob}\', \'{gender}\', \'{martial}\', \'{education}\', NULL, \"{employed}\", NULL)"
            exec_query = cur.execute(add_query)
            mysql.connection.commit()

            # Add phone_number query
            add_phone_query = f"INSERT INTO BeneficiaryPhoneEntity (aadhar_id, phone_number) "
            add_phone_query = add_phone_query + \
                f"VALUES ({aadhar}, \"{phone_number}\")"
            exec_query = cur.execute(add_phone_query)
            mysql.connection.commit()

            # Add village query
            add_village_query = f"INSERT INTO belongs (aadhar_id, pincode) "
            add_village_query = add_village_query + \
                f"VALUES ({aadhar}, (SELECT pincode FROM VillageProfile WHERE name = \"{village}\"))"
            exec_query = cur.execute(add_village_query)
            mysql.connection.commit()

            # Add project query
            add_project_query = f"INSERT INTO participants (aadhar_id, event_name, start_date) "
            add_project_query = add_project_query + \
                f"VALUES ({aadhar}, \"{project}\", (SELECT start_date FROM Projects WHERE event_name = \"{project}\" AND YEAR(start_date) = \'{project_start_year}\'))"
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

            project = request.form['project_name']
            project_start_year = request.form['project_year']

            if project != '':
                if check_project_year_combination(project, project_start_year) == False:
                    flash(f"Project {project} is not available for year {project_start_year}", 'danger')
                    return redirect('/admin/user')

            edit_query = f"UPDATE Beneficiary "
            edit_query = edit_query + \
                f"SET name = \'{name}\', date_of_birth = \'{dob}\', gender = \'{gender}\', marital_status = \'{martial}\', education = \'{education}\', photo = NULL, employed = \"{employed}\", photo_caption = NULL "
            edit_query = edit_query + f"WHERE aadhar_id = {aadhar}"
            exec_query = cur.execute(edit_query)
            mysql.connection.commit()

            # Update phone_number, village and project if provided
            if phone_number != '':
                add_phone_query = f"INSERT INTO BeneficiaryPhoneEntity (aadhar_id, phone_number) "
                add_phone_query = add_phone_query + \
                    f"VALUES ({aadhar}, \"{phone_number}\")"
                exec_query = cur.execute(add_phone_query)
                mysql.connection.commit()

            if village != '':
                edit_village_query = f"UPDATE belongs "
                edit_village_query = edit_village_query + \
                    f"SET pincode = (SELECT pincode FROM VillageProfile WHERE name = \"{village}\") "
                edit_village_query = edit_village_query + \
                    f"WHERE aadhar_id = {aadhar}"
                exec_query = cur.execute(edit_village_query)
                mysql.connection.commit()

            if project != '':
                add_project_query = f"INSERT INTO participants (aadhar_id, event_name, start_date) "
                add_project_query = add_project_query + \
                    f"VALUES ({aadhar}, \"{project}\", (SELECT start_date FROM Projects WHERE event_name = \"{project}\" AND YEAR(start_date) = \'{project_start_year}\'))"
                exec_query = cur.execute(add_project_query)
                mysql.connection.commit()

            return redirect('/admin/user')

        elif request.form['signal'] == 'delete':
            aadhar = request.form['aadhar']
            delete_query = f"DELETE FROM Beneficiary WHERE aadhar_id = {aadhar}"

            exec_query = cur.execute(delete_query)
            mysql.connection.commit()
            return redirect('/admin/user')

        elif request.form['signal'] == 'logout':
            return log_out()

    return render_template('admin/user.html', searchResults=tuple(), profile_details=profile_details, projects=projects, villages=villages, education_list=education_list)
    # return render_template('admin/user.html')


@app.route('/admin/team', methods=['GET', 'POST'])
def team():
    type = restrict_child_routes()
    if type == 'No_access':
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Teams")

    if result_value > 0:
        teamdetails = cur.fetchall()

    position_name_query = f" SELECT DISTINCT position FROM Teams"
    position_name_query_exec = cur.execute(position_name_query)
    position_names = cur.fetchall()

    project_name_query = f" SELECT DISTINCT event_name FROM Organize"
    project_name_query_exec = cur.execute(project_name_query)
    project_names = cur.fetchall()

    team_details = []
    for team in teamdetails:
        team_profile = {'employee_id': team[0], 'name': team[1], 'email_id': team[2], 'salary': team[3],
                        'position': team[4], 'year_of_joining': team[5], 'year_of_leaving': team[6],
                        'reason_of_leaving': team[7]}

        # extract_projects_role_date_query = f"SELECT event_name,start_date FROM Organize WHERE employee_id IN (SELECT employee_id FROM Organize WHERE event_name = \'{event_name}\' AND start_date = \'{start_date}\')"
        extract_projects_role_date_query = f"SELECT event_name, start_date FROM Organize WHERE employee_id = \'{team_profile['employee_id']}\' "
        extract_projects_role_date_query = cur.execute(extract_projects_role_date_query)
        print("Project query executed")
        extract_projects_role_date = cur.fetchall()

        print(len(extract_projects_role_date))
        if (len(extract_projects_role_date) > 0):
            team_profile['Project_id'] = extract_projects_role_date
        else:
            team_profile['Project_id'] = ()

        team_details.append(team_profile)

    if (request.method == 'POST'):
        if (request.form['signal'] == 'search'):
            employee_id = request.form['employee_id']
            name = request.form['name']
            email = request.form['email']
            min_amount = request.form['min_amount']
            max_amount = request.form['max_amount']
            position = request.form['position']
            project_name = request.form['project_name']
            # year = request.form['year']

            where_query = f" SELECT * FROM Teams"
            flag = False

            if (employee_id != ''):
                if (flag == False):
                    where_query = where_query + f" WHERE employee_id = \"{employee_id}\""
                else:
                    where_query = where_query + f" AND employee_id = \"{employee_id}\""
                flag = True
            if (name != ''):
                if (flag == False):
                    where_query = where_query + f" WHERE name = \"{name}\""
                else:
                    where_query = where_query + f" AND name = \"{name}\""
                flag = True

            if (email != ''):
                if (flag == False):
                    where_query = where_query + f" WHERE email_id = \"{email}\""
                else:
                    where_query = where_query + f" AND email_id = \"{email}\""
                flag = True

            if min_amount != '' and max_amount != '':
                if flag == False:
                    where_query += f" WHERE salary BETWEEN \'{min_amount}\' AND \'{max_amount}\'"
                else:
                    where_query += f" AND salary BETWEEN \'{min_amount}\' AND \'{max_amount}\'"
                flag = True

            if (position != ''):
                if (flag == False):
                    where_query = where_query + f" WHERE position = \"{position}\""
                else:
                    where_query = where_query + f" AND position = \"{position}\""
                flag = True

            if project_name != '':
                if flag == False:
                    where_query += f" WHERE employee_id IN (SELECT employee_id FROM Organize WHERE event_name = \"{project_name}\")"
                else:
                    where_query += f" AND employee_id IN (SELECT employee_id FROM Organize WHERE event_name = \"{project_name}\")"
                flag = True

            exec_query = cur.execute(where_query)
            print("Search query executed")
            search_results = cur.fetchall()

            updated_team_details = []
            for user in team_details:
                for result in search_results:
                    if user['employee_id'] == result[0]:
                        updated_team_details.append(user)
            team_details = updated_team_details

        elif (request.form['signal'] == 'add'):
            name = request.form['name']
            email = request.form['email']
            salary = request.form['salary']
            position = request.form['position']
            hired_date = request.form['hired_date']

            count_till_now_query = f" SELECT COUNT(*) FROM Teams"
            count_till_now_query = cur.execute(count_till_now_query)
            count_till_now = cur.fetchone()
            if len(count_till_now) > 0:
                count_till_now = count_till_now[0]
            else:
                count_till_now = 0

            add_member_query = f"INSERT INTO Teams (employee_id, name, email_id, salary, position, year_of_joining, year_of_leaving, reason_of_leaving) VALUES (\'{count_till_now + 1}\' , \'{name}\', \'{email}\', \'{salary}\', \'{position}\', \'{hired_date}\', NULL, NULL)"
            add_member_query = cur.execute(add_member_query)
            mysql.connection.commit()

            # add user to staff_table
            password_length = 13
            password = secrets.token_urlsafe(password_length)
            add_staff_password_query = f"INSERT INTO staff_password (EmployeeID, EmployeePassword) VALUES (\'{count_till_now + 1}\', \'{password}\')"
            add_staff_password_query = cur.execute(add_staff_password_query)
            mysql.connection.commit()

            # send email to user
            send_email(email, str(count_till_now + 1), name, password)

            return redirect('/admin/team')

        elif (request.form['signal'] == 'edit'):
            employee_id = request.form['employee_id']
            name = request.form['name']
            email = request.form['email']
            salary = request.form['salary']
            position = request.form['position']
            hired_date = request.form['hired_in']
            left_date = request.form['quit_in']

            if left_date == '':
                left_date = 'NULL'

            project_name = request.form['project_name']
            project_year = request.form['project_year']
            project_role = request.form['role']

            print(f"Project name: {project_name}, Project year: {project_year}, Project role: {project_role}")

            if project_name != '':
                if check_project_year_combination(project_name, project_year) == False:
                    flash(f"Project {project_name} is not available for year {project_year}", 'danger')
                    return redirect('/admin/team')

            update_team_query = f"UPDATE Teams SET name = \'{name}\', email_id = \'{email}\', salary = {salary}, position = \'{position}\', year_of_joining = \'{hired_date}\', year_of_leaving = {left_date} WHERE employee_id = \'{employee_id}\'"
            print(update_team_query)
            update_team_query = cur.execute(update_team_query)
            mysql.connection.commit()

            if project_name != '':
                # check if the employee is already assigned to the project
                check_query = f"SELECT * FROM Organize WHERE employee_id = \'{employee_id}\' AND event_name = \'{project_name}\' AND start_date IN (SELECT start_date FROM Projects WHERE event_name = \"{project_name}\" AND YEAR(start_date) = \'{project_year}\')"
                check_query = cur.execute(check_query)
                check_query = cur.fetchall()
                if len(check_query) == 0:
                    insert_query = f"INSERT INTO Organize (employee_id, event_name, start_date, role) "
                    insert_query += f"VALUES (\'{employee_id}\', \'{project_name}\', (SELECT start_date FROM Projects WHERE event_name = \"{project_name}\" AND YEAR(start_date) = \'{project_year}\'), \'{project_role}\')"
                    insert_query = cur.execute(insert_query)
                    mysql.connection.commit()

            return redirect('/admin/team')

        elif (request.form['signal'] == 'delete'):
            employee_id = request.form['employee_id']
            delete_query = f"DELETE FROM Teams WHERE employee_id = \'{employee_id}\'"
            delete_query_exec = cur.execute(delete_query)

            mysql.connection.commit()


    return render_template('admin/team.html', team_details=team_details, position_names=position_names,
                           project_names=project_names)

if __name__ == '__main__':
    app.run(debug=True)
