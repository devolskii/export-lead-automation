import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from extraction.data_extractor import normalize_buyer_record

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def search_wikipedia_directory(keyword: str, city: str = '', country: str = '') -> list[dict]:
    records = []
    url = "https://en.wikipedia.org/w/api.php"
    loc_parts = [p.strip() for p in [city, country] if p.strip()]
    loc_str = " ".join(loc_parts)
    srsearch = f"{keyword} {loc_str} wholesale distributor company importer".strip()
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': srsearch,
        'format': 'json'
    }
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('query', {}).get('search', [])
            for item in results:
                title = item.get('title', '')
                snippet = item.get('snippet', '')
                extracted = normalize_buyer_record({
                    'content': f"{title} {snippet}",
                    'website': f"https://en.wikipedia.org/wiki/{quote_plus(title)}",
                    'city': city,
                    'country': country,
                    'source_platform': 'Wikipedia Directory API'
                })
                records.extend(extracted)
    except Exception as e:
        print(f"[Wikipedia Directory API] Error: {e}")
    return records

def search_directory(keyword: str, city: str = '', country: str = '') -> list[dict]:
    records = search_wikipedia_directory(keyword, city=city, country=country)
    
    # Direct search fallback
    loc_parts = [p.strip() for p in [city, country] if p.strip()]
    loc_terms = " ".join(f'"{p}"' for p in loc_parts)
    loc_clause = f' {loc_terms}' if loc_terms else ''
    query = f"\"directory\" OR \"importers\" OR \"wholesale\" \"{keyword}\"{loc_clause} contact email"
    url = f"https://www.bing.com/search?q={quote_plus(query)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for r in soup.find_all('li', class_='b_algo'):
                snippet = r.get_text()
                a_tag = r.find('a')
                link = a_tag['href'] if a_tag and a_tag.has_attr('href') else ''
                extracted = normalize_buyer_record({
                    'content': snippet,
                    'website': link,
                    'city': city,
                    'country': country,
                    'source_platform': 'Business Directory'
                })
                records.extend(extracted)
    except Exception as e:
        print(f"[Directory Search] Error: {e}")
        
    return records
