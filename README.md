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
```

arvind1705: create full readme in markdown format

Workspace: Collecting workspace information

Here's a complete 

README.md

 for the invoice generation system:

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

## Prerequisites

- Python 3.7+
- Font file 

DejaVuSansCondensed.ttf


- Company logo as 

logo.jpeg



## Installation

1. Clone the repository
```sh
git clone <repository-url>
cd invoice-generation-system
```

2. Install dependencies
```sh
pip install -r requirements.txt
```

## Required Packages

- Flask==3.1.0
- fpdf==1.7.2
- gunicorn==20.0.4
- num2words==0.5.14

## Usage

1. Start the Flask server:
```sh
python app.py
```

2. Access the web interface at `http://localhost:8000`

3. Fill in the invoice form:
   - Invoice number
   - E-way bill number
   - DC number 
   - Invoice date
   - Billing address
   - Tax rate (12% or 18%)
   - Add items with description, quantity and rate

4. Click "Generate Invoice" to download the PDF

## API Endpoints

### Generate Invoice
- **URL**: `/generate`
- **Method**: `POST`
- **Form Data Parameters**:
  - 

invoice_no

 (required)
  - `invoice_date` (required)
  - `bill_to` (required)
  - `eway_bill_no` (required)
  - `your_dc_no` (required)
  - `tax_rate` (required)
  - 

item_count


  - `item_description_[n]`
  - `item_quantity_[n]`
  - `item_rate_[n]`

## File Structure

```
.
├── app.py                      # Main Flask application
├── templates/
│   ├── form.html              # Invoice form template
│   └── invoice.html           # Invoice preview template
├── requirements.txt           # Python dependencies
├── Procfile                  # Heroku deployment config
└── DejaVuSansCondensed.ttf   # Required font file
```

## Deployment

The application includes a Procfile for Heroku deployment:

```
web: gunicorn --bind 0.0.0.0:8000 app:app
```

## Testing

You can use the included 

generate_invoice.sh

 script to test the invoice generation:

```sh
./generate_invoice.sh <number_of_items>
```

## Bank Details

- Account Name: RAMESH ENGINEERING
- Bank Name: CANARA BANK
- IFSC Code: CNRB0010651
- Account Number: 04081010002140

## Terms and Conditions

1. Payment is due within 30 days from the date of invoice
2. Please make payment via bank transfer to the account details provided
3. Goods once sold cannot be returned
4. All disputes are subject to local jurisdiction only

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.