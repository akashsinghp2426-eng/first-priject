"""Connectors package for Mail Agent."""

from .base_connector import BaseEmailConnector, EmailMessage
from .gmail_connector import GmailConnector
from .outlook_connector import OutlookConnector

__all__ = ['BaseEmailConnector', 'EmailMessage', 'GmailConnector', 'OutlookConnector']
