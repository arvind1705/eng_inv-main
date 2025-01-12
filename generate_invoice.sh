#!/bin/bash

# Parameters
item_count=$1
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    desktop_path=$(echo "$USERPROFILE\\Desktop" | sed 's/\\/\//g')
else
    desktop_path=$(eval echo ~/Desktop)
fi
if [ -z "$2" ]; then
    output_file="$desktop_path/INV12345.pdf"
else
    output_file="$desktop_path/INV12345_$2.pdf"
fi
invoice_no="INV12345"
invoice_date="2025-01-12"
bill_to="ABC Corporation, 
123 Main St,
Springfield, IL 62701
USA"
terms="Net 30"
eway_bill_no="EBN1234567890"
your_dc_no="DC987654321"
tax_rate=12
tax_invoice_type="Original"

# Start the curl command
curl_command="curl -X POST http://127.0.0.1:8000/generate \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'invoice_no=$invoice_no' \
-d 'invoice_date=$invoice_date' \
-d 'bill_to=$bill_to' \
-d 'terms=$terms' \
-d 'eway_bill_no=$eway_bill_no' \
-d 'tax_invoice_type=$tax_invoice_type' \
-d 'your_dc_no=$your_dc_no' \
-d 'tax_rate=$tax_rate' \
-d 'item_count=$item_count'"

descriptions=("Widget A" "Widget B" "Widget C" "Widget D" "Widget E")

# Loop over the item entries
for ((i=0; i<item_count; i++)); do
    description=${descriptions[$RANDOM % ${#descriptions[@]}]}
    quantity=$((RANDOM % 50 + 1))  # Random quantity between 1 and 50
    rate=$((RANDOM % 1000 + 1))     # Random rate between 1 and 1000
    
    curl_command+=" -d 'item_description_$i=$description' \
-d 'item_quantity_$i=$quantity' \
-d 'item_rate_$i=$rate'"
done

# Output file
curl_command+=" -o '$output_file'"

# Execute the curl command
eval $curl_command
