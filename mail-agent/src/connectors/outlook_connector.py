"""Outlook IMAP/SMTP connector."""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup

from .base_connector import BaseEmailConnector, EmailMessage


class OutlookConnector(BaseEmailConnector):
    """Outlook-specific email connector using IMAP and SMTP."""
    
    IMAP_SERVER = 'outlook.office365.com'
    IMAP_PORT = 993
    SMTP_SERVER = 'smtp.office365.com'
    SMTP_PORT = 587
    
    def __init__(self, email_address: str, password: str, config: dict = None):
        super().__init__(email_address, password, config)
        self.imap_client = None
        self.smtp_client = None
    
    def connect(self) -> bool:
        try:
            self.imap_client = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
            self.imap_client.login(self.email_address, self.password)
            self.imap_client.select('INBOX')
            self.connected = True
            return True
        except Exception as e:
            print(f"Outlook connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        try:
            if self.imap_client:
                self.imap_client.close()
                self.imap_client.logout()
            if self.smtp_client:
                self.smtp_client.quit()
        except Exception:
            pass
        finally:
            self.connected = False
    
    def fetch_emails(self, folder: str = 'INBOX', limit: int = 50, unread_only: bool = False) -> List[EmailMessage]:
        if not self.connected:
            raise Exception("Not connected to Outlook")
        
        emails = []
        try:
            self.imap_client.select(folder)
            search_criteria = 'UNSEEN' if unread_only else 'ALL'
            status, messages = self.imap_client.search(None, search_criteria)
            
            if status != 'OK':
                return emails
            
            msg_ids = messages[0].split()
            msg_ids = msg_ids[-limit:] if len(msg_ids) > limit else msg_ids
            
            for msg_id in reversed(msg_ids):
                try:
                    status, msg_data = self.imap_client.fetch(msg_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    subject = email_message.get('Subject', '')
                    sender = email_message.get('From', '')
                    recipients = email_message.get('To', '').split(',')
                    date_str = email_message.get('Date', '')
                    
                    try:
                        date = datetime.strptime(date_str[:25], '%a, %d %b %Y %H:%M:%S')
                    except:
                        date = datetime.now()
                    
                    body, html_body = self._get_email_body(email_message)
                    is_read = '\\Seen' in str(msg_data)
                    
                    email_obj = EmailMessage(
                        id=msg_id.decode(),
                        subject=subject,
                        sender=sender,
                        recipients=[r.strip() for r in recipients],
                        date=date,
                        body=body,
                        html_body=html_body,
                        is_read=is_read
                    )
                    emails.append(email_obj)
                except Exception as e:
                    print(f"Error fetching email {msg_id}: {e}")
                    continue
            
            return emails
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return emails
    
    def _get_email_body(self, email_message) -> tuple:
        body = ""
        html_body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" in content_disposition:
                    continue
                
                try:
                    if content_type == "text/plain":
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True).decode(charset, errors='ignore')
                    elif content_type == "text/html":
                        charset = part.get_content_charset() or 'utf-8'
                        html_body = part.get_payload(decode=True).decode(charset, errors='ignore')
                        if not body:
                            soup = BeautifulSoup(html_body, 'html.parser')
                            body = soup.get_text(separator='\n', strip=True)
                except Exception:
                    continue
        else:
            try:
                charset = email_message.get_content_charset() or 'utf-8'
                body = email_message.get_payload(decode=True).decode(charset, errors='ignore')
            except Exception:
                body = ""
        
        return body, html_body
    
    def mark_as_read(self, email_id: str):
        if not self.connected:
            raise Exception("Not connected to Outlook")
        try:
            self.imap_client.store(email_id.encode(), '+FLAGS', '\\Seen')
        except Exception as e:
            print(f"Error marking email as read: {e}")
    
    def send_email(self, to: str, subject: str, body: str, in_reply_to: str = None):
        try:
            self.smtp_client = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
            self.smtp_client.starttls()
            self.smtp_client.login(self.email_address, self.password)
            
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to
            msg['Subject'] = subject
            
            if in_reply_to:
                msg['In-Reply-To'] = in_reply_to
                msg['References'] = in_reply_to
            
            msg.attach(MIMEText(body, 'plain'))
            self.smtp_client.send_message(msg)
            self.smtp_client.quit()
        except Exception as e:
            print(f"Error sending email: {e}")
            if self.smtp_client:
                self.smtp_client.quit()
            raise
    
    def move_email(self, email_id: str, destination_folder: str):
        if not self.connected:
            raise Exception("Not connected to Outlook")
        try:
            self.imap_client.copy(email_id.encode(), destination_folder)
            self.imap_client.store(email_id.encode(), '+FLAGS', '\\Deleted')
            self.imap_client.expunge()
        except Exception as e:
            print(f"Error moving email: {e}")
