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
            return render_template('admin/user.html', userDetails=userDetails, searchResults=search_results)

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
    return render_template('admin/user.html', userDetails=userDetails, searchResults=tuple())
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