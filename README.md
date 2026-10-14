# Export Lead Automation System 🚀

An end-to-end B2B buyer discovery, AI classification, and automated cold outreach pipeline built with Python, Flask, DuckDuckGo, Google Gemini AI, and Gmail SMTP.

---

## 📌 Overview

The **Export Lead Automation System** streamlines the entire B2B export sales development process:
1. **Discovers prospective international buyers and importers** across multiple search engines and business channels.
2. **Extracts, normalizes, and deduplicates contact data** (company name, contact email, country, website).
3. **Classifies leads with Google Gemini AI** into **Business** vs. **Individual** buyers.
4. **Automates personalized email outreach** with product catalogs and PDF company presentations, respecting daily quotas and send delays.
5. **Provides a Flask Web Dashboard** for real-time campaign monitoring, lead searching, and manual CSV imports.

---

## ✨ Features

- 🔍 **Multi-Channel Lead Discovery**:
  - **DuckDuckGo API**: High-yield search with deep page crawling for contact emails and dual-engine fallback (DDGS + direct HTML).
  - **Google Custom Search API**: Programmable Search Engine (CSE) integration with web search fallback.
  - **Hunter.io API**: Official domain search for verified corporate decision-makers.
  - **Social & Directory Scraping**: Facebook, LinkedIn, and global wholesale business directories.
- 🤖 **AI-Powered Lead Segmentation**:
  - Integrates **Google Gemini API** (`google-genai`) to categorize leads into Business distributors vs. Individual retail consumers.
- 📬 **Automated Cold Outreach**:
  - Secure Gmail SMTP with App Passwords.
  - Automatic PDF presentation attachment handling.
  - Inter-email rate limiting to maintain domain reputation and prevent spam flagging.
  - Duplicate prevention to ensure contacts are never emailed twice.
- 📊 **Interactive Web Dashboard**:
  - Live search and filtering across all discovered leads.
  - Source platform tagging (`DuckDuckGo API`, `Hunter.io`, `Google`, etc.).
  - CSV lead import and exportable campaign reports.

---

## 🛠️ Development Steps & Architecture Timeline

This system was built iteratively across 9 key development phases:

### Phase 1: Modular System Architecture
- Designed a decoupled, modular directory structure dividing concerns into `search/`, `extraction/`, `validation/`, `outreach/`, `reports/`, and `app_logging/`.
- Created centralized configuration management ([config.py](config.py)) that reads environment variables with fallback to [data/settings.json](data/settings.json).

### Phase 2: Contact Normalization & Validation Engine
- Built regex-based email extraction and validation rules ([validation/email_validator.py](validation/email_validator.py)) to filter out web assets (`.png`, `.jpg`, invalid domains).
- Created [extraction/data_extractor.py](extraction/data_extractor.py) to automatically extract buyer names, company names from domains, and infer buyer countries from text context.

### Phase 3: Multi-Source Search Modules
- Implemented search connectors for Google CSE, Hunter.io, Facebook, LinkedIn, and online trade directories.
- Built a unified interface where all search modules output standardized lead dictionaries into the ingestion queue.

### Phase 4: Gemini AI Classification Pipeline
- Integrated Google's official `google-genai` SDK in [extraction/ai_classifier.py](extraction/ai_classifier.py).
- Designed structured prompt engineering to analyze email domains, business context, and company names, sorting leads into `data/business_emails.csv` and `data/individual_emails.csv`.

### Phase 5: Cold Email Outreach Engine
- Built [outreach/gmail_sender.py](outreach/gmail_sender.py) utilizing Python's `smtplib` and `email.mime` modules.
- Implemented template variable replacement (`{{buyer_name}}`), PDF attachment validation, delivery rate limiting (`send_delay_seconds`), and audit logging to `data/sent_log.csv`.

### Phase 6: Flask Management Dashboard
- Built a web GUI ([app.py](app.py)) with Bootstrap 5 templates:
  - **Dashboard (`/`)**: High-level campaign statistics and recent buyer table.
  - **Leads & Upload (`/upload`)**: Manual CSV lead importer and storage stats.
  - **AI Classification (`/classify`)**: Split view of business vs. individual leads.
  - **Campaign Outreach (`/send`)**: Audience selector, custom copy editor, and presentation attachment status.
  - **Analytics Report (`/report`)**: Delivery success rates, failure audit logs, and downloadable CSV reports.
  - **Settings (`/settings`)**: Web-based credential and search parameter manager.

