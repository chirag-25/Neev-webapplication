from flask import Flask, render_template, request

app=Flask(__name__)

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
    return "Admin Page"

@app.route("/admin/user")
def user():
    return render_template('admin/user.html')
if __name__=='__main__':
    app.run(debug=True)