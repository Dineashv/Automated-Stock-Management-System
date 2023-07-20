import json
import mysql.connector
from flask import Flask,render_template,send_file,request,make_response,url_for
from flask_mysqldb import MySQL
import os
from io import BytesIO
import pdfkit
from datetime import datetime,date
from decimal import Decimal
import io
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Connection to MY SQL Workbench(Database)
conn_obj = mysql.connector.connect(host="localhost", user="root", passwd="Aa@,00001111",database="first1")
cur_obj = conn_obj.cursor(buffered=True)  
app=Flask(__name__)

billing_items = []
products = []
@app.route('/')
def hello_world():
    return render_template('index.html')
@app.route('/stock')
def stock():
    start_time = datetime.now()  # Capture the start time of the request
    # Your code to process the request
    end_time = datetime.now()  # Capture the end time of the request
    response_time = (end_time - start_time).total_seconds() * 1000  # Calculate the response time in milliseconds
    return f"Response time: {response_time} ms"
@app.route('/dashboard')
def dashboard():
    cur_obj.execute('SELECT MAX(bill_no), SUM(total), SUM(tax) FROM invoices')

    # Fetch the results and assign them to variables
    
    results = cur_obj.fetchone()
    invoice = results[0]
    sales = int(results[1])
    tax = int(results[2])

    cur_obj.execute('SELECT SUM(profit) FROM product')
    valuee=cur_obj.fetchone()
    prfit=int(valuee[0])
    
    
    cur_obj.execute("SELECT p_id,exp, p_name, DATEDIFF(exp, NOW()) AS days_left FROM product ORDER BY days_left ASC LIMIT 10")
    exp = cur_obj.fetchall()
   
    cur_obj.execute("SELECT p_id,p_name,sold FROM product ORDER BY sold DESC LIMIT 10")
    top = cur_obj.fetchall()
    return render_template('dashboard.html',invoice=invoice,sales=sales,profit=prfit,tax=tax, exp=exp, top=top)

@app.route('/home',methods = ['GET','POST'])
def home():
     if request.method=="POST":
        user= request.form["user"]
        password = request.form["pass"]
        if user=="admin" and password == "123":
            cur_obj.execute('SELECT MAX(bill_no), SUM(total), SUM(tax) FROM invoices')

    # Fetch the results and assign them to variables
    
            results = cur_obj.fetchone()
            invoice = results[0]
            sales = int(results[1])
            tax = int(results[2])

            cur_obj.execute('SELECT SUM(profit) FROM product')
            valuee=cur_obj.fetchone()
            prfit=int(valuee[0])
    

            cur_obj.execute("SELECT exp,p_name FROM product")
            exp = cur_obj.fetchall()
   
            cur_obj.execute("SELECT p_name,sold FROM product ORDER BY sold DESC LIMIT 10")
            top = cur_obj.fetchall()
            return render_template('dashboard.html',invoice=invoice,sales=sales,profit=prfit,tax=tax, exp=exp, top=top)
        else:
            return "Invalid Login Credentials"
# @app.route('/dashboard',methods=['GET','POST'])


@app.route('/manage',methods = ['GET','POST'])
def manage():
    result = {
        "p_id":"",
        "p_name":"",
        "qty":"",
        "min":"",
        "max":"",
        "buy":"",
        "sell":"",
        "exp":"",
        "s_name":"",
        "s_mail":""

    }
    return render_template('manage.html',response=result)
