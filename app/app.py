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

@app.route("/login",methods=['GET','POST'])
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

@app.route("/admin/volunteers", methods = ['POST', 'GET'])
def volunteers():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Volunteers")

    if result_value > 0:
        userDetails = cur.fetchall()

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