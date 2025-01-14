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

# Login credentials
USERNAME="vinodh944"
PASSWORD="9449444452@123ABC"

# Invoice details
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

descriptions=("Widget A" "Widget B" "Widget C" "Widget D" "Widget E")

# Perform login to get the session cookie
login_response=$(curl -i -s -X POST http://127.0.0.1:8000/login \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d "username=$USERNAME" \
    -d "password=$PASSWORD")

# Save login response for debugging
# echo "$login_response" > login_debug.txt

# Check if login was successful (look for redirect)
# if ! echo "$login_response" | grep -q "302 Found"; then
#     echo "Login failed. Please check your credentials."
#     exit 1
# fi

# Extract the session cookie
session_cookie=$(echo "$login_response" | grep 'Set-Cookie:' | grep 'session=' | sed -e 's/Set-Cookie: //' -e 's/;.*//')

if [ -z "$session_cookie" ]; then
    echo "Failed to retrieve session cookie. Check login_debug.txt for details."
    exit 1
fi

echo "Login successful. Session cookie: $session_cookie"

# Start the curl command for invoice generation
curl_command="curl -X POST http://127.0.0.1:8000/generate \
-H 'Content-Type: application/x-www-form-urlencoded' \
-H 'Cookie: $session_cookie' \
-d 'invoice_no=$invoice_no' \
-d 'invoice_date=$invoice_date' \
-d 'bill_to=$bill_to' \
-d 'terms=$terms' \
-d 'eway_bill_no=$eway_bill_no' \
-d 'tax_invoice_type=$tax_invoice_type' \
-d 'your_dc_no=$your_dc_no' \
-d 'tax_rate=$tax_rate' \
-d 'item_count=$item_count'"

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
