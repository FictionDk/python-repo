"""
Issue Main Table Mixin
Handles operations for issue_main table (latest issue state)
"""

import sqlite3
import json
from typing import Dict, Any, List, Optional


class IssueMainMixin:
    """Mixin class for issue_main table operations"""
    
    def _create_issue_main_table(self):
        """Create issue_main table for storing latest issue state"""
        self.connect().execute('''
            CREATE TABLE IF NOT EXISTS issue_main (
                project_id INTEGER NOT NULL,
                iid INTEGER NOT NULL,
                parent_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                state TEXT,
                labels TEXT,
                assignees TEXT,
                created_at TEXT,
                updated_at TEXT,
                issue_id TEXT,
                latest_status TEXT DEFAULT '',
                milestone TEXT DEFAULT '',
                PRIMARY KEY (project_id, iid)
            )
        ''')
        self.connect().commit()
    
    def upsert_issue_main(self, project_id: int, issue_data: Dict[str, Any]):
        """
        Upsert issue to issue_main table (update if exists, insert if not)
        
        Args:
            project_id: Project ID
            issue_data: Issue data from API
        """
        self.connect().execute('''
            INSERT OR REPLACE INTO issue_main (
                project_id, iid, parent_id, title, description, state, labels, 
                assignees, created_at, updated_at, issue_id, latest_status, milestone
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            issue_data.get('iid'),
            issue_data.get('parent_id', issue_data.get('iid')),
            issue_data.get('title'),
            issue_data.get('description'),
            issue_data.get('state'),
            json.dumps(issue_data.get('labels', [])),
            json.dumps([a.get('username') for a in issue_data.get('assignees', [])]),
            issue_data.get('created_at'),
            issue_data.get('updated_at'),
            issue_data.get('id'),
            issue_data.get('latest_status', ''),
            issue_data.get('milestone', '')
        ))
        self.connect().commit()
    
    def upsert_issues_main_batch(self, project_id: int, issues: List[Dict[str, Any]]):
        """
        Batch upsert issues to issue_main table
        
        Args:
            project_id: Project ID
            issues: List of issue data
        """
        conn = self.connect()
        for issue in issues:
            conn.execute('''
                INSERT OR REPLACE INTO issue_main (
                    project_id, iid, parent_id, title, description, state, labels, 
                    assignees, created_at, updated_at, issue_id, latest_status, milestone
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_id,
                issue.get('iid'),
                issue.get('parent_id', issue.get('iid')),
                issue.get('title'),
                issue.get('description'),
                issue.get('state'),
                json.dumps(issue.get('labels', [])),
                json.dumps([a.get('username') for a in issue.get('assignees', [])]),
                issue.get('created_at'),
                issue.get('updated_at'),
                issue.get('id'),
                issue.get('latest_status', ''),
                issue.get('milestone').get('title','')
            ))
        conn.commit()
    
    def get_issue_main(self, project_id: int, iid: int) -> Optional[Dict[str, Any]]:
        """
        Get latest issue state from issue_main table
        
        Args:
            project_id: Project ID
            iid: Issue IID
            
        Returns:
            Issue data or None
        """
        cursor = self.connect().execute('''
            SELECT * FROM issue_main 
            WHERE project_id = ? AND iid = ?
        ''', (project_id, iid))
        
        row = cursor.fetchone()
        if row:
            return self._row_to_issue_main(row)
        return None
    
    def get_all_issues_main(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all latest issues from issue_main table
        
        Args:
            project_id: Project ID
            
        Returns:
            List of issues
        """
        cursor = self.connect().execute('''
            SELECT * FROM issue_main 
            WHERE project_id = ?
            ORDER BY iid
        ''', (project_id,))
        
        return [self._row_to_issue_main(row) for row in cursor.fetchall()]
    
    def _row_to_issue_main(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to issue_main dictionary"""
        return {
            'project_id': row['project_id'],
            'iid': row['iid'],
            'parent_id': row['parent_id'],
            'title': row['title'],
            'description': row['description'],
            'state': row['state'],
            'labels': json.loads(row['labels']) if row['labels'] else [],
            'assignees': json.loads(row['assignees']) if row['assignees'] else [],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'issue_id': row['issue_id'],
            'latest_status': row['latest_status'],
            'milestone': row['milestone']
        }
    
    def update_issue_main_fields(self, project_id: int, iid: int, updates: Dict[str, Any]):
        """
        Update specific fields in issue_main table
        
        Args:
            project_id: Project ID
            iid: Issue IID
            updates: Dictionary of fields to update
        """
        if not updates:
            return
        
        set_clauses = []
        values = []
        
        if 'latest_status' in updates:
            set_clauses.append('latest_status = ?')
            values.append(updates['latest_status'])
        
        if 'milestone' in updates:
            set_clauses.append('milestone = ?')
            values.append(updates['milestone'])
        
        if 'parent_id' in updates:
            set_clauses.append('parent_id = ?')
            values.append(updates['parent_id'])
        
        if not set_clauses:
            return
        
        values.extend([project_id, iid])
        
        self.connect().execute(f'''
            UPDATE issue_main 
            SET {', '.join(set_clauses)}
            WHERE project_id = ? AND iid = ?
        ''', values)
        self.connect().commit()
    
    def batch_update_parent_id(self, project_id: int, parent_iid: int, child_iids: List[int]):
        """
        Batch update parent_id for multiple issues in a single database call
        
        Args:
            project_id: Project ID
            parent_iid: The parent issue iid to set
            child_iids: List of child issue iids to update
        """
        if not child_iids:
            return
        
        # Use IN clause with placeholders for batch update
        placeholders = ','.join(['?' for _ in child_iids])
        query = f'''
            UPDATE issue_main 
            SET parent_id = ? 
            WHERE project_id = ? AND iid IN ({placeholders})
        '''
        self.connect().execute(query, [parent_iid, project_id] + child_iids)
        self.connect().commit()
    
    def get_issues_with_filters(
        self,
        project_id: int,
        title_prefixes: Optional[List[str]] = None,
        status_filters: Optional[List[str]] = None,
        columns: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query issues from issue_main table with filters
        
        Args:
            project_id: Project ID
            title_prefixes: List of title prefixes to filter (e.g., ['STM', 'BCM'])
            status_filters: List of latest_status values to include
            columns: List of column names to select (if None, select all)
            
        Returns:
            List of issues matching the filters
        """
        # Build SELECT clause
        if columns:
            # Validate columns
            valid_columns = [
                'project_id', 'iid', 'parent_id', 'title', 'description',
                'state', 'labels', 'assignees', 'created_at', 'updated_at',
                'issue_id', 'latest_status', 'milestone'
            ]
            valid_columns_select = [col for col in columns if col in valid_columns]
            if not valid_columns_select:
                # If no valid columns, select all
                select_clause = '*'
            else:
                select_clause = ', '.join(valid_columns_select)
        else:
            select_clause = '*'
        
        # Build WHERE clause
        where_conditions = ['project_id = ?']
        params = [project_id]
        
        if title_prefixes:
            # Create conditions for each prefix using SUBSTR(title, 1, 3)
            prefix_conditions = []
            for prefix in title_prefixes:
                prefix_conditions.append('SUBSTR(title, 1, 3) = ?')
                params.append(prefix)
            where_conditions.append(f"({' OR '.join(prefix_conditions)})")
        
        if status_filters:
            placeholders = ','.join(['?' for _ in status_filters])
            where_conditions.append(f'latest_status IN ({placeholders})')
            params.extend(status_filters)
        
        where_clause = ' AND '.join(where_conditions)
        
        # Execute query
        query = f'SELECT {select_clause} FROM issue_main WHERE {where_clause} ORDER BY iid'
        cursor = self.connect().execute(query, params)
        rows = cursor.fetchall()
        
        # Convert rows to dictionaries
        result = []
        for row in rows:
            issue_dict = {}
            for key in row.keys():
                value = row[key]
                # Parse JSON fields
                if key in ['labels', 'assignees'] and value:
                    issue_dict[key] = json.loads(value) if isinstance(value, str) else value
                else:
                    issue_dict[key] = value
            result.append(issue_dict)
        
        return result