@app.route('/add',methods = ['GET','POST'])
def add():
    result = {
        "p_id":"",
        "p_name":"",
        "qty":"",
        "min":"",
        "max":"",
        "buy":"",
        "sell":"",
        "exp":"",
        "s_name":"",
        "s_mail":""

    }
    if request.method=="POST":
        p_id=request.form["p_id"]
        p_name=request.form["p_name"]
        qty=request.form["qty"]
        min=request.form["min"]
        max=request.form["max"]
        buy=request.form["buy"]
        sell=request.form["sell"]
        exp=request.form["exp"]
        s_name=request.form["s_name"]
        s_mail=request.form["s_mail"]
        sold=0
        profit=0
        sql = "INSERT INTO product (p_id, p_name, qty, min, max, buy, sell, exp, s_name, s_mail,sold,profit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)"
        val = (p_id, p_name, qty, min, max, buy, sell, exp, s_name, s_mail,sold,profit)
        cur_obj.execute(sql,val)
        conn_obj.commit()
        return render_template('manage.html',response=result)
    
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    result = {
        "p_id":"",
        "p_name":"",
        "qty":"",
        "min":"",
        "max":"",
        "buy":"",
        "sell":"",
        "exp":"",
        "s_name":"",
        "s_mail":""

    }
    if request.method=="POST":
        p_id=request.form["p_id"]
        cur_obj.execute('DELETE FROM product WHERE p_id = %s', (p_id,))
        conn_obj.commit()
        return render_template('manage.html',response=result)

@app.route('/update', methods=['GET', 'POST'])
def update():
    result = {
        "p_id":"",
        "p_name":"",
        "qty":"",
        "min":"",
        "max":"",
        "buy":"",
        "sell":"",
        "exp":"",
        "s_name":"",
        "s_mail":""

    }
    if request.method=="POST":
        p_id=request.form["p_id"]
        p_name=request.form["p_name"]
        qty=request.form["qty"]
        min=request.form["min"]
        max=request.form["max"]
        buy=request.form["buy"]
        sell=request.form["sell"]
        exp=request.form["exp"]
        s_name=request.form["s_name"]
        s_mail=request.form["s_mail"]
        
        #sql = "UPDATE faculty (name, department, role, phone_number, email, password) VALUES where id1=id1 (%s, %s, %s, %s, %s, %s)"
        sql = "UPDATE product SET p_name=%s ,qty=%s, min=%s, max=%s, buy=%s, sell=%s, exp=%s, s_name=%s, s_mail=%s  WHERE p_id = %s" 
        val = (p_name, qty, min, max, buy, sell, exp, s_name, s_mail,p_id,)
        cur_obj.execute(sql,val)
        conn_obj.commit()
    return render_template('manage.html',response=result)

@app.route('/search', methods=['GET', 'POST'])
def search():
    search = request.form['search_id']
    cur_obj.execute("SELECT * FROM product where p_id = %s",(search,))
    result = cur_obj.fetchall()
    for row in result:
        data = {
        "p_id":row[0],
        "p_name":row[1],
        "qty":row[2],
        "min":row[3],
        "max":row[4],
        "buy":row[5],
        "sell":row[6],
        "exp":row[7],
        "s_name":row[8],
        "s_mail":row[9]
    }
    msg=''
    data1 = {
        "p_id":"",
        "p_name":"",
        "qty":"",
        "min":"",
        "max":"",
        "buy":"",
        "sell":"",
        "exp":"",
        "s_name":"",
        "s_mail":""
    }
    if(len(result)>0):
        msg+="Your Result"
        return render_template('manage.html',response=data,msg=msg)
    else:
        msg+="Data Not Available"
        return render_template('manage.html',response=data1,msg=msg)
    # return render_template('manage.html',response=data)


