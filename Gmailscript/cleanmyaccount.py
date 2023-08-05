from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import json 
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ['https://mail.google.com/']

class Clean():
    def get_credentials():
        flow = InstalledAppFlow.from_client_secrets_file('config.json', SCOPES)
        credentials = flow.run_local_server()
        return credentials  

    credentials = get_credentials()
    access_token = credentials.token
    refresh_token = credentials.refresh_token

    from googleapiclient.discovery import build

    def get_gmail_service(self, access_token):
        creds = Credentials(access_token)
        service = build('gmail', 'v1', credentials=creds)
        return service

    gmail_service = get_gmail_service(access_token)

    # Wenn das Zugangstoken abläuft, kannst du es mit dem Refresh-Token erneuern:
    if credentials.expired:
        credentials.refresh(Request())
        access_token = credentials.token


    list_of_mails = [
        "from:support@musicianonamission.com",
        "from:team@mail.cymatics.fm",
        "from:travel@info.flybillet.dk",
        "from:hello@medium.com",
        "from:thanks@barnerbrand.com"
    ]
    def search_messages(service, query, max_results=500):
        result = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = result.get('messages', [])
        count = result.get('resultSizeEstimate', 0)
        return messages, count

    def  mark_as_starred(self, service, query):   
        messages, count = self.search_messages(service, query, max_results=100)
        for message in messages:
            service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': [], 'addLabelIds': ['STARRED']}).execute()
            count += 1
            print('Message with id: %s was starred' % (message['id']))
            labelids = message
            print(labelids)
            if "unread" in message.get("labelIds",[]):
                print("Message is unread")
                service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                print('Message with id: %s was marked as read' % (message['id']))
                
        
    def extract_sender_emails(self,service, query, max_results=500):
        messages, _ = self.search_messages(service, query, max_results)
        sender_emails = []

        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='metadata', metadataHeaders=['From']).execute()
            sender_email = None
            for header in msg.get('payload', {}).get('headers', []):
                if header['name'] == 'From':
                    sender_email = header['value']
                    break

            if sender_email:
                sender_emails.append(sender_email)

        return sender_emails

    def delete(self, service, query):
        messages, count = self.search_messages(service, query)
        for message in messages:
            service.users().messages().delete(userId='me', id=message['id']).execute()
            count += 1
            print('Message with id: %s was deleted' % (message['id']))
        print(f"deleted {count} emails of {query}")
        return f"deleted {count} emails of {query}"

    def loop_trough_list_of_senders(self,):
        gmail_service = self.get_gmail_service(self.access_token)
        sender_emails = self.extract_sender_emails(gmail_service, query="is:unread", max_results=100)
        pattern = ["news", "info", "team","investorplace","hostelworld","medium","barnerbrand","cymatics","flybillet"
                ,"musicianonamission","mail.cymatics","info.flybillet","mail.cymatics","info.flybillet","medium.com","barnerbrand.com",
                "cymatics.fm","flybillet.dk","musicianonamission.com","noreply", "no-reply", "support", "newsletter", "members","bybiehl", ".eu", "xing",".org","updates"
                ,"facebookmail"
        ]
        for email in sender_emails:
            for word in pattern:
                if word in email:
                    self.delete(gmail_service, f'is:unread from:{email}')
                    print(f"Deleted email from {email}")
                    break  # Stop checking patterns for this email once it's deleted
                else:
                    print(f"Did not delete email from {email}")

gmail_service = Clean().gmail_service
mas = Clean()

if __name__ == '__main__':
    # sender = loop_trough_list_of_senders()
    
    marked = mas.mark_as_starred(gmail_service, "from: learn@itr.mail.codecademy.com")
    print(marked)