### Phase 7: DuckDuckGo API Integration & Deep Crawler
- Added the `ddgs` library and created [search/duckduckgo_search.py](search/duckduckgo_search.py).
- Engineered a **dual-engine architecture** (DDGS with automatic fallback to DuckDuckGo's direct HTML endpoint) to bypass rate limits and bot challenges.
- Implemented a **deep-page crawler** that visits discovered URLs and root domains to extract contact emails that are absent from short search engine snippets.

### Phase 8: GUI Lead Discovery Optimization
- Upgraded the dashboard table with reverse-chronological ordering (`newest first`), ensuring newly harvested leads appear immediately at the top.
- Added client-side real-time filtering, sticky headers, source badges, and direct website links.
- Sanitized CSV parsers to handle duplicate headers and legacy data cleanly.

### Phase 9: Version Control & Data Privacy Hardening
- Configured [.gitignore](.gitignore) to strictly protect proprietary leads (`data/*.csv`) and credentials (`.env`, `data/settings.json`) from being tracked or exposed to public repositories.

---

## 📁 Project Directory Structure

```text
api-export/
├── app.py                      # Flask Web GUI application & routing
├── main.py                     # CLI pipeline runner
├── config.py                   # Central settings loader (env + JSON)
├── requirements.txt            # Project dependencies
├── .env.example                # Template for environment variables
├── .gitignore                  # Git privacy & exclusion rules
│
├── search/                     # Discovery connectors
│   ├── duckduckgo_search.py    # DuckDuckGo API + deep page crawler
│   ├── google_search.py        # Google Custom Search API connector
│   ├── hunter_search.py        # Hunter.io API lead search
│   ├── facebook_search.py      # Facebook importer search
│   ├── linkedin_search.py      # LinkedIn B2B profile search
│   ├── directory_search.py     # Wholesale trade directory search
│   └── website_search.py       # Direct company website search
│
├── extraction/                 # Lead processing & AI
│   ├── ai_classifier.py        # Google Gemini AI email classifier
│   └── data_extractor.py       # Name, company, & country normalizer
│
├── validation/                 # Validation utilities
│   └── email_validator.py      # Strict email syntax & domain checker
│
├── outreach/                   # Email campaign automation
│   ├── gmail_sender.py         # SMTP sender with rate limiting & tracking
│   ├── gmail_auth.py           # Gmail credentials verifier
│   └── attachment_handler.py   # PDF attachment validator
│
├── app_logging/                # Persistence & logging
│   └── activity_logger.py      # CSV persistence for leads & sent logs
│
├── reports/                    # Campaign analytics
│   └── report_generator.py     # Success rate & metrics compiler
│
├── templates/                  # Bootstrap 5 Jinja2 HTML templates
│   ├── layout.html             # Base sidebar layout
│   ├── index.html              # Main dashboard with live search
│   ├── upload.html             # CSV upload interface
│   ├── classify.html           # Business vs Individual review
│   ├── send.html               # Outreach composer & sender
│   ├── report.html             # Audit logs & report download
│   └── settings.html           # Settings editor
│
├── assets/                     # Outbound campaign assets
│   └── company_presentation.pdf# Company brochure / product catalog
│
└── data/                       # Local database (Git-ignored)
    ├── .gitkeep                # Preserves folder in Git
    ├── buyers.csv              # Master lead database
    ├── business_emails.csv     # AI-classified B2B contacts
    ├── individual_emails.csv   # AI-classified individual contacts
    ├── sent_log.csv            # Outreach audit log
    └── settings.json           # Web-saved credentials & config
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- A Gmail account with an **App Password** enabled ([Google App Passwords Guide](https://support.google.com/accounts/answer/185833))
- *(Optional)* [Google Gemini API Key](https://aistudio.google.com/) for AI classification
- *(Optional)* [Hunter.io API Key](https://hunter.io/) for verified corporate email searches

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/export-lead-automation.git
cd export-lead-automation
```

### 3. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```ini
# Gmail SMTP Credentials
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password
MONITOR_EMAIL=your_email@gmail.com

# Gemini AI (for email segmentation)
GEMINI_API_KEY=your_gemini_api_key

# Optional Search APIs
HUNTER_API_KEY=your_hunter_api_key
GOOGLE_CSE_API_KEY=your_google_cse_api_key
GOOGLE_CSE_CX=your_google_cse_cx_id

# Campaign Configuration
SEARCH_KEYWORD=Singing Bowls
DAILY_SEND_LIMIT=100
SEND_DELAY_SECONDS=2.0
PRESENTATION_PATH=assets/company_presentation.pdf
```

---

## 🖥️ Running the Application

### Option A: Web Dashboard (GUI)
Start the Flask application:
```bash
python app.py
```
Open your browser at **http://localhost:5000** to:
1. Click **"Run Buyer Discovery Pipeline"** to find new leads.
2. Filter leads instantly by typing into the live search bar.
3. Run **Gemini AI Classification** on the `/classify` tab.
4. Launch email outreach directly from the `/send` tab.

### Option B: Command-Line Pipeline (CLI)
To run the automated pipeline headlessly:
```bash
python main.py
```
The CLI runner executes:
1. Multi-source buyer discovery.
2. AI classification.
3. Automated Gmail outreach with PDF presentation attachment.
4. Terminal summary report.

---

## 🔒 Security & Data Privacy

- **No Scraped Leads in Git**: All lead records (`data/*.csv`) are strictly ignored via `.gitignore` and will never be pushed to remote repositories.
- **Credential Protection**: Plaintext passwords and API keys in `.env` and `data/settings.json` are excluded from version control.
- **Safe Template**: Use `.env.example` to share configuration structures without leaking actual secrets.

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
