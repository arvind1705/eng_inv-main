from flask import Flask, send_file
from fpdf import FPDF
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)

class InvoicePDF(FPDF):
    def header(self):
        # Logo and header
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "TAX INVOICE", align="R", ln=True)

        # Increase the logo size by adjusting the width and height
        self.image("logo1.jpeg", 10, 8, 50, 45)  # Adjusted width and height

        # Move header slightly to the right
        self.set_x(60)
        self.set_font("Arial", "B", 25)
        self.cell(0, 10, "RAMESH ENGINEERING", align="C", ln=True)
        self.set_font("Arial", "", 12)
        self.set_x(60)
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
        self.set_xy(80, 65)
        self.cell(0, 5, f"Invoice Date: {data['invoice_date']}", align="C")
        self.set_xy(150, 65)
        self.cell(0, 5, f"Due Date: {data['due_date']}", align="R")

        # EWay Bill Box
        self.set_fill_color(200, 200, 200)
        self.rect(10, 80, 190, 10, "DF")
        self.set_xy(15, 85)
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, f"EWAY Bill No: {data['eway_bill_no']}", align="L")

        # Billing and Shipping info
        self.set_xy(10, 95)
        self.set_font("Arial", "B", 10)
        self.cell(95, 10, "Bill To:", ln=True)
        self.set_xy(105, 95)
        self.cell(95, 10, "Ship To:", ln=True)

        self.set_font("Arial", "", 10)
        self.set_xy(10, 105)
        self.multi_cell(95, 5, data["bill_to"])
        self.set_xy(105, 105)
        self.multi_cell(95, 5, data["ship_to"])

        # Items table
        self.ln(10)
        self.set_xy(10, 130)

        # Table headers
        self.set_fill_color(200, 200, 200)
        headers = ["Description", "Qty", "Rate", "Tax%", "Amount"]
        widths = [80, 20, 30, 20, 40]
        for i, header in enumerate(headers):
            self.cell(widths[i], 10, header, 1, 0, "C", 1)
        self.ln()

        # Table rows
        for item in data["items"]:
            self.cell(widths[0], 10, item["description"], 1)
            self.cell(widths[1], 10, str(item["qty"]), 1, 0, "C")
            self.cell(widths[2], 10, f"{item['rate']:.2f}", 1, 0, "R")
            self.cell(widths[3], 10, f"{item['tax']:.2f}", 1, 0, "R")
            self.cell(widths[4], 10, f"{item['amount']:.2f}", 1, 0, "R")
            self.ln()

        # Total amount
        self.set_font("Arial", "B", 10)
        self.cell(sum(widths[:-1]), 10, "Total", 1)
        self.cell(widths[-1], 10, f"{data['total']:.2f}", 1, 0, "R")

@app.route('/invoice')
def invoice():
    data = {
        "invoice_no": "12345",
        "invoice_date": "2023-10-01",
        "due_date": "2023-10-15",
        "eway_bill_no": "EWAY1236767676",
        "bill_to": "Customer Name\nAddress Line 1\nAddress Line 2\nCity, State, ZIP",
        "ship_to": "Recipient Name\nAddress Line 1\nAddress Line 2\nCity, State, ZIP",
        "items": [
            {"description": "Item 1", "qty": 2, "rate": 100.00, "tax": 5.00, "amount": 210.00},
            {"description": "Item 2", "qty": 1, "rate": 200.00, "tax": 10.00, "amount": 220.00},
        ],
        "total": 430.00
    }

    pdf = InvoicePDF()
    pdf.create_invoice(data)
    
    # Save the PDF to a bytes buffer
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    return send_file(pdf_buffer, as_attachment=True, download_name="invoice.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)