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

@app.route("/admin/user",methods=['POST','GET'])
def user():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM Beneficiary")
    if (resultValue > 0):
        userDetails = cur.fetchall()
    if(request.method=='POST'):
        
        form_data=request.json
        
        if(form_data['signal']=='search'):
            print("this is search query")
        elif(form_data['signal']=='editUser'):
            print("this is edit query")  
        elif(form_data['signal']=='addUser'):
            print("ADD DATA")
    return render_template('admin/user.html', userDetails=userDetails)

### Add new user
@app.route("/",methods=['POST'])
def insert():
    if (request.method == 'POST'):
        aadhar = request.form['aadhar']
        name = request.form['name']
        dob = request.form['dob']
        education = request.form['education']
        martial = request.form['martial']
        gender = request.form['gender']
        employed = request.form['employed']
        cur = mysql.connection.cursor()
        
        query = "INSERT INTO Beneficiary(aadhar_id, name, date_of_birth, gender, marital_status, education, photo, employed, photo_caption) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s)"
        cur.execute(query, (aadhar, name, dob, gender, martial, education, None, employed, None))               
        mysql.connection.commit()
        cur.close()
        return redirect('user')

if __name__=='__main__':
    app.run(debug=True)