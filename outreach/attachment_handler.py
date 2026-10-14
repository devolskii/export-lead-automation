import os
from email.message import EmailMessage
import mimetypes

def attach_presentation(msg: EmailMessage, filepath: str):
    if not filepath or not os.path.exists(filepath):
        raise FileNotFoundError(f"Presentation attachment file not found at: {filepath}")
        
    ctype, encoding = mimetypes.guess_type(filepath)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
        
    maintype, subtype = ctype.split('/', 1)
    
    with open(filepath, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(filepath)
        
    msg.add_attachment(
        file_data,
        maintype=maintype,
        subtype=subtype,
        filename=file_name
    )
