import os
import pickle
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type
from google.oauth2.credentials import Credentials

SCOPES = ['https://mail.google.com/']

def get_credentials():
        flow = InstalledAppFlow.from_client_secrets_file('config.json', SCOPES)
        credentials = flow.run_local_server()
        return credentials  

credentials = get_credentials()
access_token = credentials.token
refresh_token = credentials.refresh_token



def get_gmail_service(self, access_token):
    creds = Credentials(access_token)
    service = build('gmail', 'v1', credentials=creds)
    return service

gmail_service = get_gmail_service(access_token)

# Wenn das Zugangstoken abläuft, kannst du es mit dem Refresh-Token erneuern:
if credentials.expired:
    credentials.refresh(Request())
    access_token = credentials.token



def parse_parts(service, parts, folder_name,message):
    
    if parts:
        for part in parts:
            filename = part.get('filename')
            mimeType = part.get('mimeType')
            body = part.get('body')
            data = body.get('data')
            file_size = body.get('size')
            part_headers = part.get('headers')
            
        print("Filename: ", filename)
        print("MIME Type: ", mimeType)
        print("File Size: ", file_size)
        print("Part Headers: ", part_headers)
        print("Body: ", body)

def read_message(service, message):
    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
    # parts can be the message body, or attachments
    payload = msg['payload']
    headers = payload.get("headers")
    parts = payload.get("parts")
    folder_name = "email"
    has_subject = False
    if headers:
        # this section prints email basic info & creates a folder for the email
        for header in headers:
            name = header.get("name")
            value = header.get("value")
            if name.lower() == 'from':
                # we print the From address
                print("From:", value)
            if name.lower() == "to":
                # we print the To address
                print("To:", value)
            if name.lower() == "subject":
                # make our boolean True, the email has "subject"
                has_subject = True
                # make a directory with the name of the subject
                
                # we will also handle emails with the same subject name
                folder_counter = 0
                while os.path.isdir(folder_name):
                    folder_counter += 1
                    # we have the same folder name, add a number next to it
                    if folder_name[-1].isdigit() and folder_name[-2] == "_":
                        folder_name = f"{folder_name[:-2]}_{folder_counter}"
                    elif folder_name[-2:].isdigit() and folder_name[-3] == "_":
                        folder_name = f"{folder_name[:-3]}_{folder_counter}"
                    else:
                        folder_name = f"{folder_name}_{folder_counter}"
                os.mkdir(folder_name)
                print("Subject:", value)
            if name.lower() == "date":
                # we print the date when the message was sent
                print("Date:", value)
    if not has_subject:
        # if the email does not have a subject, then make a folder with "email" name
        # since folders are created based on subjects
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
    parse_parts(service, parts, folder_name, message)
    print("="*50)
    
    