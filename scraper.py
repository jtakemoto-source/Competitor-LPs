import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

def scrape_competitor(url):
    headers = {'User-Agent': 'Mozilla/5.0...'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Example: Extract specific elements
    data = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'title': soup.find('title').text if soup.find('title') else '',
        'meta_description': soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else '',
        'h1_tags': [h1.text for h1 in soup.find_all('h1')],
        'prices': [price.text for price in soup.find_all(class_='price')],  # Adjust class name
        'products': [prod.text for prod in soup.find_all(class_='product-title')]  # Adjust
    }

    return data

# Run the scraper
urls = [
    'https://competitor1.com',
    'https://competitor2.com'
]

results = [scrape_competitor(url) for url in urls]
print(json.dumps(results))
