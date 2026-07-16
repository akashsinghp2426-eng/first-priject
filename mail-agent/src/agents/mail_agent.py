"""Main Mail Agent orchestrator."""

import sys
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.connectors import GmailConnector, OutlookConnector, EmailMessage
from src.summarizers import HuggingFaceSummarizer
from src.repliers import HuggingFaceReplier
from src.reminders import ReminderManager
from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logger


class MailAgent:
    """Main orchestrator for the Mail Agent system."""
    
    def __init__(self, config: ConfigLoader):
        """Initialize Mail Agent.
        
        Args:
            config: Configuration loader instance
        """
        self.config = config
        self.logger = setup_logger('MailAgent', config.get_logging_config())
        
        # Initialize components
        self.connector = None
        self.summarizer = None
        self.replier = None
        self.reminder_manager = None
        
        # Priority thresholds
        self.critical_threshold = config.get('reminders.critical_threshold', 0.8)
        self.important_threshold = config.get('reminders.important_threshold', 0.6)
    
    def _initialize_components(self):
        """Initialize all agent components."""
        email_config = self.config.get_email_config()
        llm_config = self.config.get_llm_config()
        reminder_config = self.config.get_reminder_config()
        
        # Initialize email connector
        provider = email_config.get('provider', 'gmail').lower()
        email_address = email_config.get('address') or email_config.get('email_address')
        password = email_config.get('password') or email_config.get('email_password')
        
        if not email_address or not password:
            raise ValueError("Email credentials not found. Please set EMAIL_ADDRESS and EMAIL_PASSWORD in .env file")
        
        self.logger.info(f"Initializing {provider} connector...")
        if provider == 'gmail':
            self.connector = GmailConnector(email_address, password, email_config)
        elif provider == 'outlook':
            self.connector = OutlookConnector(email_address, password, email_config)
        else:
            raise ValueError(f"Unsupported email provider: {provider}")
        
        # Connect to email server
        if not self.connector.connect():
            raise ConnectionError(f"Failed to connect to {provider} server")
        self.logger.info(f"Connected to {provider}")
        
        # Initialize summarizer
        model_name = llm_config.get('model_name', 'google/flan-t5-base')
        self.logger.info(f"Initializing summarizer with model: {model_name}")
        self.summarizer = HuggingFaceSummarizer(model_name=model_name)
        
        # Initialize replier
        self.logger.info("Initializing reply generator...")
        self.replier = HuggingFaceReplier(model_name=model_name)
        
        # Initialize reminder manager
        if reminder_config.get('enabled', True):
            db_path = reminder_config.get('db_path', 'reminders.db')
            self.logger.info(f"Initializing reminder manager (DB: {db_path})")
            self.reminder_manager = ReminderManager(db_path)
        
        self.logger.info("All components initialized successfully")
    
    def run_once(self):
        """Run a single email processing cycle."""
        try:
            # Initialize components if not already done
            if self.connector is None:
                self._initialize_components()
            
            email_config = self.config.get_email_config()
            max_emails = email_config.get('max_emails_per_check', 50)
            folder = email_config.get('inbox_folder', 'INBOX')
            mark_read = email_config.get('mark_as_read', True)
            
            self.logger.info(f"Fetching emails from {folder}...")
            emails = self.connector.fetch_emails(folder=folder, limit=max_emails, unread_only=True)
            
            if not emails:
                self.logger.info("No new emails found")
                return
            
            self.logger.info(f"Found {len(emails)} new email(s)")
            
            # Process each email
            processed_count = 0
            reminder_count = 0
            
            for email in emails:
                self.logger.info(f"\nProcessing email: {email.subject[:50]}...")
                
                # Generate summary
                summary = self.summarizer.summarize(email.body)
                self.logger.info(f"Summary: {summary[:100]}...")
                
                # Determine priority and create reminder if needed
                priority = self._classify_priority(email, summary)
                
                if priority in ['CRITICAL', 'IMPORTANT'] and self.reminder_manager:
                    self.reminder_manager.add_reminder(
                        email_id=email.id,
                        subject=email.subject,
                        sender=email.sender,
                        priority=priority,
                        notes=summary
                    )
                    reminder_count += 1
                    self.logger.info(f"✓ Created {priority} reminder")
                
                # Mark as read if configured
                if mark_read and not email.is_read:
                    self.connector.mark_as_read(email.id)
                
                processed_count += 1
            
            # Show pending reminders
            if self.reminder_manager:
                pending = self.reminder_manager.get_pending_reminders()
                if pending:
                    self.logger.info(f"\n📌 You have {len(pending)} pending reminder(s):")
                    for r in pending[:5]:  # Show top 5
                        self.logger.info(f"  [{r.priority}] {r.subject[:40]} - From: {r.sender}")
            
            self.logger.info(f"\n✅ Processing complete: {processed_count} emails processed, {reminder_count} reminders created")
            
        except Exception as e:
            self.logger.error(f"Error in processing cycle: {e}", exc_info=True)
            raise
    
    def _classify_priority(self, email: EmailMessage, summary: str) -> str:
        """Classify email priority based on content.
        
        Args:
            email: Email message object
            summary: Generated summary
            
        Returns:
            Priority level: CRITICAL, IMPORTANT, NORMAL, LOW
        """
        subject_lower = email.subject.lower()
        body_lower = email.body.lower()
        summary_lower = summary.lower()
        
        # Critical keywords
        critical_keywords = ['urgent', 'emergency', 'asap', 'immediately', 'critical', 
                           'deadline today', 'action required now', 'server down']
        
        # Important keywords  
        important_keywords = ['meeting', 'deadline', 'review', 'approval', 'important',
                            'action required', 'please respond', 'reply', 'tomorrow',
                            'this week', 'schedule', 'appointment']
        
        # Low priority keywords
        low_keywords = ['newsletter', 'promotion', 'unsubscribe', 'marketing',
                       'sale', 'offer', 'bulk', 'automated']
        
        # Check for critical
        for keyword in critical_keywords:
            if keyword in subject_lower or keyword in body_lower[:200]:
                return 'CRITICAL'
        
        # Check for important
        for keyword in important_keywords:
            if keyword in subject_lower or keyword in body_lower[:300]:
                return 'IMPORTANT'
        
        # Check for low priority
        for keyword in low_keywords:
            if keyword in subject_lower or keyword in body_lower[:200]:
                return 'LOW'
        
        # Default to normal
        return 'NORMAL'
    
    def generate_reply(self, email: EmailMessage, style: str = 'professional') -> str:
        """Generate a reply for an email.
        
        Args:
            email: Email to reply to
            style: Reply style
            
        Returns:
            Generated reply text
        """
        if self.replier is None:
            self._initialize_components()
        
        return self.replier.generate_reply(
            email_subject=email.subject,
            email_body=email.body,
            style=style
        )
    
    def send_reply(self, email: EmailMessage, reply_text: str = None, style: str = 'professional'):
        """Send a reply to an email.
        
        Args:
            email: Email to reply to
            reply_text: Custom reply text (optional, will generate if not provided)
            style: Reply style for auto-generation
        """
        if reply_text is None:
            reply_text = self.generate_reply(email, style)
        
        subject = f"Re: {email.subject}"
        self.connector.send_email(
            to=email.sender.split('<')[-1].strip('> '),
            subject=subject,
            body=reply_text,
            in_reply_to=email.id
        )
        self.logger.info(f"Reply sent to {email.sender}")
    
    def cleanup(self):
        """Cleanup resources."""
        if self.connector:
            self.connector.disconnect()
        if self.reminder_manager:
            # Cleanup old reminders
            deleted = self.reminder_manager.cleanup_old_reminders(days=30)
            if deleted > 0:
                self.logger.info(f"Cleaned up {deleted} old reminders")
    
    def __del__(self):
        """Destructor - cleanup on deletion."""
        try:
            self.cleanup()
        except:
            pass
