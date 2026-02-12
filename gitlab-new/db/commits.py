"""
Commits Table Mixin
Handles operations for commits table (commit data)
"""

import sqlite3
from typing import Dict, Any, List


class CommitsMixin:
    """Mixin class for commits table operations"""
    
    def _create_commits_table(self):
        """Create commits table"""
        self.connect().execute('''
            CREATE TABLE IF NOT EXISTS commits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                iid TEXT,
                title TEXT NOT NULL,
                author_name TEXT NOT NULL,
                author_email TEXT,
                authored_date TEXT,
                committed_date TEXT,
                short_id TEXT,
                message TEXT,
                issue_iid INTEGER,
                snapshot_date TEXT NOT NULL,
                rate TEXT DEFAULT 'normal',
                UNIQUE(project_id, short_id, snapshot_date)
            )
        ''')
        self.connect().commit()
    
    def insert_commit(self, project_id: int, commit_data: Dict[str, Any], snapshot_date: str):
        """
        Insert a commit snapshot
        
        Args:
            project_id: Project ID
            commit_data: Commit data from API
            snapshot_date: Snapshot date
        """
        self.connect().execute('''
            INSERT OR REPLACE INTO commits (
                project_id, iid, title, author_name, author_email,
                authored_date, committed_date, short_id, message, 
                issue_iid, snapshot_date, rate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            commit_data.get('id'),
            commit_data.get('title'),
            commit_data.get('author_name'),
            commit_data.get('author_email'),
            commit_data.get('authored_date'),
            commit_data.get('committed_date'),
            commit_data.get('short_id'),
            commit_data.get('message'),
            commit_data.get('issue_iid'),
            snapshot_date,
            commit_data.get('rate', 'normal')
        ))
        self.connect().commit()
    
    def insert_commits_batch(self, project_id: int, commits: List[Dict[str, Any]], snapshot_date: str):
        """
        Batch insert commits
        
        Args:
            project_id: Project ID
            commits: List of commit data
            snapshot_date: Snapshot date
        """
        conn = self.connect()
        for commit in commits:
            conn.execute('''
                INSERT OR REPLACE INTO commits (
                    project_id, iid, title, author_name, author_email,
                    authored_date, committed_date, short_id, message, 
                    issue_iid, snapshot_date, rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_id,
                commit.get('id'),
                commit.get('title'),
                commit.get('author_name'),
                commit.get('author_email'),
                commit.get('authored_date'),
                commit.get('committed_date'),
                commit.get('short_id'),
                commit.get('message'),
                commit.get('issue_iid'),
                snapshot_date,
                commit.get('rate', 'normal')
            ))
        conn.commit()
    
    def get_commits_by_date_range(
        self, 
        project_id: int, 
        start_date: str, 
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get commits for a date range
        
        Args:
            project_id: Project ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of commits
        """
        cursor = self.connect().execute('''
            SELECT * FROM commits 
            WHERE project_id = ? AND snapshot_date >= ? AND snapshot_date <= ?
            ORDER BY committed_date DESC
        ''', (project_id, start_date, end_date))
        
        return [self._row_to_commit(row) for row in cursor.fetchall()]
    
    def get_commits_by_issue(self, project_id: int, issue_iid: int) -> List[Dict[str, Any]]:
        """
        Get commits associated with an issue
        
        Args:
            project_id: Project ID
            issue_iid: Issue IID
            
        Returns:
            List of commits
        """
        cursor = self.connect().execute('''
            SELECT * FROM commits 
            WHERE project_id = ? AND issue_iid = ?
            ORDER BY committed_date DESC
        ''', (project_id, issue_iid))
        
        return [self._row_to_commit(row) for row in cursor.fetchall()]
    
    def get_commits_summary(self, project_id: int, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get commits summary statistics
        
        Args:
            project_id: Project ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with summary statistics
        """
        commits = self.get_commits_by_date_range(project_id, start_date, end_date)
        
        summary = {
            'total': len(commits),
            'requirements': 0,
            'fixes': 0,
            'closed': 0
        }
        
        for commit in commits:
            title = commit['title'].lower()
            message = commit['message'].lower() if commit['message'] else ''
            
            if any(word in title or word in message for word in ['feature', 'feat', 'requires', '需求']):
                summary['requirements'] += 1
            elif any(word in title or word in message for word in ['fix', 'bug', '修复']):
                summary['fixes'] += 1
            elif any(word in title or word in message for word in ['close', 'closed', 'finish']):
                summary['closed'] += 1
        
        return summary
    
    def _row_to_commit(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to commit dictionary"""
        return {
            'id': row['id'],
            'project_id': row['project_id'],
            'iid': row['iid'],
            'title': row['title'],
            'author_name': row['author_name'],
            'author_email': row['author_email'],
            'authored_date': row['authored_date'],
            'committed_date': row['committed_date'],
            'short_id': row['short_id'],
            'message': row['message'],
            'issue_iid': row['issue_iid'],
            'snapshot_date': row['snapshot_date'],
            'rate': row['rate']
        }
