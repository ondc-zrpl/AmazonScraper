from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

app = Flask(__name__)


def get_product_details(asin):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.amazon.in/',
    }

    print(f"Using User-Agent: {headers['User-Agent']}")

    response = requests.get(
        url=f'https://www.amazon.in/dp/{asin}',
        headers=headers
    )

    if response.status_code != 200:
        return {
            'error': f"Request failed with status code {response.status_code}."
        }

    soup = BeautifulSoup(response.content, 'html.parser')

    # Product title
    product_title = soup.find('span', {'id': 'productTitle'}).text.strip()
    print(product_title)

    # Product price
    price_element = soup.find('span', {'class': 'a-price-whole'})
    if price_element:
        product_price = price_element.text.strip()
        if product_price.endswith('.'):
            product_price = product_price[:-1]
        
    else:
        product_price = 'Price not available'
    print(product_price)
    # Check if product is sold by Amazon
    sold_by_amazon = bool(soup.find('span', {'id': 'sellerProfileTriggerId'}))

    # Availability status
    availability_element = soup.find('span', {'class': 'a-size-medium a-color-success'})
    if availability_element:
        availability_status = availability_element.text.strip()
        if availability_status.endswith('.'):
            availability_status = availability_status[:-1]
    else:
        availability_status = 'Availability status not available'

    # Image URL
    image_element = soup.find('img', {'id': 'landingImage'})
    if image_element:
        image_url = image_element['src']
    else:
        image_url = 'Image not available'
    price = "-1" if availability_status == "Currently unavailable" else product_price
    return {
        'title': product_title,
        'price': price,
        'image_url': image_url,
        'sold_by_amazon': sold_by_amazon,
        'availability_status': availability_status
    }
@app.route('/')
def hello():
    return 'Hello, World!'
@app.route('/get_amazon_product_info', methods=['GET'])
def get_product_info():
    asin = request.args.get('asin')
    

    if not asin:
        return jsonify(error='The "asin" parameter is required.'), 400

    

    product_info = get_product_details(asin)
    return jsonify(product_info)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
