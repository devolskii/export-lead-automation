import os
from pathlib import Path
from email.message import EmailMessage
import mimetypes
from config import BASE_DIR

def attach_presentation(msg: EmailMessage, filepath: str):
    if not filepath:
        return
        
    path_obj = Path(filepath)
    if not path_obj.is_absolute():
        path_obj = BASE_DIR / path_obj
        
    if not path_obj.exists():
        raise FileNotFoundError(f"PDF attachment file not found at: {path_obj}")
        
    ctype, encoding = mimetypes.guess_type(str(path_obj))
    if ctype is None or encoding is not None:
        if path_obj.suffix.lower() == '.pdf':
            ctype = 'application/pdf'
        else:
            ctype = 'application/octet-stream'
        
    maintype, subtype = ctype.split('/', 1)
    
    with open(path_obj, 'rb') as f:
        file_data = f.read()
        file_name = path_obj.name
        
    msg.add_attachment(
        file_data,
        maintype=maintype,
        subtype=subtype,
        filename=file_name
    )
