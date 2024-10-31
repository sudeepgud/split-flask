from flask import Flask, request, jsonify
import easyocr
import re
import os

app = Flask(__name__)
reader = easyocr.Reader(['en'])

def extract_items_and_costs(text_lines):
    items = []
    cost_pattern = re.compile(r'\b(\d+\.?\d*)\s*(?:INR|₹)?\b')  # Matches "99", "99.99", or "₹99"
    
    for line in text_lines:
        match = cost_pattern.search(line)
        if match:
            item_name = line[:match.start()].strip()
            item_cost = float(match.group(1))
            items.append({"item": item_name, "cost": item_cost})
    
    return items

@app.route('/read_bill', methods=['POST'])
def read_bill():
    if 'bill_image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    image = request.files['bill_image']
    
    # OCR Processing
    results = reader.readtext(image, detail=0)
    
    # Extract items and costs
    items_and_costs = extract_items_and_costs(results)
    
    if not items_and_costs:
        return jsonify({"error": "No items or costs detected"}), 404

    return jsonify({"items": items_and_costs})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
