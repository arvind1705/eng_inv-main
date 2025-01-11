from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)


class InvoicePDF(FPDF):
    def header(self):
        # Logo and header

        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "TAX INVOICE", align="R", ln=True)

        # Increase the logo size by adjusting the width and height
        self.image("logo1.jpeg", 10, 8, 50, 45)  # Adjusted width and height

        # Move header slightly to the right
        self.set_x(40)
        self.set_font("Arial", "B", 25)
        self.cell(0, 10, "RAMESH ENGINEERING", align="C", ln=True)
        self.set_font("Arial", "", 12)
        self.set_x(40)
        self.cell(
            0, 5, "NO.2, GROUND FLOOR, 1ST MAIN ROAD, 2ND CROSS,", align="C", ln=True
        )
        self.set_x(60)
        self.cell(0, 5, "2ND PHASE PEENYA, Bengaluru (Bangalore)", align="C", ln=True)
        self.set_x(60)
        self.cell(0, 5, "GSTIN: 29ACXPV3219P1ZD", align="C", ln=True)
        self.ln(10)

    def create_invoice(self, data):
        self.add_page()

        # Invoice details box
        self.set_font("Arial", "", 10)

        # Invoice info box
        self.set_fill_color(200, 200, 200)
        self.rect(10, 60, 190, 15, "DF")
        self.set_xy(15, 65)
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, f"Invoice No: {data['invoice_no']}", align="L")
        self.set_xy(35, 65)
        self.cell(0, 5, f"Invoice Date: {data['invoice_date']}", align="C")
        #self.set_xy(170, 65)
       # self.cell(0, 5, f"Due Date: {data['due_date']}", align="R")
       # self.set_font("Arial", "", 10)

        # EWay Bill Box
        self.set_fill_color(200, 200, 200)
        self.rect(10, 80, 190, 10, "DF")

        self.set_xy(15, 85)
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, f"E-Way Bill No: {data['eway_bill_no']}", align="L")

        # Billing and Shipping info
        self.set_xy(10, 90)
        self.set_font("Arial", "B", 10)
        self.cell(95, 10, "Bill To:", ln=True)
        # self.set_xy(105, 90)
        # self.cell(95, 10, "Ship To:")

        self.set_font("Arial", "", 10)
        self.set_xy(10, 100)
        self.multi_cell(95, 5, data["bill_to"])
       # self.set_xy(105, 100)
        #self.multi_cell(95, 5, data["ship_to"])

        # Items table
        self.ln(10)
        self.set_xy(10, 130)

        # Table headers
        self.set_fill_color(200, 200, 200)
        headers = ["Description", "Qty", "Rate", "Tax%", "Amount"]
        widths = [80, 20, 30, 20, 40]

        self.set_font("Arial", "B", 10)
        x = 10
        for i, header in enumerate(headers):
            self.set_xy(x, self.get_y())
            self.cell(widths[i], 10, header, 1, 0, "C", True)
            x += widths[i]

        # Table content
        self.set_font("Arial", "", 10)
        y = self.get_y() + 10
        total = 0

        for item in data["items"]:
            x = 10
            amount = item["quantity"] * item["rate"]
            tax_amount = amount * (item["tax"] / 100)
            total_amount = amount + tax_amount
            total += total_amount

            self.set_xy(x, y)
            self.cell(widths[0], 10, item["description"], 1)
            x += widths[0]
            self.set_xy(x, y)
            self.cell(widths[1], 10, str(item["quantity"]), 1, 0, "C")
            x += widths[1]
            self.set_xy(x, y)
            self.cell(widths[2], 10, f"Rs.{item['rate']:.2f}", 1, 0, "R")
            x += widths[2]
            self.set_xy(x, y)
            self.cell(widths[3], 10, f"{item['tax']}%", 1, 0, "C")
            x += widths[3]
            self.set_xy(x, y)
            self.cell(widths[4], 10, f"Rs.{total_amount:.2f}", 1, 0, "R")
            y += 10

        # Total
        self.set_xy(140, y + 5)
        self.set_font("Arial", "B", 10)
        self.cell(30, 10, "Total:", 0, 0, "R")
        self.cell(30, 10, f"Rs.{total:.2f}", 0, 0, "R")

        # Terms
        if "terms" in data and data["terms"]:
            self.set_xy(10, y + 25)
            self.set_font("Arial", "B", 10)
            self.cell(0, 10, "Terms and Conditions:", ln=True)
            self.set_font("Arial", "", 10)
            self.multi_cell(0, 5, data["terms"])


@app.route("/")
def index():
    return render_template("form.html")


@app.route("/generate", methods=["POST"])
def generate():
    # pdf_path = "invoice.pdf"
    try:
        data = {
            "invoice_no": request.form["invoice_no"],
            "invoice_date": request.form["invoice_date"],
            "due_date": request.form["due_date"],
            "bill_to": request.form["bill_to"],
            "ship_to": request.form["ship_to"],
            "terms": request.form.get("terms", ""),
            "eway_bill_no": request.form["eway_bill_no"],
            "items": [],
        }
        invoice_no = request.form["invoice_no"]
        filename = secure_filename(f"{invoice_no}.pdf")
        pdf_path = filename

        item_count = int(request.form["item_count"])
        for i in range(item_count):
            data["items"].append(
                {
                    "description": request.form[f"item_description_{i}"],
                    "quantity": int(request.form[f"item_quantity_{i}"]),
                    "rate": float(request.form[f"item_rate_{i}"]),
                    "tax": float(request.form[f"item_tax_{i}"]),
                }
            )

        pdf = InvoicePDF()
        pdf.create_invoice(data)
        pdf.output(pdf_path)

        return_data = send_file(pdf_path, as_attachment=True, download_name=filename)
        return return_data
    finally:
        if os.path.exists(pdf_path):
           # os.remove(pdf_path)
           pass


if __name__ == "__main__":
    app.run(debug=True)
