"""
Database module for GitLab package
"""

from .models import Database
from .database import init_database, get_database

__all__ = [
    "Database",
    "init_database",
    "get_database",
]
