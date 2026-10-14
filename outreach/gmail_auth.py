import smtplib
import ssl

def connect_gmail_smtp(email: str, app_password: str):
    if not email or not app_password:
        raise ValueError("Gmail email and App Password must be configured in settings/.env.")
        
    context = ssl.create_default_context()
    try:
        # Connect via STARTTLS on port 587
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(email, app_password)
        return server
    except Exception as e:
        # Fallback to SSL on port 465
        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=15)
            server.login(email, app_password)
            return server
        except Exception as fallback_e:
            raise RuntimeError(f"SMTP Authentication failed for {email}: {e} | Fallback SSL error: {fallback_e}")
