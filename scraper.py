import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import hashlib
import gspread
from google.oauth2.service_account import Credentials

# Your competitor list
COMPETITORS = [
    {"name": "Monday.com", "url": "https://monday.com"},
    {"name": "Atlassian", "url": "https://atlassian.com"},
    {"name": "Notion", "url": "https://notion.com"},
    {"name": "Asana", "url": "https://asana.com"},
    {"name": "Wrike", "url": "https://wrike.com"},
    {"name": "Basecamp", "url": "https://basecamp.com"},
    {"name": "Smartsheet", "url": "https://smartsheet.com"},
    {"name": "Todoist", "url": "https://todoist.com"},
    {"name": "Airtable", "url": "https://airtable.com"}
]

def scrape_competitor(competitor):
    """Scrape headers and key copy from competitor site"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(competitor['url'], headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract key elements (customized for PM tools)
        data = {
            'company': competitor['name'],
            'url': competitor['url'],
            'timestamp': datetime.now().isoformat(),
            'status': 'success',

            # Main headline (h1)
            'main_headline': soup.find('h1').get_text(strip=True) if soup.find('h1') else '',

            # Hero section text (usually h2 or first p in hero)
            'hero_subheadline': soup.find('h2').get_text(strip=True) if soup.find('h2') else '',

            # Meta description (good for tracking positioning)
            'meta_description': '',

            # Page title
            'page_title': soup.find('title').get_text(strip=True) if soup.find('title') else '',

            # CTA buttons text (top 3)
            'cta_buttons': [],

            # Pricing (if on homepage)
            'pricing_mention': '',

            # Feature headlines
            'feature_headlines': []
        }

        # Get meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            data['meta_description'] = meta_desc.get('content', '')

        # Get CTA buttons (common classes/patterns)
        button_selectors = [
            'a.btn-primary', 'a.button', 'button.cta',
            'a[class*="get-started"]', 'a[class*="try-free"]',
            'a[class*="sign-up"]', 'a[class*="demo"]'
        ]

        buttons = []
        for selector in button_selectors:
            found_buttons = soup.select(selector)[:3]  # Top 3 buttons
            buttons.extend([btn.get_text(strip=True) for btn in found_buttons])
        data['cta_buttons'] = list(set(buttons))[:3]  # Unique, max 3

        # Look for pricing mentions
        pricing_elements = soup.find_all(text=lambda t: t and ('pricing' in t.lower() or '/month' in t or '/user' in t))
        if pricing_elements:
            data['pricing_mention'] = pricing_elements[0][:100]  # First 100 chars

        # Get feature headlines (h3s often used for features)
        h3_elements = soup.find_all('h3')[:5]  # Top 5
        data['feature_headlines'] = [h3.get_text(strip=True) for h3 in h3_elements]

        # Create a hash of all content to detect changes
        all_content = json.dumps(data, sort_keys=True)
        data['content_hash'] = hashlib.md5(all_content.encode()).hexdigest()

        return data

    except Exception as e:
        return {
            'company': competitor['name'],
            'url': competitor['url'],
            'timestamp': datetime.now().isoformat(),
            'status': 'error',
            'error': str(e)
        }

def save_to_json(results):
    """Save results to JSON file"""
    filename = f"scrape_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    return filename

def main():
    """Main execution"""
    print("Starting competitor monitoring...")
    results = []

    for competitor in COMPETITORS:
        print(f"Scraping {competitor['name']}...")
        result = scrape_competitor(competitor)
        results.append(result)

        # Print summary
        if result['status'] == 'success':
            print(f"✓ {competitor['name']}: {result['main_headline'][:50]}...")
        else:
            print(f"✗ {competitor['name']}: {result.get('error', 'Unknown error')}")

    # Save results
    filename = save_to_json(results)
    print(f"\nResults saved to {filename}")

    # Print summary
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"\nSummary: {successful}/{len(COMPETITORS)} sites scraped successfully")

    return results

if __name__ == "__main__":
    main()
