import json
import csv
import os
from config import BUYERS_CSV, BUSINESS_EMAILS_CSV, INDIVIDUAL_EMAILS_CSV, load_settings

def classify_emails_with_gemini(records: list[dict], api_key: str) -> dict:
    labels = {}
    if not api_key:
        print("[AI Classifier] No Gemini API key provided. Falling back to heuristic classification.")
        for r in records:
            email = r.get('email', '')
            domain = email.split('@')[-1] if '@' in email else ''
            if domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com', 'aol.com']:
                labels[email] = 'individual'
            else:
                labels[email] = 'business'
        return labels

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        prompt = (
            "Classify each of the following email addresses and buyer contexts into either 'business' or 'individual'.\n"
            "Respond ONLY with a JSON object mapping email address to label ('business' or 'individual').\n\n"
            "Contacts:\n"
        )
        for r in records:
            prompt += f"- Email: {r.get('email')}, Company: {r.get('company_name')}, Name: {r.get('buyer_name')}\n"
            
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        labels = json.loads(text)
    except Exception as e:
        print(f"[AI Classifier] Gemini API call error: {e}. Using fallback rule.")
        for r in records:
            email = r.get('email', '')
            domain = email.split('@')[-1] if '@' in email else ''
            if domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']:
                labels[email] = 'individual'
            else:
                labels[email] = 'business'
                
    return labels

def run_classification_pipeline():
    settings = load_settings()
    api_key = settings.get('gemini_api_key', '')
    
    records = []
    if os.path.exists(BUYERS_CSV):
        with open(BUYERS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
                
    if not records:
        return {'total': 0, 'business': 0, 'individual': 0}
        
    labels = classify_emails_with_gemini(records, api_key)
    
    biz_records = []
    ind_records = []
    
    for r in records:
        email = r.get('email')
        label = labels.get(email, 'business')
        if label.lower() == 'individual':
            ind_records.append(r)
        else:
            biz_records.append(r)
            
    with open(BUSINESS_EMAILS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['email', 'buyer_name', 'company_name', 'website', 'city', 'country', 'source_platform'])
        for r in biz_records:
            writer.writerow([r.get('email'), r.get('buyer_name'), r.get('company_name'), r.get('website'), r.get('city', ''), r.get('country'), r.get('source_platform')])

    with open(INDIVIDUAL_EMAILS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['email', 'buyer_name', 'company_name', 'website', 'city', 'country', 'source_platform'])
        for r in ind_records:
            writer.writerow([r.get('email'), r.get('buyer_name'), r.get('company_name'), r.get('website'), r.get('city', ''), r.get('country'), r.get('source_platform')])
            
    return {
        'total': len(records),
        'business': len(biz_records),
        'individual': len(ind_records)
    }
