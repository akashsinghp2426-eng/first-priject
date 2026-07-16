"""Configuration loader for Mail Agent."""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv


class ConfigLoader:
    """Load and manage configuration from YAML and environment variables."""
    
    def __init__(self, config_path: str):
        """Initialize config loader.
        
        Args:
            config_path: Path to YAML configuration file
        """
        # Load environment variables
        load_dotenv()
        
        # Load YAML config
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Override with environment variables
        self._load_env_overrides()
    
    def _load_env_overrides(self):
        """Override config with environment variables."""
        # Email settings
        if os.getenv('EMAIL_ADDRESS'):
            self.config['email']['address'] = os.getenv('EMAIL_ADDRESS')
        if os.getenv('EMAIL_PASSWORD'):
            self.config['email']['password'] = os.getenv('EMAIL_PASSWORD')
        
        # Hugging Face token
        if os.getenv('HF_API_TOKEN'):
            if 'llm' not in self.config:
                self.config['llm'] = {}
            self.config['llm']['api_token'] = os.getenv('HF_API_TOKEN')
        
        # Log level
        if os.getenv('LOG_LEVEL'):
            self.config['logging']['level'] = os.getenv('LOG_LEVEL')
    
    def get(self, key: str, default=None):
        """Get configuration value by dot-notation key.
        
        Args:
            key: Dot-notation key (e.g., 'email.provider')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_email_config(self) -> dict:
        """Get email configuration."""
        return self.config.get('email', {})
    
    def get_llm_config(self) -> dict:
        """Get LLM configuration."""
        return self.config.get('llm', {})
    
    def get_reminder_config(self) -> dict:
        """Get reminder configuration."""
        return self.config.get('reminders', {})
    
    def get_logging_config(self) -> dict:
        """Get logging configuration."""
        return self.config.get('logging', {})
