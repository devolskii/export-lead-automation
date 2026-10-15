import sys
import os
import argparse
from config import load_settings, save_settings
from app_logging.activity_logger import init_csv_files, log_buyers, get_sent_log_history
from search.hunter_search import search_hunter_io
from search.google_search import search_google
from search.duckduckgo_search import search_duckduckgo
from search.facebook_search import search_facebook
from search.linkedin_search import search_linkedin
from search.directory_search import search_directory
from search.website_search import search_website
from extraction.ai_classifier import run_classification_pipeline
from outreach.gmail_sender import send_campaign
from reports.report_generator import generate_summary_report

def run_full_pipeline(keyword_arg=None, city_arg=None, country_arg=None):
    print("==================================================")
    print("      EXPORT AUTOMATION SYSTEM (API 3) RUN        ")
    print("==================================================")
    
    init_csv_files()
    settings = load_settings()
    keyword = keyword_arg or settings.get('search_keyword', 'Singing Bowls')
    city = city_arg if city_arg is not None else settings.get('search_city', '')
    country = country_arg if country_arg is not None else settings.get('search_country', '')
    
    loc_parts = [p.strip() for p in [city, country] if p.strip()]
    loc_desc = f" in {', '.join(loc_parts)}" if loc_parts else ""
    print(f"\n[1/4] Discovering buyers for keyword: '{keyword}'{loc_desc}...")
    all_raw = []
    
    if settings.get('hunter_api_key'):
        print(" -> Searching Hunter.io...")
        all_raw.extend(search_hunter_io(keyword, city=city, country=country))
    print(" -> Searching Google...")
    all_raw.extend(search_google(keyword, city=city, country=country))
    print(" -> Searching DuckDuckGo...")
    all_raw.extend(search_duckduckgo(keyword, city=city, country=country))
    print(" -> Searching Facebook...")
    all_raw.extend(search_facebook(keyword, city=city, country=country))
    print(" -> Searching LinkedIn...")
    all_raw.extend(search_linkedin(keyword, city=city, country=country))
    print(" -> Searching Business Directories...")
    all_raw.extend(search_directory(keyword, city=city, country=country))
    print(" -> Searching Company Websites...")
    all_raw.extend(search_website(keyword, city=city, country=country))
    
    added_count = log_buyers(all_raw)
    print(f"   => Discovered {len(all_raw)} total potential lead records.")
    print(f"   => Added {added_count} new unique buyers to data/buyers.csv.")
    
    print("\n[2/4] Running AI Email Classification...")
    class_res = run_classification_pipeline()
    print(f"   => Classified {class_res['total']} contacts ({class_res['business']} Business, {class_res['individual']} Individual).")
    
    print("\n[3/4] Preparing Automated Gmail Outreach...")
    gmail_email = settings.get('gmail_email')
    app_password = settings.get('gmail_app_password')
    
    if not gmail_email or not app_password:
        print("   [!] Gmail credentials missing in .env or settings.json.")
        print("   [!] Outreach skipped. Please configure GMAIL_EMAIL and GMAIL_APP_PASSWORD.")
    else:
        from app_logging.activity_logger import BUSINESS_EMAILS_CSV
        from app import read_csv_records
        buyers = read_csv_records(BUSINESS_EMAILS_CSV)
        if not buyers:
            from config import BUYERS_CSV
            buyers = read_csv_records(BUYERS_CSV)
            
        print(f"   => Launching send queue for {len(buyers)} buyers...")
        outreach_res = send_campaign(buyers)
        print(f"   => Send Complete: {outreach_res['success_count']} Sent, {outreach_res['failed_count']} Failed, {outreach_res['skipped_duplicate_count']} Skipped Duplicates.")
        
    print("\n[4/4] Summary Report")
    summary = generate_summary_report()
    print("--------------------------------------------------")
    print(f" Total Discovered Buyers  : {summary['total_discovered']}")
    print(f" Total Business Contacts  : {summary['total_business']}")
    print(f" Total Individual Contacts: {summary['total_individual']}")
    print(f" Total Outreach Sent     : {summary['total_sent']}")
    print(f" Total Outreach Failed   : {summary['total_failed']}")
    print(f" Campaign Success Rate   : {summary['success_rate']}%")
    print("--------------------------------------------------")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="EXPORT Automation System (API 3)")
    parser.add_argument('--keyword', type=str, default=None, help="Product or niche search keyword")
    parser.add_argument('--city', type=str, default=None, help="Target city (e.g. London, Berlin, New York)")
    parser.add_argument('--country', type=str, default=None, help="Target country (e.g. United Kingdom, Germany)")
    args = parser.parse_args()
    
    run_full_pipeline(keyword_arg=args.keyword, city_arg=args.city, country_arg=args.country)
