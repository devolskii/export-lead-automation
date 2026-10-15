import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from extraction.data_extractor import normalize_buyer_record
from config import load_settings

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def search_google_custom_search_api(keyword: str, api_key: str, cx: str, city: str = '', country: str = '') -> list[dict]:
    records = []
    loc_parts = [p.strip() for p in [city, country] if p.strip()]
    loc_terms = " ".join(f'"{p}"' for p in loc_parts)
    loc_clause = f' {loc_terms}' if loc_terms else ''
    query = f"{keyword}{loc_clause} buyer importer contact email"
    url = "https://www.googleapis.com/customsearch/v1"
    
    # Run up to 2 pages of 10 items
    for start in [1, 11]:
        params = {
            'key': api_key,
            'cx': cx,
            'q': query,
            'start': start
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get('items', [])
                for item in items:
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    link = item.get('link', '')
                    
                    extracted = normalize_buyer_record({
                        'content': f"{title} {snippet}",
                        'website': link,
                        'city': city,
                        'country': country,
                        'source_platform': 'Google CSE API'
                    })
                    records.extend(extracted)
            else:
                print(f"[Google CSE API] HTTP Error: {resp.status_code} {resp.text}")
                print("[Google CSE API] Falling back to Web Search Engine...")
                return search_web_fallback(keyword, city=city, country=country)
        except Exception as e:
            print(f"[Google CSE API] Exception: {e}")
            return search_web_fallback(keyword, city=city, country=country)
            
    return records

def search_web_fallback(keyword: str, city: str = '', country: str = '') -> list[dict]:
    records = []
    loc_parts = [p.strip() for p in [city, country] if p.strip()]
    loc_terms = " ".join(f'"{p}"' for p in loc_parts)
    loc_clause = f' {loc_terms}' if loc_terms else ''
    query = f"{keyword}{loc_clause} buyer importer contact email"
    try:
        url = f"https://www.bing.com/search?q={quote_plus(query)}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = soup.find_all('li', class_='b_algo')
            for r in results:
                snippet = r.get_text()
                a_tag = r.find('a')
                link = a_tag['href'] if a_tag and a_tag.has_attr('href') else ''
                extracted = normalize_buyer_record({
                    'content': snippet,
                    'website': link,
                    'city': city,
                    'country': country,
                    'source_platform': 'Google / Web'
                })
                records.extend(extracted)
    except Exception as e:
        print(f"[Web Search Fallback] Error: {e}")
    return records

def search_google(keyword: str, max_pages: int = 2, city: str = '', country: str = '') -> list[dict]:
    settings = load_settings()
    api_key = settings.get('google_cse_api_key', '').strip()
    cx = settings.get('google_cse_cx', '').strip()
    
    if api_key and cx:
        print("[Google Search] Using Official Google Custom Search API...")
        return search_google_custom_search_api(keyword, api_key, cx, city=city, country=country)
        
    print("[Google Search] No Google CSE API Key configured. Using web search fallback...")
    return search_web_fallback(keyword, city=city, country=country)
