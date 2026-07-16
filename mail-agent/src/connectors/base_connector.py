"""Base email connector interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EmailMessage:
    """Represents an email message."""
    id: str
    subject: str
    sender: str
    recipients: List[str]
    date: datetime
    body: str
    html_body: Optional[str] = None
    attachments: List[str] = None
    is_read: bool = False
    flags: List[str] = None
    
    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []
        if self.flags is None:
            self.flags = []


class BaseEmailConnector(ABC):
    """Abstract base class for email connectors."""
    
    def __init__(self, email_address: str, password: str, config: dict = None):
        """Initialize email connector.
        
        Args:
            email_address: Email address
            password: App password or credentials
            config: Additional configuration
        """
        self.email_address = email_address
        self.password = password
        self.config = config or {}
        self.connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to email server.
        
        Returns:
            True if connection successful
        """
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from email server."""
        pass
    
    @abstractmethod
    def fetch_emails(self, folder: str = 'INBOX', limit: int = 50, unread_only: bool = False) -> List[EmailMessage]:
        """Fetch emails from specified folder.
        
        Args:
            folder: Folder name (default: INBOX)
            limit: Maximum number of emails to fetch
            unread_only: Only fetch unread emails
            
        Returns:
            List of EmailMessage objects
        """
        pass
    
    @abstractmethod
    def mark_as_read(self, email_id: str):
        """Mark email as read.
        
        Args:
            email_id: Email identifier
        """
        pass
    
    @abstractmethod
    def send_email(self, to: str, subject: str, body: str, in_reply_to: str = None):
        """Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            in_reply_to: Message-ID to reply to (optional)
        """
        pass
    
    @abstractmethod
    def move_email(self, email_id: str, destination_folder: str):
        """Move email to different folder.
        
        Args:
            email_id: Email identifier
            destination_folder: Target folder
        """
        pass
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
