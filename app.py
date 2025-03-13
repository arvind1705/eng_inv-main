""" Description: This script generates a PDF invoice using the FPDF library."""

import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from fpdf import FPDF
from werkzeug.utils import secure_filename
from num2words import num2words

app = Flask(__name__)
app.secret_key = "your_secret_key"

RS = "\u20B9"

# Hardcoded credentials
USERNAME = "vinodh944"
PASSWORD = "9449444452@123ABC"


class InvoicePDF(FPDF):
    """This class generates a PDF invoice using the FPDF library."""

    def __init__(self, data):
        super().__init__()
        self.data = data

    def header(self):
        self.image("logo.jpeg", 10, 2, 50)
        self.set_xy(70, 15)
        self.set_font("Arial", "B", 20)
        self.cell(0, 5, "RAMESH ENGINEERING", ln=True)
        self.set_font("Arial", "", 10)
        address_lines = [
            "No.2, Ground Floor, 1st Main Road, 2nd Cross,",
            "2nd Phase Peenya, Bengaluru - 560058",
            "GSTIN: 29ACXPV3219P1ZD",
            "Mobile: +91-9448073832, +91-9449444452",
        ]
        y = 20
        for line in address_lines:
            self.set_xy(70, y)
            if "GSTIN" in line:
                self.set_font("Arial", "B", 10)
            else:
                self.set_font("Arial", "", 10)
            self.cell(0, 5, line, ln=True)
            y += 5
        self.ln(20)

        # Add "TAX INVOICE - ORIGINAL" to the top left of the page
        self.set_xy(5, 5)
        self.set_font("Arial", "", 10)
        self.cell(0, 5, f"TAX INVOICE - {self.data['tax_invoice_type']}", ln=True)

    def footer(self):
        terms = """
1. No returns or exchanges on sold goods.
2. All disputes are subject to local jurisdiction only.
3. Payment is due within 30 days of delivery.
4. Guarantee excludes mishandling of components after delivery.
"""
        bank = """
Bank Name: CANARA BANK
A/C NAME: RAMESH ENGINEERING
Account No: 04081010002140
IFSC Code: CNRB0010651"""
        self.set_y(-36)
        self.set_font("Arial", "B", 10)
        self.cell(0, 10, "Terms and Conditions:", ln=0)
        self.set_font("Arial", "", 10)
        self.set_y(-30)
        self.multi_cell(105, 5, terms)

        self.set_xy(130, -36)
        self.set_font("Arial", "B", 10)
        self.cell(0, 10, "Bank Details:", ln=0)
        self.set_font("Arial", "", 10)
        self.set_xy(130, -30)
        self.multi_cell(0, 5, bank)

        # Draw a dark line below the footer
        self.set_line_width(0.6)
        self.set_draw_color(0, 0, 0)
        self.line(10, 292, 200, 292)

        # Add statement below the dark line
        self.set_y(-7)
        self.set_font("Arial", "", 9)
        self.cell(0, 10, "This is a computer generated invoice.", 0, 0, "C")

    def create_invoice(self, data):
        """This method generates the invoice using the provided data."""
        self.add_font("DejaVu", "", "DejaVuSansCondensed.ttf", uni=True)
        self.add_page()
        gst_tax_rate = int(data["tax_rate"]) / 2

        # Invoice details box
        self.set_xy(10, 40)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "TAX INVOICE", align="C", ln=True)
        self.set_font("Arial", "", 10)

        # Invoice info box
        self.set_fill_color(200, 200, 200)
        self.rect(10, 55, 190, 10, "DF")
        self.set_line_width(1.0)
        self.line(10.4, 55, 199.6, 55)
        self.set_xy(15, 58)
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, f"Invoice No: {data['invoice_no']}", align="L")
        self.set_xy(105, 58)
        self.cell(0, 5, f"Invoice Date: {data['invoice_date']}", align="L")
        self.set_line_width(0.4)

        # Billing address box
        bill_to_lines = self.multi_cell(85, 5, data["bill_to"], split_only=True)
        bill_to_height = len(bill_to_lines) * 5 + 10 + 5
        self.set_fill_color(255, 255, 255)
        self.rect(10, 70, 95, bill_to_height, "DF")
        self.set_xy(15, 72)
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, "Bill To:", ln=True)
        self.set_font("Arial", "", 10)
        self.set_xy(15, 77)
        self.multi_cell(85, 5, data["bill_to"])

        # Your DC No and EWay Bill Box
        self.rect(105, 70, 95, bill_to_height, "DF")
        self.set_xy(110, 72)
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, f"Your DC No: {data['your_dc_no']}", align="L")
        self.set_xy(110, 77)
        self.cell(0, 5, f"Your DC Date: {data['your_dc_date']}", align="L")
        self.set_xy(110, 82)
        self.cell(0, 5, f"EWAY Bill No: {data['eway_bill_no']}", align="L")

        # Items table
        self.ln(5)
        self.set_xy(10, bill_to_height + 77)
        # Table headers
        self.set_fill_color(200, 200, 200)
        headers = ["S.No", "Description", "Qty", "Rate", "Amount"]
        widths = [10, 80, 20, 30, 50]

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
            total_amount = amount
            total += total_amount

            # Calculate the height of the description cell based on the number of lines
            description_lines = self.multi_cell(
                widths[1], 6, item["description"], split_only=True
            )
            description_height = len(description_lines) * 6

            if y + description_height > 250:  # Adjusted to leave space for footer
                self.add_page()
                y = 50
                x = 10
                self.set_fill_color(200, 200, 200)
                for i, header in enumerate(headers):
                    self.set_xy(x, y)
                    self.cell(widths[i], 10, header, 1, 0, "C", True)
                    x += widths[i]
                y += 10
                x = 10

            self.set_xy(x, y)
            self.cell(widths[0], description_height, str(idx), 1, 0, "C")
            x += widths[0]
            self.set_xy(x, y)
            self.multi_cell(widths[1], 6, item["description"], 1)
            x += widths[1]
            self.set_xy(x, y)
            self.cell(widths[2], description_height, str(item["quantity"]), 1, 0, "C")
            x += widths[2]
            self.set_xy(x, y)
            self.set_font("DejaVu", "", 10)
            self.cell(
                widths[3], description_height, f"{RS}{item['rate']:.2f}", 1, 0, "C"
            )
            x += widths[3]
            self.set_xy(x, y)
            self.set_font("DejaVu", "", 10)
            self.cell(
                widths[4], description_height, f"{RS}{total_amount:.2f}", 1, 0, "R"
            )
            y += description_height

        # Compute tax details
        taxable_amount = round(total)
        cgst = sgst = round(taxable_amount * (gst_tax_rate / 100))

        total = taxable_amount + cgst + sgst
        # Horizontal positions for labels and values
        x_label = 120  # X-coordinate for labels
        _ = 170  # X-coordinate for values (aligned closer to labels)
        line_height = 5  # Reduced spacing between rows
        y_start = y + 5  # Initial Y-coordinate

        # Check if there is enough space for tax details and total
        if y_start + 3 * line_height + 10 > 240:  # Adjusted to leave space for footer
            self.add_page()
            y_start = 50

        # Display Taxable Amount
        self.set_xy(x_label - 10, y_start)
        self.set_font("Arial", "B", 10)
        self.cell(50, line_height, "Taxable Amount", 1, 0, "L")
        self.set_font("DejaVu", "", 10)
        self.cell(40, line_height, f"₹ {taxable_amount:.2f}", 1, 0, "R")

        # Display CGST
        self.set_xy(x_label - 10, y_start + line_height)
        self.set_font("Arial", "B", 10)
        self.cell(50, line_height, f"CGST @{gst_tax_rate}%", 1, 0, "L")
        self.set_font("DejaVu", "", 10)
        self.cell(40, line_height, f"₹ {cgst:.2f}", 1, 0, "R")

        # Display SGST
        self.set_xy(x_label - 10, y_start + 2 * line_height)
        self.set_font("Arial", "B", 10)
        self.cell(50, line_height, f"SGST @{gst_tax_rate}%", 1, 0, "L")
        self.set_font("DejaVu", "", 10)
        self.cell(40, line_height, f"₹ {sgst:.2f}", 1, 0, "R")

        # Display Total in Rectangle
        total_in_words = (
            num2words(f"{total}.00", to="currency", lang="en_IN", currency="INR")
            .replace(", zero paise", "")
            .replace("and", "")
            .replace("  ", " ")
        )
        total_in_words = total_in_words.title().replace("-", " ")
        total_in_words = total_in_words.replace("Rupees", "Rupees Only")
        total_in_words = total_in_words.replace("Thous", "Thousand")

        # Calculate the height of the rectangle based on the number of lines in total words
        total_words_lines = self.multi_cell(
            95,
            line_height,
            f"Total Amount (in words): {total_in_words}",
            split_only=True,
        )
        rect_height = max(10, len(total_words_lines) * line_height + 4)

        # Check if there is enough space for the rectangle
        if (
            y_start + 3 * line_height + rect_height + 10 > 240
        ):  # Adjusted to leave space for footer
            self.add_page()
            y_start = 50

        # Rectangle for Total Amount and Words
        rect_y = y_start + 3 * line_height + 4
        self.set_xy(10, rect_y)
        self.set_font("Arial", "B", 10)
        self.set_line_width(0.8)  # Slightly thicker top and bottom borders
        self.cell(
            190, rect_height, "", border="TB"
        )  # Draw rectangle with top and bottom borders only

        # Total Label and Value (inside the rectangle)
        self.set_xy(120, rect_y + (rect_height - line_height) / 2)
        self.set_font("Arial", "B", 12)
        self.cell(40, line_height, "TOTAL:", 0, 0, "L")  # Bold label "TOTAL:"
        self.set_font("DejaVu", "", 12)
        self.cell(30, line_height, f"₹ {total:.2f}", 0, 0, "R")

        # Total in Words (inside the rectangle, on the same line as total amount)
        self.set_xy(15, rect_y + 2)
        self.set_font("Arial", "", 10)
        self.multi_cell(95, line_height, f"In Words: {total_in_words}", 0, "L")

        # Add "FOR RAMESH ENGINEERING" below the total
        self.set_xy(10, rect_y + rect_height + 10)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "FOR RAMESH ENGINEERING", 0, 1, "R")
        self.cell(0, 10, "", 0, 1, "R")  # Empty line for spacing

        self.set_xy(142, rect_y + rect_height + 25)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "AUTHORIZED SIGNATORY", 0, 1)
        self.cell(0, 10, "", 0, 1, "R")  # Empty line for spacing


