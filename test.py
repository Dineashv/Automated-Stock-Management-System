from flask import Flask, render_template, request, redirect, url_for,make_response
import mysql.connector
import pdfkit
from datetime import datetime

conn_obj = mysql.connector.connect(host="localhost", user="root", passwd="Aa@,00001111",database="first1")
cur_obj = conn_obj.cursor() 

app = Flask(__name__)

calcultaions=[]
billing_items = []
products = []

@app.route('/')
def home():
	return render_template('a.html')


@app.route('/page', methods=['GET','POST'])
def page():
    billing_items.clear()
    products.clear()
    cur_obj.execute("SELECT p_name FROM product")
    rows=cur_obj.fetchall()
	

    for row in rows:
         products.append(row[0])
    return render_template('test.html',products=products)

@app.route('/add_to_billing', methods=['GET','POST'])
def add():
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
	return render_template('test.html',products=products,customer_name=customer_name,customer_address=customer_address, billing_items=billing_items, subtotal=subtotal, tax_rate=tax_rate, tax=tax, grand_total=grand_total)

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


    html = render_template('bill.html', customer_name=customer_name, customer_address=customer_address, subtotal=subtotal, tax_amount=tax, total=grand_total,response=billing_items)
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

        
    cur_obj.execute('INSERT INTO invoices (timestamp, customer_name, customer_address, subtotal, tax, total, pdf) VALUES (%s, %s, %s, %s, %s, %s, %s)', (timestamp, customer_name, customer_address, subtotal, tax, grand_total, pdf))
    conn_obj.commit()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=invoice.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)
