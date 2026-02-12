"""
Issue Snapshot Table Mixin
Handles operations for issue_snapshot table (historical status tracking)
"""

import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional


class IssueSnapshotMixin:
    """Mixin class for issue_snapshot table operations"""
    
    def _create_issue_snapshot_table(self):
        """Create issue_snapshot table for storing historical issue status"""
        self.connect().execute('''
            CREATE TABLE IF NOT EXISTS issue_snapshot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                iid INTEGER NOT NULL,
                status TEXT,
                create_at TEXT NOT NULL,
                snapshot_at TEXT NOT NULL,
                UNIQUE(project_id, iid, status)
            )
        ''')
        self.connect().commit()
    
    def insert_issue_snapshot(
        self, 
        project_id: int, 
        iid: int, 
        status: str, 
        snapshot_date: str
    ):
        """
        Insert issue status snapshot
        
        Args:
            project_id: Project ID
            iid: Issue IID
            status: Main status from GraphQL API
            snapshot_date: Snapshot date (YYYY-MM-DD)
        """
        try:
            create_at = datetime.now().isoformat()
            self.connect().execute('''
                INSERT OR REPLACE INTO issue_snapshot (
                    project_id, iid, status, create_at, snapshot_at
                ) VALUES (?, ?, ?, ?, ?)
            ''', (project_id, iid, status, create_at, snapshot_date))
            self.connect().commit()
        except sqlite3.IntegrityError:
            pass
    
    def insert_issue_snapshots_batch(
        self, 
        snapshots: List[Dict[str, Any]]
    ):
        """
        Batch insert issue snapshots
        
        Args:
            snapshots: List of snapshot dictionaries with keys:
                      project_id, iid, status, snapshot_at
        """
        conn = self.connect()
        for snapshot in snapshots:
            try:
                create_at = datetime.now().isoformat()
                conn.execute('''
                    INSERT OR REPLACE INTO issue_snapshot (
                        project_id, iid, status, create_at, snapshot_at
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    snapshot.get('project_id'),
                    snapshot.get('iid'),
                    snapshot.get('status'),
                    create_at,
                    snapshot.get('snapshot_at')
                ))
            except sqlite3.IntegrityError:
                pass
        conn.commit()
    
    def get_issue_snapshots(
        self, 
        project_id: int, 
        start_date: str, 
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get issue snapshots for a date range
        
        Args:
            project_id: Project ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of snapshot records
        """
        cursor = self.connect().execute('''
            SELECT * FROM issue_snapshot 
            WHERE project_id = ? AND snapshot_at >= ? AND snapshot_at <= ?
            ORDER BY iid, snapshot_at
        ''', (project_id, start_date, end_date))
        
        return [self._row_to_issue_snapshot(row) for row in cursor.fetchall()]
    
    def get_issue_snapshots_by_iid(
        self,
        project_id: int,
        iid: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get snapshots for a specific issue
        
        Args:
            project_id: Project ID
            iid: Issue IID
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of snapshot records
        """
        if start_date and end_date:
            cursor = self.connect().execute('''
                SELECT * FROM issue_snapshot 
                WHERE project_id = ? AND iid = ? AND snapshot_at >= ? AND snapshot_at <= ?
                ORDER BY snapshot_at
            ''', (project_id, iid, start_date, end_date))
        else:
            cursor = self.connect().execute('''
                SELECT * FROM issue_snapshot 
                WHERE project_id = ? AND iid = ?
                ORDER BY snapshot_at
            ''', (project_id, iid))
        
        return [self._row_to_issue_snapshot(row) for row in cursor.fetchall()]
    
    def _row_to_issue_snapshot(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to issue_snapshot dictionary"""
        return {
            'id': row['id'],
            'project_id': row['project_id'],
            'iid': row['iid'],
            'status': row['status'],
            'create_at': row['create_at'],
            'snapshot_at': row['snapshot_at']
        }
    
    def insert_or_update_snapshot_with_status_change(
        self,
        project_id: int,
        iid: int,
        status: str,
        snapshot_at: str
    ) -> Dict[str, int]:
        """
        Insert or update snapshot with status change detection.
        Only inserts to issue_snapshot if status has changed.
        Updates snapshot_at for existing status entries.
        
        Args:
            project_id: Project ID
            iid: Issue IID
            status: Main status from GraphQL API
            snapshot_at: Snapshot date (YYYY-MM-DD)
            
        Returns:
            Dictionary with statistics:
            - inserted: Number of new snapshots inserted (status changed)
            - updated: Number of existing snapshots updated (status unchanged)
        """
        create_at = datetime.now().isoformat()
        inserted = 0
        updated = 0
        
        cursor = self.connect().execute(
            'SELECT id, snapshot_at FROM issue_snapshot WHERE project_id = ? AND iid = ? AND status = ?',
            (project_id, iid, status)
        )
        existing = cursor.fetchone()
        
        if existing:
            self.connect().execute(
                'UPDATE issue_snapshot SET snapshot_at = ? WHERE id = ?',
                (snapshot_at, existing['id'])
            )
            updated = 1
        else:
            try:
                self.connect().execute(
                    'INSERT INTO issue_snapshot (project_id, iid, status, create_at, snapshot_at) VALUES (?, ?, ?, ?, ?)',
                    (project_id, iid, status, create_at, snapshot_at)
                )
                inserted = 1
            except sqlite3.IntegrityError:
                pass
        
        self.connect().commit()
        return {'inserted': inserted, 'updated': updated}
    
    def batch_insert_or_update_snapshots_with_status_change(
        self,
        snapshots: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Batch insert or update snapshots with status change detection.
        
        Args:
            snapshots: List of snapshot dictionaries with keys:
                      project_id, iid, status, snapshot_at
            
        Returns:
            Dictionary with statistics:
            - inserted: Number of new snapshots inserted (status changed)
            - updated: Number of existing snapshots updated (status unchanged)
        """
        total_inserted = 0
        total_updated = 0
        
        for snapshot in snapshots:
            result = self.insert_or_update_snapshot_with_status_change(
                snapshot.get('project_id'),
                snapshot.get('iid'),
                snapshot.get('status'),
                snapshot.get('snapshot_at')
            )
            total_inserted += result['inserted']
            total_updated += result['updated']
        
        return {'inserted': total_inserted, 'updated': total_updated}
    
    def get_issues_summary_from_snapshots(
        self, 
        project_id: int, 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """
        Get issues summary statistics using the new two-table structure
        Combines data from issue_snapshot (historical status) and issue_main (latest data)
        
        Args:
            project_id: Project ID
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with summary statistics
        """
        snapshots = self.get_issue_snapshots(project_id, start_date, end_date)
        
        issue_status_map = {}
        for snapshot in snapshots:
            iid = snapshot['iid']
            status = snapshot['status']
            snapshot_at = snapshot['snapshot_at']
            
            if iid not in issue_status_map or snapshot_at > issue_status_map[iid]['snapshot_at']:
                issue_status_map[iid] = {
                    'status': status,
                    'snapshot_at': snapshot_at
                }
        
        all_issues = self.get_all_issues_main(project_id)
        issue_labels_map = {issue['iid']: issue['labels'] for issue in all_issues}
        
        unique_iids = set(issue_status_map.keys()).union(issue_labels_map.keys())
        
        summary = {
            'total': len(unique_iids),
            'left_pending': 0,
            'to_development': 0,
            'to_testing': 0,
            'to_completed': 0,
            'to_bug': 0,
            'to_fixed': 0
        }
        
        for iid in unique_iids:
            status = issue_status_map.get(iid, {}).get('status', '')
            labels = issue_labels_map.get(iid, [])
            
            if status:
                status_lower = status.lower()
                if 'pending' in status_lower or '待' in status:
                    summary['left_pending'] += 1
                elif 'development' in status_lower or '开发' in status:
                    summary['to_development'] += 1
                elif 'testing' in status_lower or '测试' in status:
                    summary['to_testing'] += 1
                elif 'completed' in status_lower or '完成' in status_lower or 'done' in status_lower:
                    summary['to_completed'] += 1
                elif 'bug' in status_lower:
                    summary['to_bug'] += 1
                elif 'fixed' in status_lower or 'fix' in status_lower:
                    summary['to_fixed'] += 1
                else:
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
            else:
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
