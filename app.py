from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import re

app = Flask(__name__)

def extract_items_and_costs(image_path):
    # Load the image and use Tesseract to do OCR
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)

    items = []
    
    # Common patterns for matching item and price lines, including support for ₹ symbol
    price_pattern = r'(\d+\.\d{2}|\d+)'  # Matches prices like 12.34 or 12
    item_pattern = r'(.+?)\s+(₹?\s?\d+\.\d{2}|₹?\s?\d+)$'  # Matches lines with items and prices, with optional ₹ symbol

    # Extracting lines from the OCR text
    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        
        # Check for lines with both item names and prices
        if re.search(price_pattern, line):
            # Use regex to match items with prices at the end
            match = re.search(item_pattern, line)
            if match:
                # Capture the item name and price
                item_name = match.group(1).strip()
                cost = match.group(2).strip()
                
                # Normalize cost format and handle rupee symbol if present
                try:
                    cost = float(re.sub(r'[^\d.]', '', cost))  # Remove any non-numeric characters like ₹
                except ValueError:
                    continue  # Skip if cost is not a valid number

                # Append item and cost to the list
                items.append({"item": item_name, "cost": cost})
                
            else:
                # Fallback for lines with split words (OCR sometimes splits words across lines)
                words = line.split()
                possible_cost = words[-1]
                try:
                    # Check if the last word is a price, if so, treat rest as item name
                    cost = float(re.sub(r'[^\d.]', '', possible_cost))
                    item_name = " ".join(words[:-1])
                    items.append({"item": item_name, "cost": cost})
                except ValueError:
                    continue  # Skip if no valid price is found

    return items

@app.route('/extract', methods=['POST'])
def extract_from_bill():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Save the uploaded file
    file_path = "/mnt/data/" + file.filename
    file.save(file_path)

    # Extract items and costs
    items = extract_items_and_costs(file_path)
    
    return jsonify({"items": items})

if __name__ == '__main__':
    app.run(debug=True)
