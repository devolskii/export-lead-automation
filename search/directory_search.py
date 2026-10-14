import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from extraction.data_extractor import normalize_buyer_record

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def search_wikipedia_directory(keyword: str) -> list[dict]:
    records = []
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': f"{keyword} wholesale distributor company importer",
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
                    'source_platform': 'Wikipedia Directory API'
                })
                records.extend(extracted)
    except Exception as e:
        print(f"[Wikipedia Directory API] Error: {e}")
    return records

def search_directory(keyword: str) -> list[dict]:
    records = search_wikipedia_directory(keyword)
    
    # Direct search fallback
    query = f"\"directory\" OR \"importers\" OR \"wholesale\" \"{keyword}\" contact email"
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
                    'source_platform': 'Business Directory'
                })
                records.extend(extracted)
    except Exception as e:
        print(f"[Directory Search] Error: {e}")
        
    return records