@app.route('/invoice', methods=['GET', 'POST'])
def invoice():
    customer_name = request.form['customer_name']
    customer_address = request.form['customer_address']
    product_name = request.form.getlist('product_name[]')
    product_quantity = list(map(int, request.form.getlist('product_quantity[]')))
    product_price = list(map(float, request.form.getlist('product_price[]')))

    #update products in Database
    for p_name, qty in zip(product_name, product_quantity):
        quant=qty
        cur_obj.execute("UPDATE product SET qty = qty - %s,sold=sold+%s WHERE p_name = %s", (qty,quant,p_name,))
        cur_obj.execute("UPDATE product SET profit = (sold*(sell-buy)) WHERE p_name=%s",(p_name,))
        conn_obj.commit()


    # cur_obj.execute("SELECT sold FROM product WHERE p_name=%s",(product_name))
    # sold=cur_obj.fetchone()
    # old_sold=sold[0]
    # new_sold=old_sold + product_quantity[]
    # cur_obj.execute("UPDATE product SET sold = %s, WHERE p_name=%s",(new_sold,product_name))
    # conn_obj.commit()
    
    subtotal = sum([quantity * price for quantity, price in zip(product_quantity, product_price)])
    tax_amount = subtotal * 0.07
    total = subtotal + tax_amount

    
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': 'UTF-8',
        'no-outline': None
    }
    
    data =[]
    z=0
    for X in range(len(product_name)):
       data.insert(z,{'product_name':product_name[X], 'product_quantity':product_quantity[X], 'product_price': product_price[X], 'amount':(product_quantity[X] * product_price[X])})
       z=z+1
    config = pdfkit.configuration(wkhtmltopdf="C:\\Users\\dinea\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")


    html = render_template('bill.html', customer_name=customer_name, customer_address=customer_address, product_name=product_name, product_quantities=product_quantity, product_prices=product_price, subtotal=subtotal, tax_="7", tax_amount=tax_amount, total=total,response=data)
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        
    cur_obj.execute('INSERT INTO invoices (timestamp, customer_name, customer_address, subtotal, tax, total, pdf) VALUES (%s, %s, %s, %s, %s, %s, %s)', (timestamp, customer_name, customer_address, subtotal, tax_amount, total, pdf))
    conn_obj.commit()
#Send automatic order when product is less
    cur_obj.execute("SELECT p_name, qty, buy, max, s_name, s_mail FROM product WHERE qty < min")
    for p_name, qty, buy, max, s_name, s_mail in cur_obj.fetchall():
        units_needed = max - qty
        s_total=units_needed * buy
        tax=s_total * 0.07
        total=s_total + tax
        pdf_content = render_template('purchase.html',p_name=p_name,units_needed=units_needed,buy=buy,s_total=s_total,tax=tax,total=total,s_name=s_name,s_mail=s_mail)

     
        config = pdfkit.configuration(wkhtmltopdf="C:\\Users\\dinea\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdfkit.from_string(pdf_content, f'{p_name}.pdf',configuration=config)

        
        smtp_host = 'smtp.gmail.com' 
        smtp_port = 587 
        smtp_user = 'supermarketproject2023@gmail.com' 
        smtp_password = 'bihszmckrtcltkmr' 

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)

        msg = MIMEMultipart()
        msg['From'] = 'supermarketproject2023@gmail.com'
        msg['To'] = s_mail
        msg['Subject'] = f'Order needed for {p_name}'

        body = f"Hello {s_name} we are from Supermarket, Please supply {units_needed} units of {p_name} to our warehouse. We are running out of stocks"

        msg.attach(MIMEText(body, 'plain'))

        with open(f'{p_name}.pdf', 'rb') as f:
            attachment = MIMEApplication(f.read(), _subtype='pdf')
            attachment.add_header('Content-Disposition', 'attachment', filename=f'{p_name}.pdf')
            msg.attach(attachment)

        server.sendmail(smtp_user, s_mail, msg.as_string())
        server.quit()
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        
        cur_obj.execute('INSERT INTO orders (timestamp, s_name,s_mail,tax, total, pdf) VALUES (%s, %s, %s, %s, %s, %s)', (timestamp,s_name,s_mail,tax, total, pdf_content))
        conn_obj.commit()
        

    # Return PDF invoice to client
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=invoice.pdf'
    return response
