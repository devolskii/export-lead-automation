import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
from extraction.data_extractor import normalize_buyer_record

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def crawl_site_for_content(url: str) -> str:
    """Fetch website HTML snippet with a short timeout to extract contact info."""
    if not url or not url.startswith(('http://', 'https://')):
        return ''
    try:
        resp = requests.get(url, headers=HEADERS, timeout=4)
        content_type = resp.headers.get('Content-Type', '').lower()
        if resp.status_code == 200 and ('html' in content_type or not content_type):
            return resp.text[:35000]
    except Exception:
        pass
    return ''

def search_duckduckgo_html(query: str, max_items: int = 15) -> list[dict]:
    """Fallback search using DuckDuckGo HTML endpoint."""
    items = []
    url = 'https://html.duckduckgo.com/html/'
    data = {'q': query}
    try:
        resp = requests.post(url, data=data, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            for div in soup.find_all('div', class_='result'):
                title_elem = div.find('h2', class_='result__title')
                title = title_elem.get_text(strip=True) if title_elem else ''

                a_tag = div.find('a', class_='result__a') or div.find('a', class_='result__url')
                href = a_tag['href'] if a_tag and a_tag.has_attr('href') else ''
                if 'uddg=' in href:
                    href = unquote(href.split('uddg=')[1].split('&')[0])

                snippet_elem = div.find('a', class_='result__snippet')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''

                if href and href.startswith('http'):
                    items.append({
                        'title': title,
                        'href': href,
                        'body': snippet
                    })
                if len(items) >= max_items:
                    break
    except Exception as e:
        print(f"[DuckDuckGo HTML Fallback] Error: {e}")
    return items

def search_duckduckgo(keyword: str, max_results: int = 10, city: str = '', country: str = '') -> list[dict]:
    """
    Search DuckDuckGo for potential buyers/importers and extract verified contact emails.
    Uses DDGS client with automatic fallback to DuckDuckGo HTML endpoint and deep-page extraction.
    """
    records = []
    seen_emails = set()
    loc_parts = [p.strip() for p in [city, country] if p.strip()]
    loc_terms = " ".join(f'"{p}"' for p in loc_parts)
    loc_clause = f' {loc_terms}' if loc_terms else ''
    loc_str = ", ".join(loc_parts)

    queries = [
        f'"{keyword}"{loc_clause} "contact" "email" buyer OR importer',
        f'"{keyword}"{loc_clause} wholesale distributor contact email'
    ]

    location_log = f" in {loc_str}" if loc_str else ""
    print(f"[DuckDuckGo API] Discovering buyer leads for: '{keyword}'{location_log}...")

    for query in queries:
        raw_items = []

        # 1. Try DDGS library
        try:
            from ddgs import DDGS
            raw_items = list(DDGS().text(query, max_results=max_results))
        except Exception:
            pass

        # 2. Fall back to DuckDuckGo HTML if DDGS returned no items
        if not raw_items:
            raw_items = search_duckduckgo_html(query, max_items=max_results)

        # 3. Process items and extract contacts
        for item in raw_items:
            title = item.get('title', '')
            body = item.get('body', '')
            href = item.get('href', '')

            # A. First check snippet
            extracted = normalize_buyer_record({
                'content': f"{title} {body}",
                'website': href,
                'title': title,
                'city': city,
                'country': country,
                'source_platform': 'DuckDuckGo API'
            })

            # B. If snippet had no email, crawl the target website
            if not extracted and href and href.startswith('http'):
                page_content = crawl_site_for_content(href)
                if not page_content:
                    # Try root domain
                    parsed = urlparse(href)
                    root_url = f"{parsed.scheme}://{parsed.netloc}"
                    if root_url != href:
                        page_content = crawl_site_for_content(root_url)

                if page_content:
                    extracted = normalize_buyer_record({
                        'content': page_content,
                        'website': href,
                        'title': title,
                        'city': city,
                        'country': country,
                        'source_platform': 'DuckDuckGo API (Deep Crawl)'
                    })

            for rec in extracted:
                if rec['email'] not in seen_emails:
                    seen_emails.add(rec['email'])
                    records.append(rec)

            if len(records) >= max_results:
                break

        if len(records) >= max_results:
            break

    print(f"[DuckDuckGo API] Discovered {len(records)} verified buyer contact records.")
    return records
