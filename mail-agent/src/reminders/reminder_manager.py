"""Reminder management system for important emails."""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Reminder:
    """Represents an email reminder."""
    id: int
    email_id: str
    subject: str
    sender: str
    priority: str  # CRITICAL, IMPORTANT
    created_at: datetime
    reminded: bool = False
    notes: str = ""


class ReminderManager:
    """Manage reminders for important emails."""
    
    def __init__(self, db_path: str = 'reminders.db'):
        """Initialize reminder manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT UNIQUE NOT NULL,
                subject TEXT NOT NULL,
                sender TEXT NOT NULL,
                priority TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reminded BOOLEAN DEFAULT 0,
                notes TEXT
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON reminders(priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reminded ON reminders(reminded)')
        
        conn.commit()
        conn.close()
    
    def add_reminder(self, email_id: str, subject: str, sender: str, 
                    priority: str, notes: str = "") -> bool:
        """Add a reminder for an email.
        
        Args:
            email_id: Email identifier
            subject: Email subject
            sender: Email sender
            priority: Priority level (CRITICAL, IMPORTANT)
            notes: Additional notes
            
        Returns:
            True if added successfully
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO reminders 
                (email_id, subject, sender, priority, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email_id, subject, sender, priority.upper(), notes, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding reminder: {e}")
            return False
    
    def get_pending_reminders(self, priority: str = None) -> List[Reminder]:
        """Get all pending (not reminded) reminders.
        
        Args:
            priority: Filter by priority (optional)
            
        Returns:
            List of Reminder objects
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            if priority:
                cursor.execute('''
                    SELECT id, email_id, subject, sender, priority, created_at, reminded, notes
                    FROM reminders
                    WHERE reminded = 0 AND priority = ?
                    ORDER BY 
                        CASE priority
                            WHEN 'CRITICAL' THEN 1
                            WHEN 'IMPORTANT' THEN 2
                            ELSE 3
                        END,
                        created_at DESC
                ''', (priority.upper(),))
            else:
                cursor.execute('''
                    SELECT id, email_id, subject, sender, priority, created_at, reminded, notes
                    FROM reminders
                    WHERE reminded = 0
                    ORDER BY 
                        CASE priority
                            WHEN 'CRITICAL' THEN 1
                            WHEN 'IMPORTANT' THEN 2
                            ELSE 3
                        END,
                        created_at DESC
                ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            reminders = []
            for row in rows:
                reminder = Reminder(
                    id=row[0],
                    email_id=row[1],
                    subject=row[2],
                    sender=row[3],
                    priority=row[4],
                    created_at=datetime.fromisoformat(row[5]) if isinstance(row[5], str) else row[5],
                    reminded=bool(row[6]),
                    notes=row[7] or ""
                )
                reminders.append(reminder)
            
            return reminders
        except Exception as e:
            print(f"Error getting reminders: {e}")
            return []
    
    def mark_as_reminded(self, reminder_id: int):
        """Mark a reminder as reminded.
        
        Args:
            reminder_id: Reminder ID
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('UPDATE reminders SET reminded = 1 WHERE id = ?', (reminder_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error marking reminder: {e}")
    
    def delete_reminder(self, email_id: str):
        """Delete a reminder.
        
        Args:
            email_id: Email ID
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute('DELETE FROM reminders WHERE email_id = ?', (email_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error deleting reminder: {e}")
    
    def cleanup_old_reminders(self, days: int = 30):
        """Remove old reminders.
        
        Args:
            days: Remove reminders older than this many days
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cutoff_date = datetime.now() - timedelta(days=days)
            cursor.execute('DELETE FROM reminders WHERE created_at < ?', (cutoff_date,))
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            return deleted
        except Exception as e:
            print(f"Error cleaning up reminders: {e}")
            return 0
    
    def get_stats(self) -> Dict:
        """Get reminder statistics.
        
        Returns:
            Dictionary with stats
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM reminders')
            total = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM reminders WHERE reminded = 0')
            pending = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM reminders WHERE priority = 'CRITICAL'")
            critical = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM reminders WHERE priority = 'IMPORTANT'")
            important = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total': total,
                'pending': pending,
                'critical': critical,
                'important': important,
                'reminded': total - pending
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
