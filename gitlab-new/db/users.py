"""
Users Table Mixin
Handles operations for users table (user data)
"""

import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional


class UsersMixin:
    """Mixin class for users table operations"""
    
    def _create_users_table(self):
        """Create users table"""
        self.connect().execute('''
            CREATE TABLE IF NOT EXISTS users (
                id PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                name TEXT,
                state TEXT,
                locked BOOLEAN,
                avatar_url TEXT,
                web_url TEXT,
                updated_at TEXT
            )
        ''')
        self.connect().commit()
    
    def insert_or_update_user(self, user_data: Dict[str, Any]):
        """
        Insert or update a user
        
        Args:
            user_data: User data from API
        """
        self.connect().execute('''
            INSERT OR REPLACE INTO users (
                id, username, name, state, locked, avatar_url, web_url, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data.get('id'),
            user_data.get('username'),
            user_data.get('name'),
            user_data.get('state'),
            user_data.get('locked', False),
            user_data.get('avatar_url'),
            user_data.get('web_url'),
            datetime.now().isoformat()
        ))
        self.connect().commit()
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username
        
        Args:
            username: Username
            
        Returns:
            User data or None
        """
        cursor = self.connect().execute('''
            SELECT * FROM users WHERE username = ?
        ''', (username,))
        
        row = cursor.fetchone()
        if row:
            return self._row_to_user(row)
        return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users
        
        Returns:
            List of users
        """
        cursor = self.connect().execute('SELECT * FROM users ORDER BY username')
        return [self._row_to_user(row) for row in cursor.fetchall()]
    
    def _row_to_user(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to user dictionary"""
        return {
            'id': row['id'],
            'username': row['username'],
            'name': row['name'],
            'state': row['state'],
            'locked': bool(row['locked']),
            'avatar_url': row['avatar_url'],
            'web_url': row['web_url'],
            'updated_at': row['updated_at']
        }