# def automatic_order():
#     print("Yes...................................................................................................")
#     cur_obj.execute("SELECT p_name, qty, buy, max, s_name, s_mail FROM product WHERE qty < min")
#     for p_name, qty, buy, max, s_name, s_mail in cur_obj.fetchall():
#         units_needed = max - qty
#         s_total=units_needed * buy
#         tax=s_total * 0.07
#         total=s_total + tax
#         pdf_content = render_template('purchase.html',p_name=p_name,units_needed=units_needed,buy=buy,s_total=s_total,tax=tax,total=total,s_name=s_name,s_mail=s_mail)

     
#         config = pdfkit.configuration(wkhtmltopdf="C:\\Users\\dinea\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
#         pdfkit.from_string(pdf_content, f'{p_name}.pdf',configuration=config)

        
#         smtp_host = 'smtp.gmail.com' 
#         smtp_port = 587 
#         smtp_user = 'supermarketproject2023@gmail.com' 
#         smtp_password = 'bihszmckrtcltkmr' 

#         server = smtplib.SMTP(smtp_host, smtp_port)
#         server.starttls()
#         server.login(smtp_user, smtp_password)

#         msg = MIMEMultipart()
#         msg['From'] = 'supermarketproject2023@gmail.com'
#         msg['To'] = s_mail
#         msg['Subject'] = f'Order needed for {p_name}'

#         body = f"Hello {s_name} we are from Supermarket, Please supply {units_needed} units of {p_name} to our warehouse. We are running out of stocks"

#         msg.attach(MIMEText(body, 'plain'))

#         with open(f'{p_name}.pdf', 'rb') as f:
#             attachment = MIMEApplication(f.read(), _subtype='pdf')
#             attachment.add_header('Content-Disposition', 'attachment', filename=f'{p_name}.pdf')
#             msg.attach(attachment)

#         server.sendmail(smtp_user, s_mail, msg.as_string())
#         server.quit()
#         now = datetime.now()
#         timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        
#         cur_obj.execute('INSERT INTO orders (timestamp, s_name,s_mail,s_total,tax, total, pdf) VALUES (%s, %s, %s, %s, %s, %s, %s)', (timestamp,s_name,s_mail,s_total,tax, total, pdf_content))
#         conn_obj.commit()
defective_products=[]
defective_items=[]
@app.route('/defective', methods=['GET','POST'])
def defective():
    defective_products.clear()
    cur_obj.execute("SELECT p_name FROM product")
    rows=cur_obj.fetchall()
    for row in rows:
         defective_products.append(row[0])
    cur_obj.execute("SELECT p_id,exp,p_name,qty FROM defective where profit > 0")
    items=cur_obj.fetchall()
    cur_obj.execute("SELECT SUM(price) FROM defective")
    sell=cur_obj.fetchone()[0]
    cur_obj.execute("SELECT SUM(profit) FROM defective")
    usual_profit=cur_obj.fetchone()[0]
    combo_profit=int(usual_profit/3)
    offer_price=(sell-usual_profit)+combo_profit
    return render_template('defective.html',products=defective_products,items=items,usual_profit=usual_profit,combo_profit=combo_profit,normal_price=sell,offer_price=offer_price,)

