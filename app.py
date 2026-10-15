import csv
import os
import io
import re
import uuid
import base64
import mimetypes
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify, send_from_directory

from config import load_settings, save_settings, BUYERS_CSV, SENT_LOG_CSV, BUSINESS_EMAILS_CSV, INDIVIDUAL_EMAILS_CSV, BASE_DIR
from app_logging.activity_logger import init_csv_files, get_existing_emails, log_buyers, get_sent_log_history
from validation.email_validator import is_valid_email
from search.google_search import search_google
from search.duckduckgo_search import search_duckduckgo
from search.facebook_search import search_facebook
from search.linkedin_search import search_linkedin
from search.directory_search import search_directory
from search.website_search import search_website
from extraction.ai_classifier import run_classification_pipeline
from outreach.gmail_sender import send_campaign
from reports.report_generator import generate_summary_report

app = Flask(__name__)
app.secret_key = "export-api3-secret-key"

@app.before_request
def setup():
    init_csv_files()

def read_csv_records(filepath):
    records = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get('email', '').strip().lower()
                if email and email != 'email':
                    records.append(row)
    return records

from search.hunter_search import search_hunter_io

@app.route('/')
def home():
    settings = load_settings()
    report = generate_summary_report()
    buyers = read_csv_records(BUYERS_CSV)
    return render_template('index.html', settings=settings, report=report, buyers=buyers[::-1])

