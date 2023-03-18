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
        calculate_age_query = f"SELECT TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) FROM Beneficiary WHERE aadhar_id = {user[0]}"
        extract_village_query = f"SELECT pincode, name FROM VillageProfile WHERE pincode = (SELECT pincode FROM belongs WHERE aadhar_id = {user[0]})"
        extract_enrolled_projects_query = f"SELECT * FROM participants WHERE aadhar_id = {user[0]}"
        extract_phone_query = f"SELECT phone_number FROM BeneficiaryPhoneEntity WHERE aadhar_id = {user[0]}"

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

    if (request.method == 'POST'):
        if request.form['signal'] == 'search':
            name = request.form['name']
            aadhar = request.form['aadhar']
            dob = request.form['dob']

            where_query = f"SELECT * FROM Beneficiary "
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

            exec_query = cur.execute(where_query)
            if exec_query > 0:
                search_results = cur.fetchall()
            mysql.connection.commit()
            return render_template('admin/user.html', userDetails=userDetails, searchResults=search_results, profile_details=profile_details)

        elif request.form['signal'] == 'add':
            print(request.form)
            print("addDetails filled!")

            aadhar = request.form['aadhar']
            name = request.form['name']
            dob = request.form['dob']
            education = request.form['education']
            martial = request.form['martial']
            gender = request.form['gender']
            employed = request.form['employed']

            add_query = f"INSERT INTO Beneficiary (aadhar_id, name, date_of_birth, gender, marital_status, education, photo, employed, photo_caption) "
            add_query = add_query + f"VALUES ({aadhar}, \"{name}\", \'{dob}\', \'{gender}\', \'{martial}\', \'{education}\', NULL, \"{employed}\", NULL)"
            print(add_query)

            exec_query = cur.execute(add_query)
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

            edit_query = f"UPDATE Beneficiary "
            edit_query = edit_query + f"SET name = \'{name}\', date_of_birth = \'{dob}\', gender = \'{gender}\', marital_status = \'{martial}\', education = \'{education}\', photo = NULL, employed = \"{employed}\", photo_caption = NULL "
            edit_query = edit_query + f"WHERE aadhar_id = {aadhar}"
            print(edit_query)

            exec_query = cur.execute(edit_query)
            mysql.connection.commit()
            return redirect('/admin/user')
            print("edit")

        elif request.form['signal'] == 'delete':
            print("delete filled!")
            aadhar = request.form['aadhar']
            delete_query = f"DELETE FROM Beneficiary WHERE aadhar_id = {aadhar}"

            print(delete_query)

            exec_query = cur.execute(delete_query)
            mysql.connection.commit()
            return redirect('/admin/user')

    return render_template('admin/user.html', searchResults=tuple(), profile_details=profile_details)
    # return render_template('admin/user.html')


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