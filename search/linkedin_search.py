import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from extraction.data_extractor import normalize_buyer_record

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}

def search_linkedin(keyword: str) -> list[dict]:
    records = []
    query = f"site:linkedin.com/in/ OR site:linkedin.com/company/ \"{keyword}\" buyer importer email"
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for r in soup.find_all('div', class_='result'):
                extracted = normalize_buyer_record({
                    'content': r.get_text(),
                    'source_platform': 'LinkedIn'
                })
                records.extend(extracted)
    except Exception as e:
        print(f"[LinkedIn Search] Error: {e}")
    return records
