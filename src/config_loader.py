"""
Config Loader - Load and validate configuration.

This module handles configuration loading from JSON files with validation.
Follows singleton pattern for global config access.
"""

# Standard library imports
import json
import logging
from pathlib import Path
from typing import Any, Dict

# Configure logging
logger = logging.getLogger(__name__)


class Config:
    """Configuration manager"""
    
    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = config_path
        self.data = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Returns:
            Dict[str, Any]: Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If JSON is invalid
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config_data
            
        except FileNotFoundError as e:
            logger.error(f"Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}") from e
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise ValueError(f"Invalid JSON in config file: {e}") from e
    
    def _validate_config(self) -> None:
        """
        Validate required configuration fields and create necessary directories.
        
        Raises:
            ValueError: If required field is missing
        """
        required_fields = [
            'CHANNEL_URL',
            'MAX_WINDOWS',
            'COOKIE_DB_PATH',
            'SEEN_DB_PATH',
            'LOG_PATH'
        ]
        
        missing_fields = [field for field in required_fields if field not in self.data]
        if missing_fields:
            error_msg = f"Missing required config fields: {', '.join(missing_fields)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Create directories if they don't exist
        for path_field in ['COOKIE_DB_PATH', 'SEEN_DB_PATH', 'LOG_PATH']:
            path = Path(self.data[path_field])
            path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {path.parent}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with support for nested keys.
        
        Args:
            key: Configuration key (supports dot notation: 'RATE_LIMITING.MAX_VIDEOS')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Examples:
            >>> config.get('MAX_WINDOWS')
            4
            >>> config.get('RATE_LIMITING.MAX_VIDEOS_PER_DAY')
            100
        """
        keys = key.split('.')
        value = self.data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
                
        return value
    
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access"""
        return self.get(key)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists"""
        return self.get(key) is not None


def load_config(config_path: str = "config/config.json") -> Config:
    """Load configuration from file"""
    return Config(config_path)
