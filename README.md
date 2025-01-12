# Invoice Generation System

A web-based invoice generation system built with Flask that creates professional PDF invoices.

## Features

- Web form interface for invoice data entry
- Dynamic item addition/removal
- GST calculation (CGST & SGST)
- PDF invoice generation with company letterhead
- Amount in words conversion
- Responsive design
- Bank details and terms & conditions included

## Requirements

Install the required packages:

```sh
pip install -r requirements.txt
```

Required packages:
- Flask==3.1.0
- fpdf==1.7.2
- gunicorn==20.0.4
- num2words==0.5.14

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Add your company logo as 

logo.jpeg

 in the root directory
4. Ensure 

DejaVuSansCondensed.ttf

 font file is present

## Usage

1. Start the server:
```sh
python app.py
```

2. Access the web interface at `http://localhost:8000`

3. Fill in the invoice details:
   - Invoice number
   - E-way bill number
   - DC number
   - Invoice date
   - Billing address
   - Tax rate (12% or 18%)
   - Add items with description, quantity and rate

4. Click "Generate Invoice" to download the PDF

## API Endpoint

- `POST /generate`: Generates and returns a PDF invoice
  - Form data parameters:
    - invoice_no (required)
    - invoice_date (required)
    - bill_to (required)
    - eway_bill_no (required)
    - your_dc_no (required)
    - tax_rate (required)
    - item_count
    - item_description_[n]
    - item_quantity_[n]
    - item_rate_[n]

## Deployment

The application includes a Procfile for Heroku deployment:

```
web: gunicorn --bind 0.0.0.0:8000 app:app
```