@app.route('/expiry', methods=['GET','POST'])
def expiry():
    cur_obj.execute("SELECT p_name,buy,sell FROM product WHERE DATEDIFF(exp, NOW()) <= 20")
    for p_name, buy, sell in cur_obj.fetchall():
        product=p_name
        profit=sell-buy
        offer_price=int(profit/3)
        sell_rate=buy+offer_price
        discount=((buy-sell_rate)/buy)*100
        offer_pdf = render_template('offer.html',product=product,price=sell_rate,discount=discount)
        config = pdfkit.configuration(wkhtmltopdf="C:\\Users\\dinea\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdfkit.from_string(offer_pdf, f'{p_name}.pdf',configuration=config)

        cur_obj.execute('SELECT customer_name,customer_address FROM invoices')
        for customer_name,customer_address in cur_obj.fetchall():
            smtp_host = 'smtp.gmail.com' 
            smtp_port = 587 
            smtp_user = 'supermarketproject2023@gmail.com' 
            smtp_password = 'bihszmckrtcltkmr' 

            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)

            msg = MIMEMultipart()
            msg['From'] = 'supermarketproject2023@gmail.com'
            msg['To'] = customer_address
            msg['Subject'] = 'Hurry! Grab the Deal..'

            body = f"Hello {customer_name} we are from Supermarket, We're excited to offer a limited-time discount on our top-selling Product. Find the Offer Details in bellow attached document"

            msg.attach(MIMEText(body, 'plain'))

            with open(f'{p_name}.pdf', 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype='pdf')
                attachment.add_header('Content-Disposition', 'attachment', filename=f'{p_name}.pdf')
                msg.attach(attachment)

            server.sendmail(smtp_user, customer_address, msg.as_string())
            server.quit() 
    defective_products.clear()
    cur_obj.execute("SELECT p_name FROM product")
    rows=cur_obj.fetchall()
    for row in rows:
         defective_products.append(row[0])
    cur_obj.execute("SELECT p_id,exp,p_name,qty FROM defective where profit > 0")
    items=cur_obj.fetchall()
    cur_obj.execute("SELECT SUM(price) FROM defective")
    sell=cur_obj.fetchone()[0]
    cur_obj.execute("SELECT SUM(profit) FROM defective")
    usual_profit=cur_obj.fetchone()[0]
    combo_profit=int(usual_profit/3)
    offer_price=(sell-usual_profit)+combo_profit
    return render_template('defective.html',products=defective_products,items=items,usual_profit=usual_profit,combo_profit=combo_profit,normal_price=sell,offer_price=offer_price,)
  


@app.route('/add_defective', methods=['GET','POST'])
def add_defective():
    product_name=request.form['product_name']
    quantity = int(request.form['product-quantity'])
    cur_obj.execute("SELECT p_id FROM product WHERE p_name = %s", (product_name,))
    p_id=cur_obj.fetchone()[0]
    cur_obj.execute("SELECT exp FROM product WHERE p_name = %s", (product_name,))
    exp=cur_obj.fetchone()[0]
    cur_obj.execute("SELECT buy FROM product WHERE p_name = %s", (product_name,))
    buy=cur_obj.fetchone()[0]
    cur_obj.execute("SELECT sell FROM product WHERE p_name = %s", (product_name,))
    sell=cur_obj.fetchone()[0]
    profit=sell-buy
    cur_obj.execute("UPDATE product SET qty = qty - %s WHERE p_name = %s", (quantity,product_name,))
    conn_obj.commit()  
    cur_obj.execute("SELECT sell from product WHERE p_name = %s", (product_name,))
    price=cur_obj.fetchone()[0]
    cur_obj.execute("INSERT INTO defective (p_id,exp,p_name,qty,profit,price) VALUES(%s,%s,%s,%s,%s,%s)",(p_id,exp,product_name,quantity,profit,price,))
    conn_obj.commit()  
    defective_products.clear()
    
    cur_obj.execute("SELECT p_name FROM product")
    rows=cur_obj.fetchall()
    for row in rows:
         defective_products.append(row[0])
    cur_obj.execute("SELECT SUM(profit) FROM defective")
    usual_profit=cur_obj.fetchone()[0]
    combo_profit=int(usual_profit/3)
    offer_price=buy+combo_profit
    cur_obj.execute("SELECT p_id,exp,p_name,qty FROM defective where profit > 0")
    items=cur_obj.fetchall()
    return render_template('defective.html',products=defective_products,items=items,usual_profit=usual_profit,combo_profit=combo_profit,normal_price=sell,offer_price=offer_price,)
@app.route('/show_offer', methods=['GET','POST'])
def show_offer():
    cur_obj.execute("SELECT SUM(profit) FROM defective")
    usual_profit=cur_obj.fetchone()
    combo_profit=int(usual_profit/3)
    return render_template('defective.html', usual_profit=usual_profit,combo_profit=combo_profit,)


