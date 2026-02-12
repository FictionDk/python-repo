"""
Commits Table Mixin
Handles operations for commits table (commit data)
"""

import sqlite3
from typing import Dict, Any, List, Optional


class CommitsMixin:
    """Mixin class for commits table operations"""
    
    def _create_commits_table(self):
        """Create commits table according to PLAN.md specification"""
        self.connect().execute('''
            CREATE TABLE IF NOT EXISTS commits (
                id TEXT PRIMARY KEY,
                short_id TEXT,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                author_name TEXT NOT NULL,
                authored_date TEXT,
                committed_date TEXT,
                message TEXT,
                issue_iid INTEGER,
                rate_message TEXT DEFAULT 'normal',
                rate_count INTEGER DEFAULT 0,
                operation TEXT DEFAULT '{}'
            )
        ''')
        self.connect().commit()
    
    def insert_commit(self, project_id: int, commit_data: Dict[str, Any]):
        """
        Insert a commit
        
        Args:
            project_id: Project ID
            commit_data: Commit data from API
        """
        self.connect().execute('''
            INSERT OR REPLACE INTO commits (
                id, short_id, project_id, title, author_name,
                authored_date, committed_date, message, issue_iid,
                rate_message, rate_count, operation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            commit_data.get('id'),
            commit_data.get('short_id'),
            project_id,
            commit_data.get('title'),
            commit_data.get('author_name'),
            commit_data.get('authored_date'),
            commit_data.get('committed_date'),
            commit_data.get('message'),
            commit_data.get('issue_iid'),
            commit_data.get('rate_message', 'normal'),
            commit_data.get('rate_count', 0),
            commit_data.get('operation', '{}')
        ))
        self.connect().commit()
    
    def insert_commits_batch(self, project_id: int, commits: List[Dict[str, Any]]):
        """
        Batch insert commits
        
        Args:
            project_id: Project ID
            commits: List of commit data
        """
        conn = self.connect()
        for commit in commits:
            conn.execute('''
                INSERT OR REPLACE INTO commits (
                    id, short_id, project_id, title, author_name,
                    authored_date, committed_date, message, issue_iid,
                    rate_message, rate_count, operation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                commit.get('id'),
                commit.get('short_id'),
                project_id,
                commit.get('title'),
                commit.get('author_name'),
                commit.get('authored_date'),
                commit.get('committed_date'),
                commit.get('message'),
                commit.get('issue_iid'),
                commit.get('rate_message', 'normal'),
                commit.get('rate_count', 0),
                commit.get('operation', '{}')
            ))
        conn.commit()
    
    def get_last_commit_date(self, project_id: int) -> Optional[str]:
        """
        Get the last committed_date for a project
        
        Args:
            project_id: Project ID
            
        Returns:
            The most recent committed_date in ISO format, or None if no commits exist
        """
        cursor = self.connect().execute('''
            SELECT committed_date FROM commits 
            WHERE project_id = ?
            ORDER BY committed_date DESC
            LIMIT 1
        ''', (project_id,))
        
        row = cursor.fetchone()
        if row:
            return row['committed_date']
        return None
    
    def _row_to_commit(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to commit dictionary"""
        return {
            'id': row['id'],
            'short_id': row['short_id'],
            'project_id': row['project_id'],
            'title': row['title'],
            'author_name': row['author_name'],
            'authored_date': row['authored_date'],
            'committed_date': row['committed_date'],
            'message': row['message'],
            'issue_iid': row['issue_iid'],
            'rate_message': row['rate_message'],
            'rate_count': row['rate_count'],
            'operation': row.get('operation', '{}')
        }
