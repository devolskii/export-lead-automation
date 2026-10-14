import re

# Comprehensive email extraction and validation regex
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

DISCARD_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.pdf', '.zip', '.js', '.css')
COMMON_PLACEHOLDERS = {'example.com', 'domain.com', 'email.com', 'test.com', 'yourdomain.com', 'sentry.io'}

def is_valid_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip().lower()
    if not EMAIL_REGEX.fullmatch(email):
        return False
        
    for ext in DISCARD_EXTENSIONS:
        if email.endswith(ext):
            return False
            
    parts = email.split('@')
    if len(parts) != 2:
        return False
        
    local, domain = parts
    if len(domain) > 50:
        return False
        
    if domain in COMMON_PLACEHOLDERS:
        return False
        
    return True

def extract_emails_from_text(text: str) -> list[str]:
    if not text:
        return []
    matches = EMAIL_REGEX.findall(text)
    valid_emails = []
    for email in matches:
        email_clean = email.strip().lower()
        if is_valid_email(email_clean):
            valid_emails.append(email_clean)
    return list(set(valid_emails))
