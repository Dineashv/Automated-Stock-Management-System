from flask import Flask,render_template
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pdfkit
import mysql.connector

from datetime import datetime

conn_obj = mysql.connector.connect(host="localhost", user="root", passwd="Aa@,00001111",database="first1")
cur_obj = conn_obj.cursor()   
app=Flask(__name__)

@app.route('/')
def check_inventory():

    cur_obj.execute("SELECT p_name, qty, buy, max, s_name, s_mail FROM product WHERE qty < min")
    for p_name, qty, buy, max, s_name, s_mail in cur_obj.fetchall():
        units_needed = max - qty
        s_total=units_needed * buy
        tax=s_total * 0.07
        total=s_total + tax
        pdf_content = render_template('purchase.html',p_name=p_name,units_needed=units_needed,buy=buy,s_total=s_total,tax=tax,total=total,s_name=s_name,s_mail=s_mail)

     
        config = pdfkit.configuration(wkhtmltopdf="C:\\Users\\dinea\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdfkit.from_string(pdf_content, f'{p_name}.pdf',configuration=config)

        
        smtp_host = 'smtp.gmail.com' # replace with your SMTP host
        smtp_port = 587 # replace with your SMTP port number
        smtp_user = 'supermarketproject2023@gmail.com' # replace with your email address
        smtp_password = 'bihszmckrtcltkmr' # replace with your email password

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)

        msg = MIMEMultipart()
        msg['From'] = 'supermarketproject2023@gmail.com'
        msg['To'] = s_mail
        msg['Subject'] = f'Order needed for {p_name}'

        body = f"Please supply {units_needed} units of {p_name} to our warehouse."

        msg.attach(MIMEText(body, 'plain'))

        with open(f'{p_name}.pdf', 'rb') as f:
            attachment = MIMEApplication(f.read(), _subtype='pdf')
            attachment.add_header('Content-Disposition', 'attachment', filename=f'{p_name}.pdf')
            msg.attach(attachment)

        server.sendmail(smtp_user, s_mail, msg.as_string())
        server.quit()
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        
    cur_obj.execute('INSERT INTO orders (timestamp, s_name,s_mail, total, pdf) VALUES (%s, %s, %s, %s, %s)', (timestamp,s_name,s_mail, total, pdf_content))
    conn_obj.commit()
    
    

    

if __name__ == '__main__':
    app.run(debug=True)
