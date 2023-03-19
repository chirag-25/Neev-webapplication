from flask import Flask, render_template, request, session, url_for, redirect, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_bcrypt import Bcrypt
import yaml

# import flask_login



app=Flask(__name__)
mysql=MySQL(app)
bcrypt=Bcrypt(app)
app.secret_key='secret_key'


db = yaml.load(open('db.yaml'), Loader=yaml.Loader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']


def check_password(pass_word,id,table):
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query="SELECT * FROM" +" "+table +" " + "WHERE EmployeeID="+str(id)
    cursor.execute(query)
    account=cursor.fetchone()
    if(account):
        if(bcrypt.check_password_hash(account['EmployeePassword'],password=pass_word)):
            return True
    return False


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login",methods=['GET','POST'])
def login():
    if(request.method=='POST'):
        employee_id=request.form["employeeID"]
        password=request.form["password"]
        # pw_hash=bcrypt.generate_password_hash(password,10)
        print(bcrypt.generate_password_hash("sandeep1").decode('utf-8'))
        print(bcrypt.generate_password_hash("dheeraj1").decode('utf-8'))
        print("Employee ID: ",employee_id)
        print("Password: ",password)
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if(check_password(password,employee_id,"admin_password")):
            session['loggedin']=True
            session['id']=employee_id
            # session['username']=account['username']
            return render_template("admin/user.html")
        elif(check_password(password,employee_id,"staff_password")):
            session['loggedin']=True
            session['id']=employee_id
            # session['username']=account['username']
            return render_template("staff/user.html")
        else:
            msg="Incorrect Employee ID/password"
            flash(msg)

        # cursor.execute("SELECT * FROM admin_password WHERE EmployeeID=%s AND EmployeePassword=%s",(employee_id,password))
        # account=cursor.fetchone()

        # if(account):
        #     session['loggedin']=True
        #     session['id']=account['EmployeeID']
        #     # session['username']=account['username']
        #     return render_template("admin/user.html")
        # else:
        #     cursor.execute("SELECT * FROM staff_password WHERE EmployeeID=%s AND EmployeePassword=%s",(employee_id,password))
        #     account=cursor.fetchone()
        #     if(account):
        #         session['loggedin']=True
        #         session['id']=account['EmployeeID']
        #         # session['username']=account['username']
        #         return render_template("staff/user.html")
        #     msg="Incorrect Employee ID/password"
        #     flash(msg)
    return render_template("admin/login.html")



def if_admin():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM admin_password WHERE EmployeeID=%s",(session['id']))
    account=cursor.fetchone()
    if(account):
        return True
    return False

@app.route("/admin")
def admin():
    if 'loggedin' in session and if_admin():
        return render_template("admin/dashboard.html",type="admin")
    elif('loggedin' in session ):
        return render_template("admin/dashboard.html",type="staff")
    else:
        return redirect(url_for('login'))

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