"""
Database initialization and helper functions
"""

from typing import Optional
from .models import Database
from ..config import default_config


# Global database instance
_db_instance: Optional[Database] = None


def get_database(db_path: Optional[str] = None) -> Database:
    """
    Get or create database instance
    
    Args:
        db_path: Optional custom database path
        
    Returns:
        Database instance
    """
    global _db_instance
    
    if _db_instance is None:
        path = db_path or default_config.db_path
        _db_instance = Database(path)
        _db_instance.init_tables()
    
    return _db_instance


def init_database(db_path: Optional[str] = None) -> Database:
    """
    Initialize database with tables
    
    Args:
        db_path: Optional custom database path
        
    Returns:
        Database instance
    """
    db = Database(db_path or default_config.db_path)
    db.init_tables()
    return db


def close_database():
    """Close global database connection"""
    global _db_instance
    
    if _db_instance is not None:
        _db_instance.close()
        _db_instance = None
