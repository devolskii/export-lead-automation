import csv
import os
from config import BUYERS_CSV, SENT_LOG_CSV, BUSINESS_EMAILS_CSV, INDIVIDUAL_EMAILS_CSV

def generate_summary_report():
    total_discovered = 0
    if os.path.exists(BUYERS_CSV):
        with open(BUYERS_CSV, 'r', encoding='utf-8') as f:
            total_discovered = max(0, sum(1 for row in f) - 1)
            
    total_business = 0
    if os.path.exists(BUSINESS_EMAILS_CSV):
        with open(BUSINESS_EMAILS_CSV, 'r', encoding='utf-8') as f:
            total_business = max(0, sum(1 for row in f) - 1)

    total_individual = 0
    if os.path.exists(INDIVIDUAL_EMAILS_CSV):
        with open(INDIVIDUAL_EMAILS_CSV, 'r', encoding='utf-8') as f:
            total_individual = max(0, sum(1 for row in f) - 1)

    sent_count = 0
    failed_count = 0
    unique_sent_emails = set()
    
    if os.path.exists(SENT_LOG_CSV):
        with open(SENT_LOG_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                status = row.get('status', '').lower()
                if status == 'sent':
                    sent_count += 1
                    unique_sent_emails.add(row.get('email', '').lower())
                elif status == 'failed':
                    failed_count += 1
                    
    total_outreach = sent_count + failed_count
    success_rate = (sent_count / total_outreach * 100) if total_outreach > 0 else 0.0
    
    return {
        'total_discovered': total_discovered,
        'total_business': total_business,
        'total_individual': total_individual,
        'total_outreach_attempts': total_outreach,
        'total_sent': sent_count,
        'total_failed': failed_count,
        'unique_sent': len(unique_sent_emails),
        'success_rate': round(success_rate, 2)
    }
