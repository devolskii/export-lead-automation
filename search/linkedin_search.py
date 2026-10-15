import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from extraction.data_extractor import normalize_buyer_record

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}

def search_linkedin(keyword: str, city: str = '', country: str = '') -> list[dict]:
    records = []
    loc_parts = [p.strip() for p in [city, country] if p.strip()]
    loc_terms = " ".join(f'"{p}"' for p in loc_parts)
    loc_clause = f' {loc_terms}' if loc_terms else ''
    query = f"site:linkedin.com/in/ OR site:linkedin.com/company/ \"{keyword}\"{loc_clause} buyer importer email"
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for r in soup.find_all('div', class_='result'):
                extracted = normalize_buyer_record({
                    'content': r.get_text(),
                    'city': city,
                    'country': country,
                    'source_platform': 'LinkedIn'
                })
                records.extend(extracted)
    except Exception as e:
        print(f"[LinkedIn Search] Error: {e}")
    return records
