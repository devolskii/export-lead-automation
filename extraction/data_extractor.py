import re
from validation.email_validator import extract_emails_from_text, is_valid_email

COUNTRY_KEYWORDS = {
    'usa': 'United States', 'us': 'United States', 'united states': 'United States',
    'uk': 'United Kingdom', 'united kingdom': 'United Kingdom', 'england': 'United Kingdom',
    'germany': 'Germany', 'deutschland': 'Germany',
    'france': 'France', 'canada': 'Canada', 'australia': 'Australia',
    'japan': 'Japan', 'india': 'India', 'nepal': 'Nepal', 'singapore': 'Singapore',
    'netherlands': 'Netherlands', 'spain': 'Spain', 'italy': 'Italy', 'brazil': 'Brazil'
}

def infer_country(text: str) -> str:
    if not text:
        return 'International'
    text_lower = text.lower()
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
                
        country = raw_dict.get('country', '')
        if not country:
            country = infer_country(content + " " + raw_dict.get('title', ''))

        record = {
            'email': email,
            'buyer_name': name,
            'company_name': company,
            'website': raw_dict.get('website', ''),
            'country': country,
            'source_platform': raw_dict.get('source_platform', 'Web Search')
        }
        records.append(record)
        
    return records
