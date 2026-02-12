"""
Database models for GitLab package
"""

import sqlite3
from typing import Optional

# Import mixin classes for database operations
from .issue_main import IssueMainMixin
from .issue_snapshot import IssueSnapshotMixin
from .commits import CommitsMixin
from .users import UsersMixin

class Database(IssueMainMixin, IssueSnapshotMixin, CommitsMixin, UsersMixin):
    """Database manager for SQLite operations
    
    Inherits table-specific operations from mixin classes:
    - IssueMainMixin: issue_main table operations
    - IssueSnapshotMixin: issue_snapshot table operations
    - CommitsMixin: commits table operations
    - UsersMixin: users table operations
    """
    
    def __init__(self, db_path: str):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Connection:
        """Create database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def init_tables(self):
        """Initialize all database tables"""
        self._create_issue_main_table()
        self._create_issue_snapshot_table()
        self._create_commits_table()
        self._create_users_table()
        print("✅ Database tables initialized")
