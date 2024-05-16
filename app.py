from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

app = Flask(__name__)

PROXY_URL = 'https://proxy.scrapeops.io/v1/'
PROXY_API_KEY = '3c1fb83d-5b93-4495-b023-170775d435f7'


def get_product_details(asin):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.amazon.in/',
    }

    print(f"Using User-Agent: {headers['User-Agent']}")

    proxy_response = requests.get(
        url=PROXY_URL,
        params={
            'api_key': PROXY_API_KEY,
            'url': f'https://www.amazon.in/dp/{asin}', 
        },
        headers=headers
    )

    if proxy_response.status_code != 200:
        return {
            'error': f"Proxy request failed with status code {proxy_response.status_code}."
        }

    soup = BeautifulSoup(proxy_response.content, 'html.parser')
    #print(soup)

    # Product title
    product_title = soup.find('span', {'id': 'productTitle'}).text.strip()
    print(product_title)

    # Product price
    price_div = soup.find('div', {'id': 'corePriceDisplay_desktop_feature_div'})

# Check if the div is found
    if price_div:
        # Find the price element inside this div
        price_element = price_div.find('span', {'class': 'a-price-whole'})
    
        if price_element:
            product_price = price_element.text.strip()
        
            # Remove trailing period if exists
            if product_price.endswith('.'):
                product_price = product_price[:-1]
        
        else:
            product_price = 'Price not available'
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
