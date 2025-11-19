import os
import json
import mimetypes
from uuid import uuid4
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

bp = Blueprint('upload', __name__, url_prefix='/upload')

BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DATA_FILE = os.path.join(BASE_DIR, 'uploads_data.json')

PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
CLIENT_SECRETS_FILE = os.path.join(PROJECT_ROOT, 'client_secrets.json')
TOKEN_FILE = os.path.join(PROJECT_ROOT, 'token.json')

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
  allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'docx', 'txt'})
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def get_drive_service_oauth():
    """
    Returns an authorized Drive v3 service.
    If token.json doesn't exist, runs local server flow to create it (opens browser).
    """
    if not os.path.exists(CLIENT_SECRETS_FILE):
        raise RuntimeError(f"client_secrets.json not found at {CLIENT_SECRETS_FILE}. Download from Google Cloud Console.")

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        # refresh if possible
        if creds and creds.expired and creds.refresh_token:
            try:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
                    f.write(creds.to_json())
            except Exception:
                creds = None
        else:
            # interactive flow to create token.json (one-time)
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
            with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
                f.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    return service


@bp.route('/')
def upload_form():

    user_id = session.get('user_id')
    if user_id is None:
        return redirect('/auth/login')
    
    return render_template('upload.html')

@bp.route('/', methods=['POST'])
def upload_file():

    if 'file' not in request.files:
        flash('No file part.')
        return redirect(request.url)
   
    file = request.files['file']


    doc_type = request.form.get('doc_type', '')
    subject = request.form.get('subject', '')
    semester = request.form.get('semester', '')
    year = request.form.get('year', '')
    uploaded_by = request.form.get('teacher', '')

    if file.filename == '':
        flash('No selected file.')
        return redirect(request.url)


    if not allowed_file(file.filename):
        flash('Please upload a valid PDF, DOCX, or TXT file.')
        return redirect(request.url)
    
    max_size = current_app.config.get('MAX_CONTENT_LENGTH')
    try:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if max_size and size > max_size:
            flash('File too large.')
            return redirect(request.url)
    except Exception:
        pass

    original = secure_filename(file.filename)
    unique_name = f"{uuid4().hex}_{original}"
    local_path = os.path.join(UPLOAD_FOLDER, unique_name)

    try:
        file.save(local_path)


        mime_type, _ = mimetypes.guess_type(local_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        

        drive_service = get_drive_service_oauth()


        metadata = {'name': original}
        parent_id = current_app.config.get('DRIVE_PARENT_FOLDER_ID')
        if parent_id:
            metadata['parents'] = [parent_id]


        media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
        created = drive_service.files().create(body=metadata, media_body=media, fields='id,webViewLink').execute()
        file_id = created.get('id')

        try:
            drive_service.permissions().create(
                fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
            fields='id'
            ).execute()
        except HttpError as e:
            current_app.logger.warning('Could not create public permission: %s', e)


        link = created.get('webViewLink') or f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
        
        record = {
                    "type": doc_type,
                    "subject": subject,
                    "semester": semester,
                    "year": year,
                    "uploaded_by": uploaded_by,
                    "drive_link": link,
                    "drive_id": file_id,
                    "original_filename": original
                }
        
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception:
                data = []
        
        else:
            data = []


        data.append(record)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        flash(f'{doc_type or "Document"} for {subject or "(no subject)"} uploaded successfully!')
        
        return redirect(url_for('upload.upload_form'))
    
    except Exception as e:
        current_app.logger.exception('Upload failed')
        flash(f'Upload failed: {e}')
        return redirect(request.url)
    
    finally:
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
        except Exception:
            pass
