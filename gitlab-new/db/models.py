"""
Database models for GitLab package
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


class Database:
    """Database manager for SQLite operations"""
    
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
        self._create_issues_table()
        self._create_commits_table()
        self._create_users_table()
        print("✅ Database tables initialized")
    
    def _create_issues_table(self):
        """Create issues table"""
        self.connect().execute('''
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                iid INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                state TEXT,
                labels TEXT,
                assignees TEXT,
                created_at TEXT,
                updated_at TEXT,
                snapshot_date TEXT NOT NULL,
                UNIQUE(project_id, iid, snapshot_date)
            )
        ''')
        self.connect().commit()
    
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
    
    def _create_users_table(self):
        """Create users table"""
        self.connect().execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
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
    
    # ================== Issues Operations ==================
    
    def insert_issue(self, project_id: int, issue_data: Dict[str, Any], snapshot_date: str):
        """
        Insert an issue snapshot
        
        Args:
            project_id: Project ID
            issue_data: Issue data from API
            snapshot_date: Snapshot date (YYYY-MM-DD)
        """
        self.connect().execute('''
            INSERT OR REPLACE INTO issues (
                project_id, iid, title, description, state, labels, 
                assignees, created_at, updated_at, snapshot_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id,
            issue_data.get('iid'),
            issue_data.get('title'),
            issue_data.get('description'),
            issue_data.get('state'),
            json.dumps(issue_data.get('labels', [])),
            json.dumps([a.get('username') for a in issue_data.get('assignees', [])]),
            issue_data.get('created_at'),
            issue_data.get('updated_at'),
            snapshot_date
        ))
        self.connect().commit()
    
    def insert_issues_batch(self, project_id: int, issues: List[Dict[str, Any]], snapshot_date: str):
        """
        Batch insert issues
        
        Args:
            project_id: Project ID
            issues: List of issue data
            snapshot_date: Snapshot date
        """
        conn = self.connect()
        for issue in issues:
            conn.execute('''
                INSERT OR REPLACE INTO issues (
                    project_id, iid, title, description, state, labels, 
                    assignees, created_at, updated_at, snapshot_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_id,
                issue.get('iid'),
                issue.get('title'),
                issue.get('description'),
                issue.get('state'),
                json.dumps(issue.get('labels', [])),
                json.dumps([a.get('username') for a in issue.get('assignees', [])]),
                issue.get('created_at'),
                issue.get('updated_at'),
                snapshot_date
            ))
        conn.commit()
    
    def get_issues_by_date_range(
        self, 
        project_id: int, 
        start_date: str, 
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get issues snapshot for a specific date range
        
        Args:
            project_id: Project ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of issues
        """
        cursor = self.connect().execute('''
            SELECT * FROM issues 
            WHERE project_id = ? AND snapshot_date >= ? AND snapshot_date <= ?
            ORDER BY iid
        ''', (project_id, start_date, end_date))
        
        return [self._row_to_issue(row) for row in cursor.fetchall()]
    
    def get_issues_summary(self, project_id: int, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get issues summary statistics
        
        Args:
            project_id: Project ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with summary statistics
        """
        cursor = self.connect().execute('''
            SELECT * FROM issues 
            WHERE project_id = ? AND snapshot_date >= ? AND snapshot_date <= ?
            ORDER BY iid
        ''', (project_id, start_date, end_date))
        
        issues = [self._row_to_issue(row) for row in cursor.fetchall()]
        
        # TODO: Define label mapping logic
        # For now, return basic counts based on state
        summary = {
            'total': len(issues),
            'left_pending': 0,
            'to_development': 0,
            'to_testing': 0,
            'to_completed': 0,
            'to_bug': 0,
            'to_fixed': 0
        }
        
        for issue in issues:
            labels = issue['labels']
            state = issue['state']
            
            # Simple mapping based on labels - needs refinement
            if '待处理' in labels or 'pending' in [l.lower() for l in labels]:
                summary['left_pending'] += 1
            elif '开发中' in labels or 'development' in [l.lower() for l in labels]:
                summary['to_development'] += 1
            elif '测试中' in labels or 'testing' in [l.lower() for l in labels]:
                summary['to_testing'] += 1
            elif '已完成' in labels or 'completed' in [l.lower() for l in labels]:
                summary['to_completed'] += 1
            elif 'bug' in [l.lower() for l in labels]:
                summary['to_bug'] += 1
            elif 'fixed' in [l.lower() for l in labels]:
                summary['to_fixed'] += 1
        
        return summary
    
    def _row_to_issue(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to issue dictionary"""
        return {
            'id': row['id'],
            'project_id': row['project_id'],
            'iid': row['iid'],
            'title': row['title'],
            'description': row['description'],
            'state': row['state'],
            'labels': json.loads(row['labels']) if row['labels'] else [],
            'assignees': json.loads(row['assignees']) if row['assignees'] else [],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'snapshot_date': row['snapshot_date']
        }
    
    # ================== Commits Operations ==================
    
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
            
            # Categorize commits based on title/message
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
    
    # ================== Users Operations ==================
    
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
