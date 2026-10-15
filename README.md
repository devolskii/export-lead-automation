# Export Lead Automation System 🚀

An end-to-end B2B buyer discovery, AI classification, and automated cold outreach pipeline built with Python, Flask, DuckDuckGo, Google Gemini AI, and Gmail SMTP.

---

## 📌 Overview

The **Export Lead Automation System** streamlines the entire B2B export sales development process:
1. **Discovers prospective international buyers and importers** targeted by product niche, **city, and country** across multiple search engines and business channels.
2. **Extracts, normalizes, and deduplicates contact data** (company name, contact email, city, country, website).
3. **Classifies leads with Google Gemini AI** into **Business** vs. **Individual** buyers.
4. **Composes rich HTML outreach emails** with inline images, custom HTML templates, personalized variable injection, and uploaded PDF presentations/catalogs.
5. **Provides an interactive Flask Web Dashboard** for real-time lead harvesting, location-based filtering, WYSIWYG campaign authoring, and downloadable audit reports.

---

## ✨ Features

- 🔍 **Location-Targeted Lead Discovery**:
  - **City & Country Targeting**: Filter lead discovery by specific geographic locations (e.g., city: *London*, country: *United Kingdom*) across all search engines.
  - **DuckDuckGo API**: High-yield search with deep page crawling for contact emails and dual-engine fallback (DDGS + direct HTML).
  - **Google Custom Search API**: Programmable Search Engine (CSE) integration with web search fallback.
  - **Hunter.io API**: Official domain search for verified corporate decision-makers.
  - **Social & Directory Scraping**: Facebook, LinkedIn, Wikipedia, and global wholesale business directories.
  - **Geographic Data Tagging**: Automatically captures and records the city and country for each discovered contact in `data/buyers.csv`.
- 🤖 **AI-Powered Lead Segmentation**:
  - Integrates **Google Gemini API** (`google-genai`) to categorize leads into Business distributors vs. Individual retail consumers.
- ✉️ **Rich Text & HTML Email Composer with Inline Images**:
  - **Visual WYSIWYG Editor**: Full formatting toolbar with Bold, Italic, Underline, Strikethrough, Headings (H1/H2/H3/P), Colors, Highlight, Alignment, Bulleted & Numbered Lists, and Tables.
  - **Embed HTML / Source Code Mode (`</>`)**: Switch seamlessly between visual editing and raw HTML mode to paste or embed custom email templates, banners, CSS styles, or pricing cards.
  - **Inline Images in Email Body**: Insert images via local computer upload, drag-and-drop, clipboard paste (`Ctrl+V`), or web URL.
  - **Automatic CID Attachment Conversion**: Embedded images are automatically converted to standard MIME `cid:` inline attachments, ensuring they display in Gmail, Outlook, and Apple Mail without remote image blocking warnings.
  - **PDF Attachment Uploader**: Upload any `.pdf` presentation or catalog file directly from your computer, or use default server documents with an on/off toggle.
  - **Built-in Outreach Templates**: Pre-packaged templates for B2B Export Intros and Product Catalog MOQ tables.
- 📬 **Automated Cold Outreach**:
  - Secure Gmail SMTP with App Passwords.
  - Dynamic personalization with `{{buyer_name}}` and `{{company_name}}` tokens.
  - Inter-email rate limiting to maintain domain reputation and prevent spam flagging.
  - Duplicate prevention to ensure contacts are never emailed twice.
- 📊 **Interactive Web Dashboard**:
  - Live search bar and location-filtered discovery card.
  - Discovered buyers table with City, Country, Source, and Website columns.
  - CSV lead import and exportable campaign reports.

---

## 🛠️ Development Steps & Architecture Timeline

This system was built iteratively across 10 key development phases:

### Phase 1: Modular System Architecture
- Designed a decoupled, modular directory structure dividing concerns into `search/`, `extraction/`, `validation/`, `outreach/`, `reports/`, and `app_logging/`.
- Created centralized configuration management ([config.py](config.py)) that reads environment variables with fallback to [data/settings.json](data/settings.json).

### Phase 2: Contact Normalization & Validation Engine
- Built regex-based email extraction and validation rules ([validation/email_validator.py](validation/email_validator.py)) to filter out web assets (`.png`, `.jpg`, invalid domains).
- Created [extraction/data_extractor.py](extraction/data_extractor.py) to automatically extract buyer names, company names from domains, and infer buyer cities and countries from text context.

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

