import re
from validation.email_validator import extract_emails_from_text, is_valid_email

COUNTRY_KEYWORDS = {
    'usa': 'United States', 'us': 'United States', 'united states': 'United States', 'america': 'United States',
    'uk': 'United Kingdom', 'united kingdom': 'United Kingdom', 'england': 'United Kingdom', 'great britain': 'United Kingdom',
    'germany': 'Germany', 'deutschland': 'Germany',
    'france': 'France', 'canada': 'Canada', 'australia': 'Australia',
    'japan': 'Japan', 'india': 'India', 'nepal': 'Nepal', 'singapore': 'Singapore',
    'netherlands': 'Netherlands', 'holland': 'Netherlands', 'spain': 'Spain', 'italy': 'Italy', 'brazil': 'Brazil',
    'switzerland': 'Switzerland', 'austria': 'Austria', 'belgium': 'Belgium', 'sweden': 'Sweden', 'norway': 'Norway',
    'denmark': 'Denmark', 'finland': 'Finland', 'new zealand': 'New Zealand', 'south africa': 'South Africa',
    'united arab emirates': 'United Arab Emirates', 'uae': 'United Arab Emirates', 'dubai': 'United Arab Emirates',
    'mexico': 'Mexico', 'china': 'China', 'south korea': 'South Korea', 'korea': 'South Korea'
}

CITY_KEYWORDS = {
    'new york': ('New York', 'United States'),
    'los angeles': ('Los Angeles', 'United States'),
    'chicago': ('Chicago', 'United States'),
    'houston': ('Houston', 'United States'),
    'san francisco': ('San Francisco', 'United States'),
    'miami': ('Miami', 'United States'),
    'seattle': ('Seattle', 'United States'),
    'austin': ('Austin', 'United States'),
    'boston': ('Boston', 'United States'),
    'london': ('London', 'United Kingdom'),
    'manchester': ('Manchester', 'United Kingdom'),
    'birmingham': ('Birmingham', 'United Kingdom'),
    'edinburgh': ('Edinburgh', 'United Kingdom'),
    'berlin': ('Berlin', 'Germany'),
    'munich': ('Munich', 'Germany'),
    'hamburg': ('Hamburg', 'Germany'),
    'frankfurt': ('Frankfurt', 'Germany'),
    'cologne': ('Cologne', 'Germany'),
    'paris': ('Paris', 'France'),
    'lyon': ('Lyon', 'France'),
    'marseille': ('Marseille', 'France'),
    'toronto': ('Toronto', 'Canada'),
    'vancouver': ('Vancouver', 'Canada'),
    'montreal': ('Montreal', 'Canada'),
    'sydney': ('Sydney', 'Australia'),
    'melbourne': ('Melbourne', 'Australia'),
    'brisbane': ('Brisbane', 'Australia'),
    'tokyo': ('Tokyo', 'Japan'),
    'osaka': ('Osaka', 'Japan'),
    'kyoto': ('Kyoto', 'Japan'),
    'mumbai': ('Mumbai', 'India'),
    'delhi': ('Delhi', 'India'),
    'bangalore': ('Bangalore', 'India'),
    'kathmandu': ('Kathmandu', 'Nepal'),
    'pokhara': ('Pokhara', 'Nepal'),
    'singapore': ('Singapore', 'Singapore'),
    'amsterdam': ('Amsterdam', 'Netherlands'),
    'rotterdam': ('Rotterdam', 'Netherlands'),
    'madrid': ('Madrid', 'Spain'),
    'barcelona': ('Barcelona', 'Spain'),
    'rome': ('Rome', 'Italy'),
    'milan': ('Milan', 'Italy'),
    'dubai': ('Dubai', 'United Arab Emirates'),
    'abu dhabi': ('Abu Dhabi', 'United Arab Emirates'),
    'sao paulo': ('Sao Paulo', 'Brazil'),
    'rio de janeiro': ('Rio de Janeiro', 'Brazil'),
    'zurich': ('Zurich', 'Switzerland'),
    'geneva': ('Geneva', 'Switzerland'),
    'vienna': ('Vienna', 'Austria')
}

def infer_city(text: str) -> str:
    if not text:
        return ''
    text_lower = text.lower()
    for kw, (city_name, _) in CITY_KEYWORDS.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            return city_name
    return ''

def infer_country(text: str) -> str:
    if not text:
        return 'International'
    text_lower = text.lower()
    # First check if city keyword reveals country
    for kw, (_, country_name) in CITY_KEYWORDS.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            return country_name
    for kw, name in COUNTRY_KEYWORDS.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            return name
    return 'International'

def normalize_buyer_record(raw_dict: dict) -> list[dict]:
    records = []
    content = raw_dict.get('content', '')
    emails = extract_emails_from_text(content)
    
    # Also check if explicit email key provided
    if raw_dict.get('email') and is_valid_email(raw_dict['email']):
        emails.append(raw_dict['email'].lower())
        
    emails = list(set(emails))
    combined_context = f"{content} {raw_dict.get('title', '')} {raw_dict.get('company_name', '')}".strip()
    
    for email in emails:
        # Default name extraction fallback
        name = raw_dict.get('buyer_name', '').strip()
        if not name:
            local_part = email.split('@')[0]
            name = local_part.replace('.', ' ').replace('_', ' ').title()
            
        company = raw_dict.get('company_name', '').strip()
        if not company:
            domain = email.split('@')[1]
            domain_name = domain.split('.')[0]
            if domain_name not in ['gmail', 'yahoo', 'hotmail', 'outlook', 'icloud', 'aol', 'protonmail', 'zoho']:
                company = domain_name.title()
            else:
                company = "Import / Distribution"
                
        city = raw_dict.get('city', '').strip()
        if not city:
            city = infer_city(combined_context)

        country = raw_dict.get('country', '').strip()
        if not country or country == 'International':
            country = infer_country(combined_context)

        record = {
            'email': email,
            'buyer_name': name,
            'company_name': company,
            'website': raw_dict.get('website', ''),
            'city': city,
            'country': country or 'International',
            'source_platform': raw_dict.get('source_platform', 'Web Search')
        }
        records.append(record)
        
    return records
