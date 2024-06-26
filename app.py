from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "3c1fb83d-5b93-4495-b023-170775d435f7"

def get_amazon_product_info(asin):
    url = f"https://proxy.scrapeops.io/v1/?api_key={API_KEY}&url=https://www.amazon.in/dp/{asin}&auto_extract=amazon"
    response = requests.get(url)
    data = response.json()
    
    if data["status"] == "parse_successful":
        product_data = data.get("data")
        if product_data:
            availability_status = product_data.get("availability_status", "").strip()
            if not availability_status and not product_data.get("pricing"):
                return "Not available", None, None
            if "Currently unavailable" in availability_status:
                return "Not available", None, None
            else:
                pricing_str = product_data["pricing"]
                pricing = float(''.join(c for c in pricing_str if c.isdigit() or c == '.'))
            
                product_name = product_data["name"]
                image_url = product_data["images"][0]
                return pricing, product_name, image_url
            
        else:
            return "Not available", None, None
    else:
        return "Error parsing the URL", None, None


@app.route('/get_amazon_product_info', methods=['GET'])
def product_info():
    asin = request.args.get('asin')

    if not asin:
        return jsonify({"error": "ASIN is required."}), 400

    pricing, product_name, image_url = get_amazon_product_info(asin)

    if pricing:
        return jsonify({
            "price": pricing,
            "title": product_name,
            "image_url": image_url
        })
    else:
        return jsonify({"message": "NA"})

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
