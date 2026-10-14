import csv
import os
from datetime import datetime
from pathlib import Path
from config import BUYERS_CSV, SENT_LOG_CSV, BUSINESS_EMAILS_CSV, INDIVIDUAL_EMAILS_CSV

def init_csv_files():
    Path(BUYERS_CSV).parent.mkdir(parents=True, exist_ok=True)
    
    if not os.path.exists(BUYERS_CSV):
        with open(BUYERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'buyer_name', 'company_name', 'website', 'country', 'source_platform', 'discovered_at'])
            
    if not os.path.exists(SENT_LOG_CSV):
        with open(SENT_LOG_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'buyer_name', 'company_name', 'status', 'timestamp', 'error_detail'])

    if not os.path.exists(BUSINESS_EMAILS_CSV):
        with open(BUSINESS_EMAILS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'buyer_name', 'company_name', 'website', 'country', 'source_platform'])

    if not os.path.exists(INDIVIDUAL_EMAILS_CSV):
        with open(INDIVIDUAL_EMAILS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'buyer_name', 'company_name', 'website', 'country', 'source_platform'])

def get_existing_emails():
    init_csv_files()
    emails = set()
    if os.path.exists(BUYERS_CSV):
        with open(BUYERS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('email'):
                    emails.add(row['email'].strip().lower())
    return emails

def get_sent_emails():
    init_csv_files()
    sent_emails = set()
    if os.path.exists(SENT_LOG_CSV):
        with open(SENT_LOG_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('status') == 'sent' and row.get('email'):
                    sent_emails.add(row['email'].strip().lower())
    return sent_emails

def log_buyers(buyer_records):
    init_csv_files()
    existing = get_existing_emails()
    added_count = 0
    with open(BUYERS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for r in buyer_records:
            email = r.get('email', '').strip().lower()
            if email and email not in existing:
                writer.writerow([
                    email,
                    r.get('buyer_name', 'Valued Customer'),
                    r.get('company_name', ''),
                    r.get('website', ''),
                    r.get('country', ''),
                    r.get('source_platform', 'Unknown'),
                    datetime.now().isoformat()
                ])
                existing.add(email)
                added_count += 1
    return added_count

def log_send_attempt(email, buyer_name, company_name, status, error_detail=""):
    init_csv_files()
    with open(SENT_LOG_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            email,
            buyer_name,
            company_name,
            status,
            datetime.now().isoformat(),
            error_detail
        ])

def get_sent_log_history():
    init_csv_files()
    records = []
    if os.path.exists(SENT_LOG_CSV):
        with open(SENT_LOG_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    return records
