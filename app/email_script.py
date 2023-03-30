import smtplib

def send_email(email_id,employee_id,employee_name, employee_password):
   
    # this is wrong 
    with smtplib.SMTP('smtp.gmail.com',587) as server:
        # server.ehlo()
        server.starttls()
        # server.ehlo()
        sender_email='neevtesting1234@gmail.com'
        server.login(sender_email, "nkdpiwwrtdtnkpwi")
        
        body="Hello " + employee_name + ",\n\n" + "Your employee id is " + employee_id +"\n" +"Your password is "+ employee_password+  ".\n\n" + "Regards,\n" + "Admin"
    # server.sendmail("email_id", email_id, "Hello " + employee_name + ",\n\n" + "Your employee id is " + employee_id +  ".\n\n" + "Regards,\n" + "Admin")
        server.sendmail(sender_email, email_id, body)
        
    # server = smtplib.SMTP('smtp.gmail.com', 587)
    # server.starttls()
    # server.login("email_id", "password")
    # server = smtplib.SMTP_SSL('smtp.gmail.com', 465)