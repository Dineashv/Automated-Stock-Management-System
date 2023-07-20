from flask import Flask, render_template, request, send_file
from flask_wkhtmltopdf import Wkhtmltopdf

app = Flask(__name__)

wkhtmltopdf = Wkhtmltopdf(app)

@app.route("/")
def form1():
    return render_template("form.html")

@app.route("/generate_invoice", methods=["POST"])
def generate_invoice():
    # get data from the form
    customer_name = request.form.get("customer_name")
    invoice_number = request.form.get("invoice_number")
    invoice_date = request.form.get("invoice_date")
    # product_description = request.form.get("product_description")
    product_quantity = request.form.get("product_quantity")
    product_price = request.form.get("product_price")
    product_amount = int(product_quantity)*int(product_price)

    customer_mobile = request.form.get('customer_mobile')
    product_description = request.form.get("product_description")
    invoice_due_date = request.form.get("invoice_due_date")
    # generate the invoice HTML using a template
    invoice_html = render_template("test.html", 
        customer_name=customer_name, 
        invoice_number=invoice_number, 
        invoice_date=invoice_date, 
        # product_description=product_description, 
        product_quantity=product_quantity, 
        product_price=product_price,
        product_amount=str(product_amount),
        invoice_due_date=invoice_due_date,
        product_description=product_description,
        customer_mobile=customer_mobile
    )

    # convert the HTML to PDF
    # pdf_file = wkhtmltopdf.from_string(invoice_html)

    # return the PDF as a file download
    #return send_file(pdf_file, attachment_filename="invoice.pdf")
    return render_template("test.html", 
        customer_name=customer_name, 
        invoice_number=invoice_number, 
        invoice_date=invoice_date, 
        # product_description=product_description, 
        product_quantity=product_quantity, 
        product_price=product_price,
        product_amount=str(product_amount),
        invoice_due_date=invoice_due_date,
        product_description=product_description,
        customer_mobile=customer_mobile
    )

if __name__ == "__main__":
    app.run(debug=True)
