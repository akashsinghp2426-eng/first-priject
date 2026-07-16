"""
Mail Agent - Intelligent Email Assistant
Connects to Gmail/Outlook, summarizes emails, generates replies, and manages reminders.
Uses lightweight Hugging Face models for AI processing.
"""

import argparse
import schedule
import time
import signal
import sys
from datetime import datetime
from pathlib import Path

from src.agents.mail_agent import MailAgent
from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Mail Agent - Intelligent Email Assistant')
    parser.add_argument('--test', action='store_true', help='Run in test mode (process once and exit)')
    parser.add_argument('--continuous', action='store_true', help='Run continuously (check emails periodically)')
    parser.add_argument('--interval', type=int, default=15, help='Check interval in minutes (default: 15)')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Path to config file')
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Setup logging
    logger = setup_logger()
    logger.info("=" * 60)
    logger.info("Mail Agent Starting...")
    logger.info(f"Mode: {'TEST' if args.test else 'CONTINUOUS' if args.continuous else 'SINGLE RUN'}")
    logger.info("=" * 60)
    
    try:
        # Load configuration
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        
        config = ConfigLoader(config_path)
        logger.info("Configuration loaded successfully")
        
        # Initialize agent
        agent = MailAgent(config)
        logger.info("Mail Agent initialized")
        
        # Run agent
        if args.test or not args.continuous:
            # Single run or test mode
            logger.info("Running single check...")
            agent.run_once()
            logger.info("Single check completed")
        else:
            # Continuous mode
            interval = args.interval or config.get('email.check_interval', 15)
            logger.info(f"Starting continuous mode (checking every {interval} minutes)...")
            
            # Schedule periodic checks
            schedule.every(interval).minutes.do(agent.run_once)
            
            # Run initial check
            agent.run_once()
            
            # Keep running
            while True:
                schedule.run_pending()
                time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Mail Agent stopped")
        logger.info("=" * 60)


if __name__ == '__main__':
    main()
