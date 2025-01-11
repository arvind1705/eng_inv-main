from flask import Flask, render_template, request, send_file
from fpdf import FPDF
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

terms = """
1. Payment is due within 30 days from the date of invoice
        2. Please make payment via bank transfer to the account details provided
        3. Goods once sold cannot be returned
        4. All disputes are subject to local jurisdiction only"""

class InvoicePDF(FPDF):
    def header(self):
        # Logo and header
        self.image("logo1.jpeg", 0, 0, 50, 50)  # Adjusted width and height
        self.set_font("Arial", "B", 20)
        self.cell(0, 12, "RAMESH ENGINEERING", align="C", ln=True)
        self.set_font("Arial", "", 10)
        self.cell(
            0, 5, "NO.2, GROUND FLOOR, 1ST MAIN ROAD, 2ND CROSS,", align="C", ln=True
        )
        self.cell(0, 5, "2ND PHASE PEENYA, Bengaluru (Bangalore)", align="C", ln=True)
        self.cell(0, 5, "GSTIN: 29ACXPV3219P1ZD", align="C", ln=True)
        self.ln(10)

    def footer(self):
        self.set_y(-30)
        self.set_font("Arial", "B", 10)
        self.cell(0, 10, "Terms and Conditions:", ln=True)
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 5, terms)

    def create_invoice(self, data):
        self.add_page()

        # Invoice details box
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "TAX INVOICE", align="C", ln=True)
        self.set_font("Arial", "", 10)

        # Invoice info box
        self.set_fill_color(200, 200, 200)
        self.rect(10, 60, 190, 15, "DF")
        self.set_xy(15, 65)
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, f"Invoice No: {data['invoice_no']}", align="L")
        self.set_xy(35, 65)
        self.cell(0, 5, f"Invoice Date: {data['invoice_date']}", align="C")
        self.set_xy(170, 65)

        # Your DC No and EWay Bill Box    
        self.set_fill_color(200, 200, 200)
        self.rect(10, 80, 190, 10, "DF")
        self.set_xy(15, 85)
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, f"Your DC No: {data['your_dc_no']}", align="L")
        self.set_xy(150, 85)
        self.cell(0, 5, f"EWAY Bill No: {data['eway_bill_no']}", align="R")

        # Billing and Shipping info
        self.set_xy(10, 90)
        self.set_font("Arial", "B", 10)
        self.cell(95, 10, "Bill To:", ln=True)

        self.set_font("Arial", "", 10)
        self.set_xy(10, 100)
        self.multi_cell(95, 5, data["bill_to"])

        # Items table
        self.ln(10)
        self.set_xy(10, 130)

        # Table headers
        self.set_fill_color(200, 200, 200)
        headers = ["S.No", "Description", "Qty", "Rate", "Tax%", "Amount"]
        widths = [10, 70, 20, 30, 20, 40]

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

        for idx, item in enumerate(data["items"], start=1):
            x = 10
            amount = item["quantity"] * item["rate"]
            tax_amount = amount * (item["tax"] / 100)
            total_amount = amount + tax_amount
            total += total_amount

            if y > 260:  # Check if the y-coordinate exceeds the page height
                self.add_page()
                y = 50  # Reset y-coordinate for the new page, leaving space for header
                x = 10  # Reset x-coordinate for the new page
                self.set_fill_color(200, 200, 200)
                for i, header in enumerate(headers):
                    self.set_xy(x, y)
                    self.cell(widths[i], 10, header, 1, 0, "C", True)
                    x += widths[i]
                y += 10

            self.set_xy(x, y)
            self.cell(widths[0], 10, str(idx), 1, 0, "C")
            x += widths[0]
            self.set_xy(x, y)
            self.cell(widths[1], 10, item["description"], 1)
            x += widths[1]
            self.set_xy(x, y)
            self.cell(widths[2], 10, str(item["quantity"]), 1, 0, "C")
            x += widths[2]
            self.set_xy(x, y)
            self.cell(widths[3], 10, f"Rs.{item['rate']:.2f}", 1, 0, "R")
            x += widths[3]
            self.set_xy(x, y)
            self.cell(widths[4], 10, f"{item['tax']}%", 1, 0, "C")
            x += widths[4]
            self.set_xy(x, y)
            self.cell(widths[5], 10, f"Rs.{total_amount:.2f}", 1, 0, "R")
            y += 10

        # Total
        self.set_xy(140, y + 5)
        self.set_font("Arial", "B", 10)
        self.cell(30, 10, "Total:", 0, 0, "R")
        self.cell(30, 10, f"Rs.{total:.2f}", 0, 0, "R")

        # display bank details
        self.set_xy(10, y + 5)
        self.set_font("Arial", "B", 10) 
        self.cell(0, 10, "Bank Details:", ln=True)
        self.set_font("Arial", "", 10)
        self.cell(0, 5, "Bank Name: CANARA BANK", ln=True)
        self.cell(0, 5, "A/C NAME: RAMESH ENGINEERING", ln=True)
        self.cell(0, 5, "Account No: 04081010002140", ln=True)
        self.cell(0, 5, "IFSC Code: CNRB0010651", ln=True)
       

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
            "your_dc_no": request.form["your_dc_no"],
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
        pass
      # if os.path.exists(pdf_path):
            # os.remove(pdf_path)


if __name__ == "__main__":
    app.run(debug=True)
