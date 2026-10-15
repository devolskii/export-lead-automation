import os
import json
from pathlib import Path

# Fallback .env reader if python-dotenv is not installed
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent

# File paths
SETTINGS_FILE = BASE_DIR / "data" / "settings.json"
BUYERS_CSV = BASE_DIR / "data" / "buyers.csv"
BUSINESS_EMAILS_CSV = BASE_DIR / "data" / "business_emails.csv"
INDIVIDUAL_EMAILS_CSV = BASE_DIR / "data" / "individual_emails.csv"
SENT_LOG_CSV = BASE_DIR / "data" / "sent_log.csv"
DEFAULT_PRESENTATION_PATH = BASE_DIR / "assets" / "company_presentation.pdf"

def load_settings():
    default_settings = {
        "gmail_email": os.getenv("GMAIL_EMAIL", ""),
        "gmail_app_password": os.getenv("GMAIL_APP_PASSWORD", ""),
        "monitor_email": os.getenv("MONITOR_EMAIL", ""),
        "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
        "hunter_api_key": os.getenv("HUNTER_API_KEY", ""),
        "google_cse_api_key": os.getenv("GOOGLE_CSE_API_KEY", ""),
        "google_cse_cx": os.getenv("GOOGLE_CSE_CX", ""),
        "search_keyword": os.getenv("SEARCH_KEYWORD", "Singing Bowls"),
        "search_city": os.getenv("SEARCH_CITY", ""),
        "search_country": os.getenv("SEARCH_COUNTRY", ""),
        "daily_send_limit": int(os.getenv("DAILY_SEND_LIMIT", 100)),
        "send_delay_seconds": float(os.getenv("SEND_DELAY_SECONDS", 2.0)),
        "presentation_path": os.getenv("PRESENTATION_PATH", "assets/company_presentation.pdf"),
        "default_subject": "Export Inquiry & Product Catalog",
        "default_body": "Hello {{buyer_name}},\n\nWe are a premium supplier. Attached is our product catalog and presentation.\n\nBest regards,\nExport BD Team"
    }
    
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                default_settings.update(saved)
        except Exception:
            pass
            
    return default_settings

def save_settings(new_settings):
    current = load_settings()
    current.update(new_settings)
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2)
    return current