### Phase 10: Location-Based Targeting & Rich HTML Email Outreach
- Added **Location-Based Discovery** supporting City and Country filters across all search engines and CLI scripts.
- Enhanced the dashboard with an interactive search card with active location badges and a dedicated City column.
- Upgraded the email campaign dispatcher ([templates/send.html](templates/send.html)) with a dual-mode **Visual WYSIWYG & Embed HTML Editor**, pre-built email templates, and variable insert buttons.
- Implemented inline image embedding via local file upload, clipboard paste, and drag-and-drop, automatically converted to MIME CID inline attachments in [outreach/gmail_sender.py](outreach/gmail_sender.py).
- Added direct **PDF File Upload** support allowing users to attach any custom presentation or catalog PDF directly from their device.

---

## 📁 Project Directory Structure

```text
api-export/
├── app.py                      # Flask Web GUI application & routing
├── main.py                     # CLI pipeline runner with arguments
├── config.py                   # Central settings loader (env + JSON)
├── requirements.txt            # Project dependencies
├── .env.example                # Template for environment variables
├── .gitignore                  # Git privacy & exclusion rules
│
├── search/                     # Discovery connectors (with City & Country support)
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
│   └── data_extractor.py       # Name, company, city, & country normalizer
│
├── validation/                 # Validation utilities
│   └── email_validator.py      # Strict email syntax & domain checker
│
├── outreach/                   # Email campaign automation
│   ├── gmail_sender.py         # SMTP sender with HTML parsing & CID inline images
│   ├── gmail_auth.py           # Gmail credentials verifier
│   └── attachment_handler.py   # PDF attachment validator & resolver
│
├── app_logging/                # Persistence & logging
│   └── activity_logger.py      # CSV persistence for leads & sent logs
│
├── reports/                    # Campaign analytics
│   └── report_generator.py     # Success rate & metrics compiler
│
├── templates/                  # Bootstrap 5 Jinja2 HTML templates
│   ├── layout.html             # Base sidebar layout
│   ├── index.html              # Main dashboard with location search & city column
│   ├── upload.html             # CSV upload interface
│   ├── classify.html           # Business vs Individual review
│   ├── send.html               # Rich WYSIWYG & HTML email composer + PDF uploader
│   ├── report.html             # Audit logs & report download
│   └── settings.html           # Settings editor with default city & country
│
├── assets/                     # Outbound campaign assets
│   ├── company_presentation.pdf# Default company brochure / catalog
│   ├── attachments/            # Uploaded PDF campaign attachments
│   └── images/                 # Uploaded inline email body images
│
└── data/                       # Local database (Git-ignored)
    ├── .gitkeep                # Preserves folder in Git
    ├── buyers.csv              # Master lead database with city & country
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
- *(Optional)* [Google Custom Search API Key & CX ID](https://developers.google.com/custom-search/v1/overview)

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
SEARCH_CITY=Berlin
SEARCH_COUNTRY=Germany
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
1. **Search Leads by Location**: Enter your product keyword and optional **City** and **Country** in the top discovery card, then click **"Find Buyers"**.
2. **Review & Filter**: View discovered buyers with City and Country tags, or filter results in real-time with the search bar.
3. **AI Classification**: Categorize contacts into Business vs. Individual buyers on the `/classify` tab.
4. **Compose & Dispatch Email Campaigns**:
   - Go to the `/send` tab.
   - Use the **Rich Text Toolbar** to format your email, or click **`</> Embed HTML / Source`** to paste custom HTML templates.
   - Click **`🖼️ Insert Image`**, drag-and-drop an image, or paste a screenshot (`Ctrl+V`) directly into the email body.
   - Attach a custom PDF catalog from your device or use the default presentation.
   - Click **"Launch Gmail Outreach Campaign"**.

### Option B: Command-Line Pipeline (CLI)
To run the automated pipeline headlessly:
```bash
python main.py
```

You can also pass custom keyword and location parameters directly from the terminal:
```bash
python main.py --keyword "Singing Bowls" --city "Berlin" --country "Germany"
```

The CLI runner executes:
1. Multi-source buyer discovery targeted by keyword and location.
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