@app.route('/run-discovery', methods=['POST'])
def run_discovery():
    settings = load_settings()
    keyword = request.form.get('keyword', '').strip() if 'keyword' in request.form and request.form.get('keyword', '').strip() else settings.get('search_keyword', 'Singing Bowls')
    city = request.form.get('city', '').strip() if 'city' in request.form else settings.get('search_city', '')
    country = request.form.get('country', '').strip() if 'country' in request.form else settings.get('search_country', '')
    
    save_settings({
        'search_keyword': keyword,
        'search_city': city,
        'search_country': country
    })
    
    loc_desc = []
    if city: loc_desc.append(city)
    if country: loc_desc.append(country)
    loc_str = f" in {', '.join(loc_desc)}" if loc_desc else ""
    
    flash(f"Running buyer discovery across Hunter.io, Google, DuckDuckGo, Facebook, LinkedIn, Directories & Web for '{keyword}'{loc_str}...", "info")
    
    all_raw = []
    all_raw.extend(search_hunter_io(keyword, city=city, country=country))
    all_raw.extend(search_google(keyword, city=city, country=country))
    all_raw.extend(search_duckduckgo(keyword, city=city, country=country))
    all_raw.extend(search_facebook(keyword, city=city, country=country))
    all_raw.extend(search_linkedin(keyword, city=city, country=country))
    all_raw.extend(search_directory(keyword, city=city, country=country))
    all_raw.extend(search_website(keyword, city=city, country=country))
    
    added_count = log_buyers(all_raw)
    flash(f"Discovery pipeline finished! Discovered {len(all_raw)} total potential leads, added {added_count} new unique buyers to database.", "success")
    return redirect(url_for('home'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file uploaded", "danger")
            return redirect(url_for('upload'))
        file = request.files['file']
        if file.filename == '':
            flash("No file selected", "danger")
            return redirect(url_for('upload'))
            
        if file and file.filename.endswith('.csv'):
            stream = io.StringIO(file.stream.read().decode("utf8"), newline=None)
            reader = csv.DictReader(stream)
            records = []
            for row in reader:
                if row.get('email') and is_valid_email(row['email']):
                    records.append({
                        'email': row['email'].strip().lower(),
                        'buyer_name': row.get('buyer_name', 'Valued Customer'),
                        'company_name': row.get('company_name', ''),
                        'website': row.get('website', ''),
                        'city': row.get('city', ''),
                        'country': row.get('country', 'International'),
                        'source_platform': row.get('source_platform', 'CSV Import')
                    })
            added = log_buyers(records)
            flash(f"Successfully processed CSV. Added {added} new unique lead records.", "success")
            return redirect(url_for('upload'))
            
    files = [
        ('buyers.csv', BUYERS_CSV),
        ('business_emails.csv', BUSINESS_EMAILS_CSV),
        ('individual_emails.csv', INDIVIDUAL_EMAILS_CSV),
        ('sent_log.csv', SENT_LOG_CSV)
    ]
    file_stats = []
    for name, p in files:
        rows = 0
        size_kb = 0
        if os.path.exists(p):
            size_kb = round(os.path.getsize(p) / 1024, 2)
            with open(p, 'r', encoding='utf-8') as f:
                rows = max(0, sum(1 for line in f) - 1)
        file_stats.append({'name': name, 'rows': rows, 'size': size_kb})
        
    return render_template('upload.html', file_stats=file_stats)

@app.route('/classify', methods=['GET', 'POST'])
def classify():
    if request.method == 'POST':
        res = run_classification_pipeline()
        flash(f"AI Classification complete! Classified {res['total']} contacts ({res['business']} Business, {res['individual']} Individual).", "success")
        return redirect(url_for('classify'))
        
    biz = read_csv_records(BUSINESS_EMAILS_CSV)
    ind = read_csv_records(INDIVIDUAL_EMAILS_CSV)
    return render_template('classify.html', business_buyers=biz[::-1], individual_buyers=ind[::-1])

@app.route('/send', methods=['GET', 'POST'])
def send():
    settings = load_settings()
    
    if request.method == 'POST':
        audience = request.form.get('audience', 'both')
        subject = request.form.get('subject')
        body = request.form.get('body')
        
        # Determine PDF attachment
        attach_pdf = request.form.get('attach_pdf') in ('1', 'true', 'on', 'yes')
        attachment_path = ""
        
        if attach_pdf:
            pdf_file = request.files.get('pdf_file')
            if pdf_file and pdf_file.filename and pdf_file.filename.lower().endswith('.pdf'):
                upload_dir = BASE_DIR / 'assets' / 'attachments'
                upload_dir.mkdir(parents=True, exist_ok=True)
                clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', pdf_file.filename)
                target_pdf = upload_dir / clean_name
                pdf_file.save(str(target_pdf))
                attachment_path = str(target_pdf)
            else:
                custom_path = request.form.get('attachment_path', '').strip()
                attachment_path = custom_path or settings.get('presentation_path', 'assets/company_presentation.pdf')
        
        if audience == 'business':
            buyers = read_csv_records(BUSINESS_EMAILS_CSV)
        elif audience == 'individual':
            buyers = read_csv_records(INDIVIDUAL_EMAILS_CSV)
        else:
            buyers = read_csv_records(BUYERS_CSV)
            
        if not buyers:
            flash("Selected audience queue is empty!", "warning")
            return redirect(url_for('send'))
            
        try:
            res = send_campaign(buyers, custom_subject=subject, custom_body=body, attachment_path=attachment_path)
            flash(f"Campaign launched! Sent: {res['success_count']}, Failed: {res['failed_count']}, Duplicates Skipped: {res['skipped_duplicate_count']}", "info")
        except Exception as e:
            flash(f"Campaign send error: {e}", "danger")
            
        return redirect(url_for('report'))
        
    presentation_path = Path(settings.get('presentation_path', 'assets/company_presentation.pdf'))
    if not presentation_path.is_absolute():
        presentation_path = BASE_DIR / presentation_path
        
    presentation_exists = presentation_path.exists()
    presentation_size = round(os.path.getsize(presentation_path) / 1024, 2) if presentation_exists else 0
    presentation_filename = presentation_path.name if presentation_exists else ''
    
    return render_template(
        'send.html', 
        settings=settings, 
        presentation_exists=presentation_exists, 
        presentation_size=presentation_size,
        presentation_filename=presentation_filename
    )

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file uploaded'}), 400
    file = request.files['image']
    if not file or file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    allowed_exts = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_exts:
        return jsonify({'success': False, 'error': f'Unsupported image format: {ext}'}), 400

    upload_dir = BASE_DIR / 'assets' / 'images'
    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = f"img_{uuid.uuid4().hex[:10]}{ext}"
    target_path = upload_dir / filename
    file.save(str(target_path))

    with open(target_path, 'rb') as f:
        data_b64 = base64.b64encode(f.read()).decode('utf-8')
    mime = mimetypes.guess_type(str(target_path))[0] or 'image/png'
    data_uri = f"data:{mime};base64,{data_b64}"

    return jsonify({
        'success': True,
        'url': f"/assets/images/{filename}",
        'data_uri': data_uri,
        'filename': filename
    })

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(BASE_DIR / 'assets', filename)

@app.route('/report')
def report():
    summary = generate_summary_report()
    logs = get_sent_log_history()
    return render_template('report.html', report=summary, logs=logs[::-1])

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        new_s = {
            'gmail_email': request.form.get('gmail_email', '').strip(),
            'gmail_app_password': request.form.get('gmail_app_password', '').strip(),
            'monitor_email': request.form.get('monitor_email', '').strip(),
            'hunter_api_key': request.form.get('hunter_api_key', '').strip(),
            'google_cse_api_key': request.form.get('google_cse_api_key', '').strip(),
            'google_cse_cx': request.form.get('google_cse_cx', '').strip(),
            'gemini_api_key': request.form.get('gemini_api_key', '').strip(),
            'search_keyword': request.form.get('search_keyword', 'Singing Bowls').strip(),
            'search_city': request.form.get('search_city', '').strip(),
            'search_country': request.form.get('search_country', '').strip(),
            'daily_send_limit': int(request.form.get('daily_send_limit', 100)),
            'send_delay_seconds': float(request.form.get('send_delay_seconds', 2.0)),
            'presentation_path': request.form.get('presentation_path', 'assets/company_presentation.pdf').strip()
        }
        save_settings(new_s)
        flash("Settings updated successfully!", "success")
        return redirect(url_for('settings'))
        
    cur_settings = load_settings()
    return render_template('settings.html', settings=cur_settings)

@app.route('/download-report')
def download_report():
    logs = get_sent_log_history()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['email', 'buyer_name', 'company_name', 'status', 'timestamp', 'error_detail'])
    for log in logs:
        writer.writerow([log.get('email'), log.get('buyer_name'), log.get('company_name'), log.get('status'), log.get('timestamp'), log.get('error_detail')])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=outreach_campaign_report.csv"}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
