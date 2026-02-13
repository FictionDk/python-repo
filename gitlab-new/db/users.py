"""
Users Table Mixin
Handles operations for users table (user data)
"""

import sqlite3
from datetime import datetime
from typing import Dict, Any


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
                alias TEXT,
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
                id, username, name, state, locked, avatar_url, web_url, alias, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data.get('id'),
            user_data.get('username'),
            user_data.get('name'),
            user_data.get('state'),
            user_data.get('locked', False),
            user_data.get('avatar_url'),
            user_data.get('web_url'),
            user_data.get('alias'),
            datetime.now().isoformat()
        ))
        self.connect().commit()
    
    def update_user_alias(self, username: str, alias: str) -> bool:
        """
        Update user alias
        
        Args:
            username: Username
            alias: Alias string (can contain comma-separated multiple aliases)
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            self.connect().execute('''
                UPDATE users SET alias = ?, updated_at = ? WHERE username = ?
            ''', (alias, datetime.now().isoformat(), username))
            self.connect().commit()
            return True
        except Exception as e:
            print(f"Error updating alias for user {username}: {e}")
            return False
    
    def batch_update_aliases(self, alias_mapping: Dict[str, str]) -> int:
        """
        Batch update user aliases
        
        Args:
            alias_mapping: Dictionary mapping username to alias string
            
        Returns:
            Number of updated users
        """
        updated_count = 0
        for username, alias in alias_mapping.items():
            if self.update_user_alias(username, alias):
                updated_count += 1
        return updated_count
    
    def get_user_by_alias(self, alias: str) -> Dict[str, Any] | None:
        """
        Get user by alias (case-insensitive)
        
        The alias field in the database can contain multiple comma-separated aliases.
        This method will search for a match across all aliases for each user.
        
        Args:
            alias: Alias to search for (case-insensitive)
            
        Returns:
            User dictionary if found, None otherwise
            
        Example:
            If a user has alias "Pan ZhiHao,panzhihao":
            - get_user_by_alias("Pan ZhiHao") returns the user
            - get_user_by_alias("panzhihao") returns the same user
        """
        # Normalize the search alias (strip whitespace)
        search_alias = alias.strip()
        
        # Query all users from database
        cursor = self.connect().execute('SELECT * FROM users WHERE alias IS NOT NULL')
        rows = cursor.fetchall()
        
        # Search through each user's aliases
        for row in rows:
            user_alias = row['alias']
            if not user_alias:
                continue
            
            # Split by comma and compare each alias case-insensitively
            user_aliases = [a.strip() for a in user_alias.split(',')]
            for user_alias_item in user_aliases:
                if user_alias_item.lower() == search_alias.lower():
                    return self._row_to_user(row)
        
        # No match found
        return None
    
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
            'alias': row['alias'],
            'updated_at': row['updated_at']
        }
