from flask import Flask, render_template, request, redirect
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

@app.route("/admin/funding", methods = ['POST', 'GET'])
def funding():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM Funding")
    if result_value > 0:
        userDetails = cur.fetchall()
    
    profileDetails = []
    for user in userDetails:
        user_profile = {'email': user[0], 'amount': user[1], 'benefactor': user[2], 'date': user[3]}
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

        

        if(len(calculate_events) > 0):
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
                    where_query +=  f" WHERE funder_name = \'{benefactor}\' "
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
            print(search_results)
            
            updated_profile_details = []
            for user in profileDetails:
                for result in search_results:
                    print("email", result[0])
                    if user['email'] == result[0]:
                        updated_profile_details.append(user)
            profileDetails = updated_profile_details
            
            return render_template('admin/funding.html', userDetails=userDetails, profileDetails = profileDetails)
        elif request.form['signal'] == 'add':
            print(request.form)
            print("addDetails filled!")
            
            benefactor = request.form['name']
            amount = request.form['amount_add']
            email = request.form['email']
            date = request.form['funding_date']
            
            funding_to = request.form['project']
            
            add_query = f"INSERT INTO Funding (email_id, amount, funder_name, date) "
            add_query = add_query + f"VALUES (\"{email}\", \"{amount}\", \'{benefactor}\', \"{date}\")"
            exec_query = cur.execute(add_query)
            mysql.connection.commit()
            
            # add_project_query = f"INSERT INTO Sponsors (email_id, event_name, start_date)"
            # add_project_query = add_project_query + f"VALUES (\"{email}\", \"{funding_to}\", \"{date}\" )"
            # add_project_query = add_project_query + f" WHERE email_id = \"{email}\" "
            
            add_project_query = f"INSERT INTO Sponsors (email_id, event_name, start_date) "
            # assumption is taken here that beneficiary can only participate in current year's project
            add_project_query = add_project_query + f"VALUES (\"{email}\", \"{funding_to}\", (SELECT start_date FROM Projects WHERE event_name = \"{funding_to}\" AND YEAR(start_date) = YEAR(\'{date}\')))"
            exec_add_project_query = cur.execute(add_project_query)
            mysql.connection.commit()

            return redirect('/admin/funding')
        elif request.form['signal'] == 'edit':
            print("iN edit")
            benefactor = request.form['benefactor']
            amount = request.form['amount']
            email = request.form['email']
            date = request.form['funding_date']
 
            edit_query = f"UPDATE Funding "
            edit_query = edit_query + f"SET funder_name = \'{benefactor}\', amount = \'{amount}\', email_id = \'{email}\', date = \'{date}\' "
            edit_query = edit_query + f"WHERE email_id = \'{email}\'"

            exec_query = cur.execute(edit_query)
            mysql.connection.commit()
            return redirect('/admin/funding')
        elif request.form['signal'] == 'delete':
            email = request.form['email']
            delete_query = f"DELETE FROM Funding WHERE email_id = \'{email}\' "
            exec_query = cur.execute(delete_query)
            mysql.connection.commit()
            return redirect('/admin/funding')
        # print(profileDetails)
    return render_template('admin/funding.html', userDetails=userDetails, profileDetails = profileDetails, calculate_events = calculate_events,calculate_sponsors = calculate_sponsors)


@app.route("/admin/volunteers")
def volunteers():
    return render_template("admin/volunteers.html")


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