""" Description: This script generates a PDF invoice using the FPDF library."""

import os

from flask import Flask, render_template, request, send_file
from fpdf import FPDF
from werkzeug.utils import secure_filename
from num2words import num2words

app = Flask(__name__)

RS = "\u20B9"


class InvoicePDF(FPDF):
    """This class generates a PDF invoice using the FPDF library."""

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
        self.set_font("Arial", "B", 10)
        y = 20
        for line in address_lines:
            self.set_xy(70, y)
            self.cell(0, 5, line, ln=True)
            y += 5
        self.ln(20)
        
        # Add "TAX INVOICE - ORIGINAL" to the top left of the page
        self.set_xy(5, 5)
        self.set_font("Arial", "", 10)
        self.cell(0, 5, "TAX INVOICE - ORIGINAL", ln=True)

    def footer(self):
        terms = """
1. No returns or exchanges on sold goods.
2. All disputes are subject to local jurisdiction only.
3. Payment is due within 30 days of delivery.
4. Guarantee excludes mishandling after delivery.
"""
        bank = """
Bank Name: CANARA BANK
A/C NAME: RAMESH ENGINEERING
Account No: 04081010002140
IFSC Code: CNRB0010651"""
        self.set_y(-36)  # Moved down by 2 units
        self.set_font("Arial", "B", 10)
        self.cell(0, 10, "Terms and Conditions:", ln=0)
        self.set_font("Arial", "", 10)
        self.set_y(-30)  # Moved down by 2 units
        self.multi_cell(90, 5, terms)

        self.set_xy(120, -36)  # Moved down by 2 units
        self.set_font("Arial", "B", 10)
        self.cell(0, 10, "Bank Details:", ln=0)
        self.set_font("Arial", "", 10)
        self.set_xy(120, -30)  # Moved down by 2 units
        self.multi_cell(0, 5, bank)

        # Draw a dark line below the footer
        self.set_line_width(0.6)
        self.set_draw_color(0, 0, 0)
        self.line(10, 292, 200, 292)

        # Add statement below the dark line
        self.set_y(-7)
        self.set_font("Arial", "I", 9)
        self.cell(0, 10, "This is a computer generated invoice.", 0, 0, "C")

    def create_invoice(self, data):
        """This method generates the invoice using the provided data."""
        self.add_font("DejaVu", "", "DejaVuSansCondensed.ttf", uni=True)
        self.add_page()
        gst_tax_rate = int(data["tax_rate"]) / 2

        # Invoice details box
        self.set_xy(10, 40)  # Moved up by 5 units
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "TAX INVOICE", align="C", ln=True)
        self.set_font("Arial", "", 10)

        # Invoice info box
        self.set_fill_color(200, 200, 200)
        self.rect(10, 55, 190, 10, "DF")  # Moved up by 5 units
        self.set_line_width(1.0)
        self.line(10.4, 55, 199.6, 55)  # Moved up by 5 units
        self.set_xy(15, 58)  # Moved up by 5 units
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, f"Invoice No: {data['invoice_no']}", align="L")
        self.set_xy(105, 58)  # Moved up by 5 units
        self.cell(0, 5, f"Invoice Date: {data['invoice_date']}", align="L")
        self.set_line_width(0.4)

        # Billing address box
        bill_to_lines = self.multi_cell(85, 5, data["bill_to"], split_only=True)
        bill_to_height = len(bill_to_lines) * 5 + 10
        self.set_fill_color(255, 255, 255)
        self.rect(10, 70, 95, bill_to_height, "DF")  # Moved up by 5 units
        self.set_xy(15, 72)  # Moved up by 5 units
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, "Bill To:", ln=True)
        self.set_font("Arial", "", 10)
        self.set_xy(15, 77)  # Moved up by 5 units
        self.multi_cell(85, 5, data["bill_to"])

        # Your DC No and EWay Bill Box
        self.rect(105, 70, 95, bill_to_height, "DF")  # Moved up by 5 units
        self.set_xy(110, 72)  # Moved up by 5 units
        self.set_font("Arial", "B", 10)
        self.cell(0, 5, f"Your DC No: {data['your_dc_no']}", align="L")
        self.set_xy(110, 77)  # Moved up by 5 units
        self.cell(0, 5, f"EWAY Bill No: {data['eway_bill_no']}", align="L")

        # Items table
        self.ln(5)
        self.set_xy(10, bill_to_height + 77)  # Moved up by 5 units

        # Table headers
        self.set_fill_color(200, 200, 200)
        headers = ["S.No", "Description", "Qty", "Rate", "Tax (%)", "Amount"]
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
            tax_amount = amount * (int(data["tax_rate"]) / 100)
            total_amount = amount + tax_amount
            total += total_amount

            if y > 250:  # Adjusted to leave space for footer. Changed from 250 to 260
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
            self.cell(widths[0], 10, str(idx), 1, 0, "C")
            x += widths[0]
            self.set_xy(x, y)
            self.cell(widths[1], 10, item["description"], 1)
            x += widths[1]
            self.set_xy(x, y)
            self.cell(widths[2], 10, str(item["quantity"]), 1, 0, "C")
            x += widths[2]
            self.set_xy(x, y)
            self.set_font("DejaVu", "", 10)
            self.cell(widths[3], 10, f"{RS}{item['rate']:.2f}", 1, 0, "C")
            x += widths[3]
            self.set_xy(x, y)
            self.cell(widths[4], 10, f"{data['tax_rate']}%", 1, 0, "C")
            x += widths[4]
            self.set_xy(x, y)
            self.set_font("DejaVu", "", 10)
            self.cell(widths[5], 10, f"{RS}{total_amount:.2f}", 1, 0, "R")
            y += 10

        # Round total to nearest integer
        total = round(total)

        # Compute tax details
        taxable_amount = total / (1 + gst_tax_rate / 100)
        cgst = taxable_amount * 0.06
        sgst = taxable_amount * 0.06

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
        self.multi_cell(
            95, line_height, f"Total Amount (in words): {total_in_words}", 0, "L"
        )

        # Add "FOR RAMESH ENGINEERING" below the total
        self.set_xy(10, rect_y + rect_height + 10)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "FOR RAMESH ENGINEERING", 0, 1, "R")
        self.cell(0, 10, "", 0, 1, "R")  # Empty line for spacing

        self.set_xy(10, rect_y + rect_height + 25)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "AUTHORIZED SIGNATORY", 0, 1, "R")
        self.cell(0, 10, "", 0, 1, "R")  # Empty line for spacing


@app.route("/")
def index():
    """This function renders the form template."""
    return render_template("form.html")


@app.route("/generate", methods=["POST"])
def generate():
    """This function generates the PDF invoice using the provided data."""
    # pdf_path = 'invoice.pdf'
    try:
        data = {
            "invoice_no": request.form["invoice_no"],
            "invoice_date": request.form["invoice_date"],
            "bill_to": request.form["bill_to"],
            "terms": request.form.get("terms", ""),
            "eway_bill_no": request.form["eway_bill_no"],
            "your_dc_no": request.form["your_dc_no"],
            "tax_rate": request.form["tax_rate"],
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
                }
            )

        pdf = InvoicePDF()
        pdf.create_invoice(data)
        pdf.output(pdf_path)

        return_data = send_file(pdf_path, as_attachment=True, download_name=filename)
        return return_data
    finally:
        if os.name == "nt":
            pass
        else:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
