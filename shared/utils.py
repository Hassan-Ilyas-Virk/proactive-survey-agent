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
        config_path: Path to JSON config file (relative or absolute)
        
    Returns:
        Configuration dictionary
    """
    try:
        # If path is relative, try to resolve it relative to project root
        if not os.path.isabs(config_path):
            # Try multiple possible project roots
            current_file = Path(__file__).resolve()
            # shared/utils.py -> project root
            project_root = current_file.parent.parent
            
            # Try the relative path from project root
            full_path = project_root / config_path
            if not full_path.exists():
                # Try current working directory as fallback
                full_path = Path(config_path)
        else:
            full_path = Path(config_path)
        
        with open(full_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_path} (tried: {full_path if 'full_path' in locals() else config_path})")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON config: {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error loading config: {e}")
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
        
        # In serverless environments (like Vercel), use /tmp for writable storage
        # Check if we're in a serverless environment
        is_serverless = os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("FUNCTION_TARGET")
        
        if is_serverless:
            # Use /tmp in serverless environments
            base_path = "/tmp/ltm"
        
        # Resolve relative paths to absolute
        if not os.path.isabs(base_path):
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent
            base_path = str(project_root / base_path)
        
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


class LTMDatabaseStorage:
    """MongoDB-based Long-Term Memory storage"""
    
    def __init__(self, agent_name: str, config: dict):
        self.agent_name = agent_name
        self.collection_name = config.get("collection_name", "agent_memory")
        self.db_name = config.get("db_name", "agent_db")
        
        # Get URI from env var or config
        self.uri = os.getenv("MONGODB_URI")
        
        if not self.uri:
            raise ValueError("MONGODB_URI environment variable not set")
            
        try:
            import pymongo
            self.client = pymongo.MongoClient(self.uri)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            # Ensure index on agent_name and key
            self.collection.create_index([("agent_name", 1), ("key", 1)], unique=True)
        except ImportError:
            raise ImportError("pymongo not installed. Please install it to use database storage.")
        except Exception as e:
            raise Exception(f"Failed to connect to MongoDB: {e}")

    def write(self, key: str, value: Any) -> bool:
        """Write key-value pair to DB"""
        try:
            filter_query = {"agent_name": self.agent_name, "key": key}
            update_data = {
                "$set": {
                    "value": value,
                    "updated_at": get_timestamp()
                },
                "$setOnInsert": {
                    "created_at": get_timestamp()
                }
            }
            self.collection.update_one(filter_query, update_data, upsert=True)
            return True
        except Exception as e:
            print(f"DB Write Error: {e}")
            return False

    def read(self, key: str) -> Optional[Any]:
        """Read value from DB"""
        try:
            doc = self.collection.find_one({"agent_name": self.agent_name, "key": key})
            if doc:
                return doc.get("value")
            return None
        except Exception as e:
            print(f"DB Read Error: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete key from DB"""
        try:
            result = self.collection.delete_one({"agent_name": self.agent_name, "key": key})
            return result.deleted_count > 0
        except Exception as e:
            print(f"DB Delete Error: {e}")
            return False

    def list_keys(self) -> list:
        """List all keys for this agent in DB"""
        try:
            cursor = self.collection.find({"agent_name": self.agent_name}, {"key": 1})
            return [doc["key"] for doc in cursor]
        except Exception as e:
            print(f"DB List Error: {e}")
            return []


def get_ltm_storage(agent_name: str, config: dict) -> Any:
    """
    Factory function to get LTM storage backend
    
    Args:
        agent_name: Name of the agent
        config: Full agent configuration dictionary
        
    Returns:
        Storage instance (LTMFileStorage or LTMDatabaseStorage)
    """
    ltm_config = config.get("ltm_config", {})
    storage_type = ltm_config.get("storage_type", "file")
    
    if storage_type == "mongodb":
        try:
            # Pass the specific mongodb config or the whole ltm_config
            mongo_config = config.get("mongodb_config", {})
            return LTMDatabaseStorage(agent_name, mongo_config)
        except Exception as e:
            print(f"Failed to initialize MongoDB storage: {e}. Falling back to file storage.")
            # Fallback to file storage
            return LTMFileStorage(agent_name, ltm_config.get("base_directory", "shared/LTM"))
            
    # Default to file storage
    return LTMFileStorage(agent_name, ltm_config.get("base_directory", "shared/LTM"))

