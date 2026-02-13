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
                project_name TEXT,
                group_name TEXT,
                title TEXT NOT NULL,
                author_name TEXT NOT NULL,
                authored_date TEXT,
                committed_date TEXT,
                message TEXT,
                operation TEXT DEFAULT '',
                issue_iid TEXT,
                rate_message TEXT DEFAULT 'normal',
                rate_count INTEGER DEFAULT 0,
                issue_synced INTEGER DEFAULT 0
            )
        ''')
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
                    id, short_id, project_id, project_name, group_name,
                    title, author_name,
                    authored_date, committed_date, message, issue_iid,
                    rate_message, rate_count, operation, issue_synced
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                commit.get('id'),
                commit.get('short_id'),
                project_id,
                commit.get('project_name'),
                commit.get('group_name'),
                commit.get('title'),
                commit.get('author_name'),
                commit.get('authored_date'),
                commit.get('committed_date'),
                commit.get('message'),
                commit.get('issue_iid'),
                commit.get('rate_message', 'normal'),
                commit.get('rate_count', 0),
                commit.get('operation', ''),
                commit.get('issue_synced', 0)
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
            'project_name': row['project_name'],
            'group_name': row['group_name'],
            'title': row['title'],
            'author_name': row['author_name'],
            'authored_date': row['authored_date'],
            'committed_date': row['committed_date'],
            'message': row['message'],
            'issue_iid': row['issue_iid'],
            'rate_message': row['rate_message'],
            'rate_count': row['rate_count'],
            'operation': row.get('operation', ''),
            'issue_synced': row.get('issue_synced', 0)
        }
    
    def get_commits_summary(
        self,
        project_id_arr: List[int],
        start_date: str,
        end_date: str
    ) -> List[sqlite3.Row]:
        """
        Get commits summary by issue within specified project list and date range
        
        Args:
            project_id_arr: List of project IDs
            start_date: Start date in format YYYY-MM-DD
            end_date: End date in format YYYY-MM-DD
            
        Returns:
            List of database rows containing commit information
        """
        if not project_id_arr:
            return []
        
        # Convert dates to ISO format with time suffix for comparison
        start_datetime = f"{start_date}T00:00:00+08:00"
        end_datetime = f"{end_date}T23:59:59+08:00"
        
        # Build query for projects
        placeholders = ','.join('?' * len(project_id_arr))
        
        query = f'''
            SELECT 
                id, short_id, project_id, project_name, group_name,
                title, author_name, authored_date, committed_date,
                message, issue_iid, operation
            FROM commits
            WHERE project_id IN ({placeholders})
                AND committed_date >= ?
                AND committed_date <= ?
            ORDER BY committed_date
        '''
        
        params = project_id_arr + [start_datetime, end_datetime]
        cursor = self.connect().execute(query, params)
        
        return cursor.fetchall()
    
    def mark_issue_synced(self, commit_ids: List[str]) -> int:
        """
        Mark commits as having their issue synchronization completed
        
        Args:
            commit_ids: List of commit IDs to mark as synced
            
        Returns:
            Number of commits marked as synced
        """
        if not commit_ids:
            return 0
        
        placeholders = ','.join('?' * len(commit_ids))
        query = f'''
            UPDATE commits
            SET issue_synced = 1
            WHERE id IN ({placeholders})
        '''
        
        cursor = self.connect().execute(query, commit_ids)
        self.connect().commit()
        
        return cursor.rowcount
    
    def get_commits_needing_sync(
        self,
        project_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[sqlite3.Row]:
        """
        Get commits that still need issue synchronization
        
        A commit needs sync if:
        - issue_synced = 0 (not yet synced)
        - issue_iid is not NULL and not empty (has associated issues)
        
        Args:
            project_id: Optional project ID to filter by
            start_date: Optional start date in format YYYY-MM-DD
            end_date: Optional end date in format YYYY-MM-DD
            
        Returns:
            List of database rows containing commit information
        """
        query = '''
            SELECT 
                id, short_id, project_id, project_name, group_name,
                title, author_name, authored_date, committed_date,
                message, issue_iid, operation
            FROM commits
            WHERE issue_synced = 0
                AND issue_iid IS NOT NULL
                AND issue_iid != ''
        '''
        
        params = []
        
        if project_id is not None:
            query += ' AND project_id = ?'
            params.append(project_id)
        
        if start_date and end_date:
            start_datetime = f"{start_date}T00:00:00+08:00"
            end_datetime = f"{end_date}T23:59:59+08:00"
            query += ' AND committed_date >= ? AND committed_date <= ?'
            params.extend([start_datetime, end_datetime])
        
        query += ' ORDER BY committed_date DESC'
        
        cursor = self.connect().execute(query, params)
        return cursor.fetchall()
