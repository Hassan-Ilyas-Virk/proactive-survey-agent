"""Shared utility functions for all agents"""
import logging
import json
import os
from datetime import datetime
from typing import Any, Optional
from pathlib import Path


def setup_logging(name: str, level: str = "INFO", log_format: str = None) -> logging.Logger:
    """
    Setup logging for an agent
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Custom log format string
        
    Returns:
        Configured logger instance
    """
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format
    )
    
    logger = logging.getLogger(name)
    return logger


def load_json_config(config_path: str) -> dict:
    """
    Load JSON configuration file
    
    Args:
        config_path: Path to JSON config file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON config: {e}")
        return {}


def save_json(data: dict, file_path: str, indent: int = 2) -> bool:
    """
    Save dictionary as JSON file
    
    Args:
        data: Dictionary to save
        file_path: Path to save file
        indent: JSON indentation
        
    Returns:
        True on success, False on failure
    """
    try:
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False


def load_json(file_path: str) -> Optional[dict]:
    """
    Load JSON file
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary or None if error
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def ensure_directory(directory_path: str) -> bool:
    """
    Ensure directory exists, create if not
    
    Args:
        directory_path: Path to directory
        
    Returns:
        True if directory exists or was created
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory: {e}")
        return False


class LTMFileStorage:
    """File-based Long-Term Memory storage"""
    
    def __init__(self, agent_name: str, base_path: str = "shared/LTM"):
        self.agent_name = agent_name
        self.storage_path = os.path.join(base_path, agent_name)
        ensure_directory(self.storage_path)
    
    def write(self, key: str, value: Any) -> bool:
        """Write key-value pair to LTM"""
        try:
            data = {
                "value": value,
                "stored_at": get_timestamp()
            }
            file_path = os.path.join(self.storage_path, f"{key}.json")
            return save_json(data, file_path)
        except Exception as e:
            print(f"LTM Write Error: {e}")
            return False
    
    def read(self, key: str) -> Optional[Any]:
        """Read value from LTM"""
        try:
            file_path = os.path.join(self.storage_path, f"{key}.json")
            data = load_json(file_path)
            if data:
                return data.get("value")
            return None
        except Exception as e:
            print(f"LTM Read Error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete key from LTM"""
        try:
            file_path = os.path.join(self.storage_path, f"{key}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"LTM Delete Error: {e}")
            return False
    
    def list_keys(self) -> list:
        """List all keys in LTM"""
        try:
            if not os.path.exists(self.storage_path):
                return []
            files = os.listdir(self.storage_path)
            return [f.replace('.json', '') for f in files if f.endswith('.json')]
        except Exception as e:
            print(f"LTM List Error: {e}")
            return []

