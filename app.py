from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

app = Flask(__name__)

def get_amazon_product_details(asin):
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

    # Product price
    price_element = soup.find('span', {'class': 'a-price-whole'})
    if price_element:
        product_price = price_element.text.strip()
        if product_price.endswith('.'):
            product_price = product_price[:-1]
    else:
        product_price = 'Price not available'

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

def get_flipkart_product_details(pid, lid):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
    }

    print(f"Using User-Agent: {headers['User-Agent']}")

    url = f'https://www.flipkart.com/brooks-launch-9-running-shoes-men/p/itmc1fa98405e951?pid={pid}&lid={lid}'
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')

    # Product name
    product_name = soup.find('span', {'class': 'B_NuCI'}).text

    # Product Price
    price_tag = soup.find('div', {'class': '_30jeq3 _16Jk6d'})
    product_price = '0'
    if price_tag:
        product_price = price_tag.text.replace('₹', '').replace(',', '')
        product_price = float(product_price)

    # Image URL
    image_tag = soup.find('img', {'class': '_396cs4'})
    image_url = ''
    if image_tag and 'src' in image_tag.attrs:
        image_url = image_tag['src']

    return {
        'title': product_name,
        'price': product_price,
        'image_url': image_url
    }

@app.route('/get_amazon_product_info', methods=['GET'])
def get_amazon_product_info():
    asin = request.args.get('asin')

    if not asin:
        return jsonify(error='The "asin" parameter is required.'), 400

    product_info = get_amazon_product_details(asin)
    return jsonify(product_info)

@app.route('/get_flipkart_product_info', methods=['GET'])
def get_flipkart_product_info():
    pid = request.args.get('pid')
    lid = request.args.get('lid')

    if not pid or not lid:
        return jsonify(error='Both "pid" and "lid" parameters are required.'), 400

    product_info = get_flipkart_product_details(pid, lid)
    return jsonify(product_info)

if __name__ == "__main__":
    app.run(debug=True)