@app.route('/page', methods=['GET','POST'])
def page():
    billing_items.clear()
    products.clear()
    cur_obj.execute("SELECT p_name FROM product")
    rows=cur_obj.fetchall()
	

    for row in rows:
         products.append(row[0])
    return render_template('billing_system.html',products=products)

@app.route('/add_to_billing', methods=['GET','POST'])
def add_bill():
	customer_name = request.form['customer_name']
	customer_address = request.form['customer_address']
	product_name = request.form['product_name']
	quantity = int(request.form['quantity'])
    
	cur_obj.execute("SELECT sell FROM product WHERE p_name = %s", (product_name,))
	price = cur_obj.fetchone()[0]

	# Calculate the total price of the selected product based on quantity
	total_price = price * quantity

	# Add the new item to the billing_items list
	billing_items.append({'product_name': product_name, 'price': price, 'quantity': quantity, 'total_price' : total_price})
		# Calculate subtotal
	subtotal = sum(item['total_price'] for item in billing_items)
	# Calculate tax
	tax_rate = 7  # Assume tax rate is 10%
	tax = subtotal * (tax_rate/100)
        
	# Calculate grand total
	grand_total = subtotal + tax
    
	
	# return render_template('test.html',products=products,customer_name=customer_name,customer_address=customer_address billing_items=billing_items, subtotal=subtotal, tax_rate=tax_rate, tax=tax, grand_total=grand_total)
	return render_template('billing_system.html',products=products,customer_name=customer_name,customer_address=customer_address, billing_items=billing_items, subtotal=subtotal, tax_rate=tax_rate, tax=tax, grand_total=grand_total)

@app.route('/bill', methods=['GET','POST'])
def bill():
    customer_name = request.form['customer_name']
    customer_address = request.form['customer_address']
    for x in billing_items:
         qty=x['quantity']
         p_name=x['product_name']
         quant=qty
         cur_obj.execute("UPDATE product SET qty = qty - %s,sold=sold+%s WHERE p_name = %s", (qty,quant,p_name,))
         cur_obj.execute("UPDATE product SET profit = (sold*(sell-buy)) WHERE p_name=%s",(p_name,))
         conn_obj.commit()    
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': 'UTF-8',
        'no-outline': None
    }
    
    config = pdfkit.configuration(wkhtmltopdf="C:\\Users\\dinea\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    subtotal = sum(item['total_price'] for item in billing_items)
    tax = subtotal * (7/100)
    grand_total = subtotal + tax                   
    now = datetime.now().date()
    date = now.strftime('%Y-%m-%d')
    time=datetime.now().time()
    timenow=time.strftime('%H:%M:%S')
    cur_obj.execute("SELECT MAX(bill_no) FROM invoices")
    bill=cur_obj.fetchone()[0]
    bill_no=bill+1
    html = render_template('bill.html', customer_name=customer_name,bill_no=bill_no,date=date ,timenow=timenow, customer_address=customer_address, subtotal=subtotal, tax_amount=tax, total=grand_total,response=billing_items)
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)
    
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        
    cur_obj.execute('INSERT INTO invoices (bill_no,timestamp, customer_name, customer_address, subtotal, tax, total, pdf) VALUES (%s,%s, %s, %s, %s, %s, %s, %s)', (bill_no,timestamp, customer_name, customer_address, subtotal, tax, grand_total, pdf))
    conn_obj.commit()
    #Send automatic order when product is less
    cur_obj.execute("SELECT p_name, qty, buy, max, s_name, s_mail FROM product WHERE qty < min AND orders IS NULL")
    for p_name, qty, buy, max, s_name, s_mail in cur_obj.fetchall():
        units_needed = max - qty
        s_total=units_needed * buy
        tax=s_total * 0.07
        total=s_total + tax
        cur_obj.execute('SELECT MAX(order_no) FROM orders')
        id=cur_obj.fetchone()[0]
        order_id=id+1
        pdf_content = render_template('purchase.html',order_id=order_id,p_name=p_name,date=date,timenow=timenow,units_needed=units_needed,buy=buy,s_total=s_total,tax=tax,total=total,s_name=s_name,s_mail=s_mail)

        cur_obj.execute('UPDATE product SET orders =1 WHERE qty < min AND orders IS NULL')
        conn_obj.commit()
        # config = pdfkit.configuration(wkhtmltopdf="C:\\Users\\dinea\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdf_order=pdfkit.from_string(pdf_content, False, options=options, configuration=config)
        pdfkit.from_string(pdf_content, f'{p_name}.pdf',configuration=config)

        
        smtp_host = 'smtp.gmail.com' 
        smtp_port = 587 
        smtp_user = 'supermarketproject2023@gmail.com' 
        smtp_password = 'bihszmckrtcltkmr' 

        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)

        msg = MIMEMultipart()
        msg['From'] = 'supermarketproject2023@gmail.com'
        msg['To'] = s_mail
        msg['Subject'] = f'Order needed for {p_name}'

        body = f"Hello {s_name} we are from Supermarket, Please supply {units_needed} units of {p_name} to our warehouse. We are running out of stocks"

        msg.attach(MIMEText(body, 'plain'))

        with open(f'{p_name}.pdf', 'rb') as f:
            attachment = MIMEApplication(f.read(), _subtype='pdf')
            attachment.add_header('Content-Disposition', 'attachment', filename=f'{p_name}.pdf')
            msg.attach(attachment)

        server.sendmail(smtp_user, s_mail, msg.as_string())
        server.quit()
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        
        cur_obj.execute('INSERT INTO orders (order_no, timestamp, s_name,s_mail,tax, total, pdf) VALUES (%s, %s, %s, %s, %s, %s, %s)', (id, timestamp,s_name,s_mail,tax, total, pdf_order))
        conn_obj.commit()
        
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=invoice.pdf'
    return response   
    

