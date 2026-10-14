import time
import smtplib
from email.message import EmailMessage
from outreach.gmail_auth import connect_gmail_smtp
from outreach.attachment_handler import attach_presentation
from app_logging.activity_logger import get_sent_emails, log_send_attempt
from config import load_settings

def build_personalized_message(subject_template: str, body_template: str, buyer: dict, sender_email: str, monitor_email: str) -> EmailMessage:
    msg = EmailMessage()
    
    buyer_name = buyer.get('buyer_name', 'Valued Customer')
    company_name = buyer.get('company_name', '')
    
    subject = subject_template.replace('{{buyer_name}}', buyer_name).replace('{{company_name}}', company_name)
    body = body_template.replace('{{buyer_name}}', buyer_name).replace('{{company_name}}', company_name)
    
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = buyer.get('email')
    
    if monitor_email:
        msg['Cc'] = monitor_email
        
    msg.set_content(body)
    return msg

def send_campaign(buyers: list[dict], custom_subject: str = None, custom_body: str = None, attachment_path: str = None) -> dict:
    settings = load_settings()
    gmail_email = settings.get('gmail_email')
    app_password = settings.get('gmail_app_password')
    monitor_email = settings.get('monitor_email')
    delay = float(settings.get('send_delay_seconds', 2.0))
    limit = int(settings.get('daily_send_limit', 100))
    
    subject_tmpl = custom_subject or settings.get('default_subject')
    body_tmpl = custom_body or settings.get('default_body')
    attach_file = attachment_path or settings.get('presentation_path')
    
    already_sent = get_sent_emails()
    
    # Filter out already sent contacts
    queue = [b for b in buyers if b.get('email', '').strip().lower() not in already_sent]
    queue = queue[:limit]
    
    if not queue:
        return {
            'total_queued': 0,
            'success_count': 0,
            'failed_count': 0,
            'skipped_duplicate_count': len(buyers),
            'successful': [],
            'failed': []
        }
        
    server = connect_gmail_smtp(gmail_email, app_password)
    
    success_count = 0
    failed_count = 0
    successful_list = []
    failed_list = []
    
    try:
        for buyer in queue:
            email = buyer.get('email', '').strip()
            name = buyer.get('buyer_name', '')
            company = buyer.get('company_name', '')
            
            try:
                msg = build_personalized_message(subject_tmpl, body_tmpl, buyer, gmail_email, monitor_email)
                if attach_file:
                    attach_presentation(msg, attach_file)
                    
                # Try sending message
                try:
                    server.send_message(msg)
                except smtplib.SMTPServerDisconnected:
                    print("[Gmail Sender] Server disconnected. Reconnecting...")
                    server = connect_gmail_smtp(gmail_email, app_password)
                    server.send_message(msg)
                    
                log_send_attempt(email, name, company, 'sent')
                success_count += 1
                successful_list.append(email)
                time.sleep(delay)
                
            except Exception as e:
                err_msg = str(e)
                log_send_attempt(email, name, company, 'failed', err_msg)
                failed_count += 1
                failed_list.append({'email': email, 'error': err_msg})
                
    finally:
        try:
            server.quit()
        except Exception:
            pass
            
    return {
        'total_queued': len(queue),
        'success_count': success_count,
        'failed_count': failed_count,
        'skipped_duplicate_count': len(buyers) - len(queue),
        'successful': successful_list,
        'failed': failed_list
    }
