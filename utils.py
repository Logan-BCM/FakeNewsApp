import hashlib

from bs4 import BeautifulSoup
import requests



# a = '''“We have over 100,000 children, which we’ve never had before, in serious condition, and many on ventilators” due to the coronavirus.'''

def sha256_hash(data):
	sha256 = hashlib.sha256()
	sha256.update(data.encode("utf-8"))
	hashed_data = sha256.hexdigest()
	return hashed_data

def fetch_url_content(url):
    try:
        # Fetch webpage content
        response = requests.get(url)
        if response.status_code == 200:
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract text from HTML
            text = soup.get_text()
            # Remove extra whitespaces and newlines
            text = ' '.join(text.split())
            return text
        else:
            print("Failed to fetch URL:", response.status_code)
            return None
    except Exception as e:
        print("Error fetching URL:", e)
        return None