@app.route("/login", methods=["GET", "POST"])
def login():
    """This function handles user login."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
def logout():
    """This function logs out the user."""
    session.pop("logged_in", None)
    return redirect(url_for("login"))


@app.route("/")
def index():
    """This function renders the form template."""
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("form.html")


@app.route("/generate", methods=["POST"])
def generate():
    """This function generates the PDF invoice using the provided data."""
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    # pdf_path = 'invoice.pdf'
    try:
        data = {
            "invoice_no": request.form["invoice_no"],
            "invoice_date": request.form["invoice_date"],
            "bill_to": request.form["bill_to"],
            "terms": request.form.get("terms", ""),
            "eway_bill_no": (
                request.form["eway_bill_no"] if request.form["eway_bill_no"] else "NA"
            ),
            "your_dc_no": request.form["your_dc_no"],
            "your_dc_date": request.form["your_dc_date"],
            "tax_rate": request.form["tax_rate"],
            "tax_invoice_type": request.form["tax_invoice_type"],
            "items": [],
        }
        invoice_no = request.form["invoice_no"]
        tax_invoice_type = request.form["tax_invoice_type"]
        filename = secure_filename(f"{invoice_no}_{tax_invoice_type}.pdf")
        pdf_path = filename

        item_count = int(request.form["item_count"])
        for i in range(item_count):
            data["items"].append(
                {
                    "description": request.form[f"item_description_{i}"],
                    "quantity": int(request.form[f"item_quantity_{i}"]),
                    "rate": float(request.form[f"item_rate_{i}"]),
                }
            )

            pdf = InvoicePDF(data=data)
            pdf.create_invoice(data)
            pdf.output(pdf_path)

        # Modified send_file with explicit parameters to force download
        return_data = send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename,
            conditional=False
        )
        
        # Enhanced headers to force download in Safari
        return_data.headers["Content-Disposition"] = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{filename}'
        return_data.headers["Content-Type"] = "application/pdf"
        return_data.headers["X-Content-Type-Options"] = "nosniff"
        # Add cache control headers to prevent browser caching
        return_data.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return_data.headers["Pragma"] = "no-cache"
        return_data.headers["Expires"] = "0"
        
        return return_data
    finally:
        if os.name == "nt":
            pass
        else:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