@app.route('/billing_system',methods = ['GET','POST'])
def billing():
    return render_template('billing_system.html')

@app.route('/invoicepage', methods = ['GET', 'POST'])
def invoicepage():
    cur_obj.execute("SELECT bill_no,timestamp,customer_name,customer_address,subtotal,tax,total FROM invoices")
    rows = cur_obj.fetchall()
    return render_template('invoicepage.html', rows=rows)

@app.route('/view_pdf/<int:bill_no>')
def view_pdf(bill_no):
    cur_obj.execute("SELECT pdf FROM invoices WHERE bill_no=%s", (bill_no,))
    row = cur_obj.fetchone()[0]
    return send_file(
        io.BytesIO(row),
        mimetype="application/pdf",
        as_attachment=False,
        download_name="document.pdf"
    )

@app.route('/myorders', methods = ['GET', 'POST'])
def myorders():
    cur_obj.execute("SELECT order_no,timestamp,s_name,s_mail,tax,total FROM orders")
    rows = cur_obj.fetchall()
    return render_template('myorders.html', rows=rows)

@app.route('/view_order/<int:order_no>')
def view_order(order_no):
    cur_obj.execute("SELECT pdf FROM orders WHERE order_no=%s", (order_no,))
    rows = cur_obj.fetchone()[0]
    return send_file(
        io.BytesIO(rows),
        mimetype="application/pdf",
        as_attachment=False,
        download_name="order.pdf"
    )
    # with open('temp.pdf', 'wb') as f:
    #     f.write(pdf_data)
    
    # # Serve the file to the user as a PDF response
    # with open('temp.pdf', 'rb') as f:
    #     response = make_response(f.read())
    #     response.htffhghggfchi sunagukfrinuf guwhfs7ihcwrfwbscjsyi guywefgicknaedjcguy sbdcsydc eaders.set('Content-Type', 'application/pdf')
    #     response.headers.set('Content-Disposition', 'inline', filename='temp.pdf')
    #     return response


if __name__ == '__main__':
    app.run(debug=True)

