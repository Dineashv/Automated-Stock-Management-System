from flask import Flask, render_template
import mysql.connector
import os
os.environ["FLASK_DEBUG"] = "development"



app = Flask(__name__)


# Connect to MySQL database
conn_obj = mysql.connector.connect(host="localhost", user="root", passwd="Aa@,00001111",database="first1")
cur_obj = conn_obj.cursor() 


@app.route('/')
def display_tables():
    p_lst=[]
    d_lst=[]
    new_lst=[]
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

    # today = datetime.now()

    # Calculate the date 7 days from now
    # seven_days_from_now = today + datetime.timedelta(days=14)

    #expiry 
    cur_obj.execute('SELECT exp FROM product')
    row=cur_obj.fetchall()
    from datetime import date,datetime
    str_d2 = date.today()
    day1=datetime.strptime(str(str_d2), "%Y-%m-%d")
    # print(today)
    for result in row:
        date_object = result[0]
        date_string = date_object.strftime('%Y-%m-%d')
        # date_string=result[0]
    # Convert the date string to a datetime object
        date_from_db = datetime.strptime(str(date_string), '%Y-%m-%d')

    # Calculate the difference between the dates in days
        diff = day1 - date_from_db
        days_left=(f'{diff.days}')
        day_left1=int(days_left)
        if day_left1 <= 14 :
            cur_obj.execute('SELECT buy, sell,p_name FROM product')
            date=cur_obj.fetchall()
            for element in date:
                cost_price = element[0]
                current_selling_price = element[1]
                p_name=element[2]
            # exp_date=date[3]
            # exp = str(datetime.strptime(str(exp_date), "%Y-%m-%d"))
            # days_left=(str(date.today()))- exp
                new_selling_price=0
                Discount=0

                profit=current_selling_price - cost_price
                new_selling_price+=int(cost_price + (profit/2))
                Discount +=int(((current_selling_price - new_selling_price) / current_selling_price) * 100)
                p_lst.append(p_name)
                
            p_lst.append(Discount)
            p_lst.append(new_selling_price)
    print(p_lst)


    # cur_obj.execute('SELECT buy, sell,p_name,exp FROM product')
    # date=cur_obj.fetchall()

    # cost_price = date[0]
    # current_selling_price = date[1]
    # p_name=date[2]
    # exp_date=date[3]
    # exp = datetime.strptime(str(exp_date), "%Y-%m-%d")
    # days_left=str(date.today()) - exp
    # new_selling_price=0
    # Discount=0

    # if days_left <= 14 :
    #     profit=current_selling_price - cost_price
    #     new_selling_price+=int(cost_price + (profit/2))
        
    # profit=current_selling_price - cost_price
    # new_selling_price=int(cost_price + (profit/2))
    

    # Discount +=int(((current_selling_price - new_selling_price) / current_selling_price) * 100)

    return render_template('practice.html',invoice=invoice,sales=sales,profit=prfit,tax=tax, exp=exp, top=top,p_lst=p_lst,)

if __name__ == '__main__':
    app.run()

