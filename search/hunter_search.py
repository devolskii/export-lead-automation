import requests
from extraction.data_extractor import normalize_buyer_record
from config import load_settings

def search_hunter_io(keyword: str, city: str = '', country: str = '') -> list[dict]:
    settings = load_settings()
    api_key = settings.get('hunter_api_key', '').strip()
    if not api_key:
        print("[Hunter.io API] No Hunter API key configured.")
        return []
        
    loc_parts = [p.strip() for p in [city, country] if p.strip()]
    loc_str = f" in {', '.join(loc_parts)}" if loc_parts else ""
    print(f"[Hunter.io API] Discovering leads for keyword/domain: '{keyword}'{loc_str}...")
    records = []
    
    # 1. Discover domains matching the keyword if keyword looks like a domain or search term
    domain = keyword if '.' in keyword else f"{keyword.lower().replace(' ', '')}.com"
    
    url = "https://api.hunter.io/v2/domain-search"
    params = {
        'domain': domain,
        'api_key': api_key,
        'limit': 10
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json().get('data', {})
            emails = data.get('emails', [])
            org = data.get('organization', domain)
            
            for item in emails:
                email_addr = item.get('value')
                first_name = item.get('first_name', '')
                last_name = item.get('last_name', '')
                full_name = f"{first_name} {last_name}".strip() or "Valued Customer"
                position = item.get('position', '')
                
                extracted = normalize_buyer_record({
                    'email': email_addr,
                    'buyer_name': full_name,
                    'company_name': org,
                    'website': f"https://{domain}",
                    'content': f"Position: {position}",
                    'city': city,
                    'country': country,
                    'source_platform': 'Hunter.io API'
                })
                records.extend(extracted)
        else:
            print(f"[Hunter.io API] HTTP Error: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"[Hunter.io API] Exception: {e}")
        
    return records
