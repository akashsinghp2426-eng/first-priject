"""Gmail IMAP/SMTP connector."""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime
import base64
from bs4 import BeautifulSoup

from .base_connector import BaseEmailConnector, EmailMessage


class GmailConnector(BaseEmailConnector):
    """Gmail-specific email connector using IMAP and SMTP."""
    
    # Gmail server settings
    IMAP_SERVER = 'imap.gmail.com'
    IMAP_PORT = 993
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    
    def __init__(self, email_address: str, password: str, config: dict = None):
        super().__init__(email_address, password, config)
        self.imap_client = None
        self.smtp_client = None
    
    def connect(self) -> bool:
        """Connect to Gmail IMAP server."""
        try:
            # Connect to IMAP
            self.imap_client = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
            self.imap_client.login(self.email_address, self.password)
            self.imap_client.select('INBOX')
            self.connected = True
            return True
        except Exception as e:
            print(f"Gmail connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Gmail servers."""
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
        """Fetch emails from Gmail."""
        if not self.connected:
            raise Exception("Not connected to Gmail")
        
        emails = []
        try:
            # Select folder
            self.imap_client.select(folder)
            
            # Search criteria
            search_criteria = 'UNSEEN' if unread_only else 'ALL'
            status, messages = self.imap_client.search(None, search_criteria)
            
            if status != 'OK':
                return emails
            
            # Get message IDs (limit to recent ones)
            msg_ids = messages[0].split()
            msg_ids = msg_ids[-limit:] if len(msg_ids) > limit else msg_ids
            
            for msg_id in reversed(msg_ids):  # Most recent first
                try:
                    status, msg_data = self.imap_client.fetch(msg_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    
                    # Extract email components
                    subject = email_message.get('Subject', '')
                    sender = email_message.get('From', '')
                    recipients = email_message.get('To', '').split(',')
                    date_str = email_message.get('Date', '')
                    
                    # Parse date
                    try:
                        date = datetime.strptime(date_str[:25], '%a, %d %b %Y %H:%M:%S')
                    except:
                        date = datetime.now()
                    
                    # Get body
                    body, html_body = self._get_email_body(email_message)
                    
                    # Check if read
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
        """Extract plain text and HTML body from email."""
        body = ""
        html_body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                try:
                    if content_type == "text/plain":
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True).decode(charset, errors='ignore')
                    elif content_type == "text/html":
                        charset = part.get_content_charset() or 'utf-8'
                        html_body = part.get_payload(decode=True).decode(charset, errors='ignore')
                        # Also extract text from HTML
                        if not body:
                            soup = BeautifulSoup(html_body, 'html.parser')
                            body = soup.get_text(separator='\n', strip=True)
                except Exception:
                    continue
        else:
            # Non-multipart email
            try:
                charset = email_message.get_content_charset() or 'utf-8'
                body = email_message.get_payload(decode=True).decode(charset, errors='ignore')
            except Exception:
                body = ""
        
        return body, html_body
    
    def mark_as_read(self, email_id: str):
        """Mark email as read in Gmail."""
        if not self.connected:
            raise Exception("Not connected to Gmail")
        
        try:
            self.imap_client.store(email_id.encode(), '+FLAGS', '\\Seen')
        except Exception as e:
            print(f"Error marking email as read: {e}")
    
    def send_email(self, to: str, subject: str, body: str, in_reply_to: str = None):
        """Send email via Gmail SMTP."""
        try:
            # Connect to SMTP
            self.smtp_client = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
            self.smtp_client.starttls()
            self.smtp_client.login(self.email_address, self.password)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to
            msg['Subject'] = subject
            
            if in_reply_to:
                msg['In-Reply-To'] = in_reply_to
                msg['References'] = in_reply_to
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send
            self.smtp_client.send_message(msg)
            self.smtp_client.quit()
            
        except Exception as e:
            print(f"Error sending email: {e}")
            if self.smtp_client:
                self.smtp_client.quit()
            raise
    
    def move_email(self, email_id: str, destination_folder: str):
        """Move email to different folder in Gmail."""
        if not self.connected:
            raise Exception("Not connected to Gmail")
        
        try:
            # Gmail uses labels, copy to new label then delete from INBOX
            self.imap_client.copy(email_id.encode(), destination_folder)
            self.imap_client.store(email_id.encode(), '+FLAGS', '\\Deleted')
            self.imap_client.expunge()
        except Exception as e:
            print(f"Error moving email: {e}")
