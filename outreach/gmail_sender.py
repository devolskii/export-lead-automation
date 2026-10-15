import time
import smtplib
import re
import uuid
import base64
from pathlib import Path
from email.message import EmailMessage
from bs4 import BeautifulSoup
from outreach.gmail_auth import connect_gmail_smtp
from outreach.attachment_handler import attach_presentation
from app_logging.activity_logger import get_sent_emails, log_send_attempt
from config import load_settings

def build_personalized_message(subject_template: str, body_template: str, buyer: dict, sender_email: str, monitor_email: str) -> EmailMessage:
    msg = EmailMessage()
    
    buyer_name = buyer.get('buyer_name', 'Valued Customer')
    company_name = buyer.get('company_name', '')
    
    subject = subject_template.replace('{{buyer_name}}', buyer_name).replace('{{company_name}}', company_name)
    body_content = body_template.replace('{{buyer_name}}', buyer_name).replace('{{company_name}}', company_name)
    
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = buyer.get('email')
    
    if monitor_email:
        msg['Cc'] = monitor_email

    # Check if content has HTML tags
    is_html = bool(re.search(r'<[a-z][\s\S]*>', body_content, re.IGNORECASE))
    
    if not is_html:
        paragraphs = body_content.split('\n\n')
        html_paragraphs = "".join(f"<p>{p.replace(chr(10), '<br>')}</p>" for p in paragraphs if p.strip())
        raw_html = f"<!DOCTYPE html><html><body>{html_paragraphs}</body></html>"
        plain_text = body_content
    else:
        raw_html = body_content
        soup = BeautifulSoup(raw_html, 'html.parser')
        plain_text = soup.get_text(separator='\n').strip()

    soup = BeautifulSoup(raw_html, 'html.parser')
    inline_images = []

    # Process all <img> tags for inline attachments
    for i, img in enumerate(soup.find_all('img')):
        src = img.get('src', '')
        if src.startswith('data:image/'):
            # Embedded base64 data URI
            match = re.match(r'^data:image/([a-zA-Z0-9\+\-]+);base64,(.+)$', src, re.DOTALL)
            if match:
                subtype = match.group(1).lower()
                if subtype == 'jpg':
                    subtype = 'jpeg'
                b64_data = match.group(2).strip()
                try:
                    img_bytes = base64.b64decode(b64_data)
                    cid = f"img_{i}_{uuid.uuid4().hex[:8]}@export.pipeline"
                    img['src'] = f"cid:{cid}"
                    inline_images.append((cid, img_bytes, 'image', subtype))
                except Exception as e:
                    print(f"[Gmail Sender] Warning: Failed to decode base64 image {i}: {e}")
        elif not src.startswith(('http://', 'https://', 'cid:')) and src.strip():
            # Local relative or web-root file path
            clean_src = src.lstrip('/')
            local_path = Path(__file__).resolve().parent.parent / clean_src
            if not local_path.exists() or not local_path.is_file():
                local_path = Path(src)
                
            if local_path.exists() and local_path.is_file():
                try:
                    with open(local_path, 'rb') as f:
                        img_bytes = f.read()
                    subtype = local_path.suffix.lstrip('.').lower()
                    if subtype == 'jpg':
                        subtype = 'jpeg'
                    cid = f"img_{i}_{uuid.uuid4().hex[:8]}@export.pipeline"
                    img['src'] = f"cid:{cid}"
                    inline_images.append((cid, img_bytes, 'image', subtype))
                except Exception as e:
                    print(f"[Gmail Sender] Warning: Failed to attach local image {src}: {e}")

    final_html = str(soup)

    # 1. Plain text fallback
    msg.set_content(plain_text)

    # 2. Rich HTML alternative
    msg.add_alternative(final_html, subtype='html')

    # 3. Attach inline related images
    if inline_images:
        html_part = msg.get_payload()[-1]
        for cid, img_bytes, maintype, subtype in inline_images:
            html_part.add_related(img_bytes, maintype=maintype, subtype=subtype, cid=f"<{cid}>")

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
    attach_file = attachment_path if attachment_path is not None else settings.get('presentation_path')
    
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
                if attach_file and str(attach_file).strip():
                    attach_presentation(msg, str(attach_file).strip())
                    
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
