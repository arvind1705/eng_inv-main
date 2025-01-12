#!/bin/bash

# Parameters
item_count=$1
invoice_no="INV12345"
invoice_date="2025-01-12"
bill_to="Aravind G, 
No.331, 10th A main road, 
Manjunath Nagar, Basaveshwaranagar, 
WOC road, Bengaluru - 560010
Karnataka, 
India"
terms="Net 30"
eway_bill_no="EBN1234567890"
your_dc_no="DC987654321"
tax_rate=18
output_file="/Users/aravind/Desktop/INV12345.pdf"

# Start the curl command
curl_command="curl -X POST http://127.0.0.1:8000/generate \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'invoice_no=$invoice_no' \
-d 'invoice_date=$invoice_date' \
-d 'bill_to=$bill_to' \
-d 'terms=$terms' \
-d 'eway_bill_no=$eway_bill_no' \
-d 'your_dc_no=$your_dc_no' \
-d 'tax_rate=$tax_rate' \
-d 'item_count=$item_count'"

descriptions=("Widget A" "Widget B" "Widget C" "Widget D" "Widget E")

# Loop over the item entries
for ((i=0; i<item_count; i++)); do
    description=${descriptions[$RANDOM % ${#descriptions[@]}]}
    quantity=$((i + 1))
    rate=$((10 + i * 5))
    
    curl_command+=" -d 'item_description_$i=$description' \
-d 'item_quantity_$i=$quantity' \
-d 'item_rate_$i=$rate'"
done

# Output file
curl_command+=" -o '$output_file'"

# Execute the curl command
eval $curl_command
