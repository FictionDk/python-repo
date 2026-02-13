"""
Issue Management Module

Provides functionality for:
1. Clone issue snapshots to SQLite database
2. Get issue summary statistics
3. Update issue assignees and labels
4. Export issues to CSV with filters
"""

import csv
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os

from api.client import GitLabClient
from db.database import get_database
from user.manager import UserManager
from config import Config


class IssueManager:
    """Manager for GitLab issue operations"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize issue manager
        
        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config()
        self.api_client = GitLabClient(self.config)
        self.db = get_database()
        self.user_manager: Optional[UserManager] = None
    
    def _load_users(self, project_id: int):
        """Load users for the project"""
        if self.user_manager is None:
            self.user_manager = UserManager(self.config, project_id)
    
    def clone_snapshot(self, project_id: int) -> Dict[str, Any]:
        """
        获取当前时间点项目 Issue 的详细信息快照，并存入本地 SQLite 数据库
        优化流程：
        1. 从API中获取数据后直接插入或更新到issue_main
        2. 拉取get_issue_children再更新issue_main的latest_status和parent_id，同时插入或更新issue_snapshot
        
        Args:
            project_id: 项目 ID

        Returns:
            Dictionary containing:
            - issue_total: issue 总数
            - issue_main_new: issue_main 表此次新增数量
            - issue_snapshot_new: issue_snapshot 表此次新增数量
            - status_changed: 状态(status)变更的 issue 数量
        """
        # Use current date as snapshot date
        snapshot_at = datetime.now().strftime('%Y-%m-%d')
        print(f"🔄 Cloning issue snapshot for project {project_id} from {snapshot_at}...")
        
        # Step 1: Get all issues from REST API (primary data source)
        issues_data = self.api_client.get_issues(project_id, all_issues=True)
        
        issue_total = len(issues_data)
        print(f"✅ Fetched {issue_total} issues from REST API")
        
        # Create a mapping from iid to issue for easy lookup
        issues_by_iid = {issue.get('iid'): issue for issue in issues_data}
        
        # Step 2: Direct upsert into issue_main table (optimized - insert immediately after API fetch)
        # Track how many are new vs updated
        issues_before = len(self.db.get_all_issues_main(project_id))
        self.db.upsert_issues_main_batch(project_id, issues_data)
        issues_after = len(self.db.get_all_issues_main(project_id))
        issue_main_new = max(0, issues_after - issues_before)
        print(f"✅ Direct upsated {issue_total} issues to issue_main table (new: {issue_main_new})")
        
        # Step 3: Fetch GraphQL data to update parent_id, latest_status, milestone, and create snapshots
        from graphql.client import get_issue_children
        print(f"🔍 Fetching parent-child relationships and status from GraphQL...")
        
        # Prepare updates for issue_main and snapshots for issue_snapshot
        snapshots = []
        
        total_issues = len(issues_data)
        processed = 0
        
        for issue in issues_data:
            issue_id = issue.get('id')
            issue_iid = issue.get('iid')
            latest_status = ''
            
            if issue_id:
                try:
                    # Get children info from GraphQL (this also gives us the parent's main_status)
                    main_status, children = get_issue_children(issue_id)
                    latest_status = main_status
                    for child in children:
                        child_iid = child.get('iid')
                        self.db.update_issue_main_fields(
                            project_id, child_iid, 
                            {'parent_id': issue_iid}
                        )
                except Exception as e:
                    print(f"⚠️  Warning: Failed to get children for issue {issue_iid}: {e}")
                    latest_status = ''
            
            # Add snapshot for this issue
            snapshots.append({
                'project_id': project_id,
                'iid': issue_iid,
                'status': latest_status,
                'snapshot_at': snapshot_at
            })
            
            # Update this issue's latest_status in issue_main
            self.db.update_issue_main_fields(
                project_id, issue_iid,
                {'latest_status': latest_status}
            )
            
            # Display progress every 10 issues or on completion
            processed += 1
            if processed % 10 == 0 or processed == total_issues:
                print(f"   📊 Progress: {processed}/{total_issues} issues processed ({processed/total_issues:.1%})")
        
        # Step 4: Batch insert snapshots with status change detection
        snapshot_stats = self.db.batch_insert_or_update_snapshots_with_status_change(snapshots)
        print(f"✅ Processed {len(snapshots)} snapshots to issue_snapshot table:")
        print(f"   - New statuses inserted: {snapshot_stats['inserted']}")
        print(f"   - Existing statuses updated: {snapshot_stats['updated']}")
        
        # Step 5: Format response according to PLAN.md specification
        result = {
            "issue_total": issue_total,
            "issue_main_new": issue_main_new,
            "issue_snapshot_new": snapshot_stats['inserted'],
            "status_changed": snapshot_stats['inserted']
        }
        
        print(f"✅ Clone snapshot completed:")
        print(f"   - Total issues: {issue_total}")
        print(f"   - New to issue_main: {issue_main_new}")
        print(f"   - Status changes: {snapshot_stats['inserted']}")
        
        return result
    
    def get_summary(
        self,
        project_id: int,
        start_date: str,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        根据 Issue 快照库获取指定时间范围内 Issue 的统计概要数据
        使用新的双表结构 (issue_main + issue_snapshot) 进行查询
        
        If end_date not provided, defaults to one week after start_date
        
        Args:
            project_id: 项目 ID
            start_date: 开始日期 (格式: YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYY-MM-DD)
            
        Returns:
            Dictionary containing summary statistics
        """
        if end_date is None:
            # Default to one week
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = start_dt + timedelta(days=7)
            end_date = end_dt.strftime('%Y-%m-%d')
        
        print(f"� Getting issue summary for project {project_id} from {start_date} to {end_date}...")
        
        # Use new two-table structure to get summary
        summary = self.db.get_issues_summary_from_snapshots(project_id, start_date, end_date)
        
        print(f"✅ Issue summary: {summary}")
        return summary
    
    def update_issue(
        self,
        project_id: int,
        issue_iid: int,
        assignees: Optional[List[str]] = None,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        更新指定 Issue 的指派人和标签
        
        Args:
            project_id: 项目 ID
            issue_iid: Issue IID
            assignees: 指派人用户名列表
            labels: 标签列表
            
        Returns:
            Dictionary containing update result
        """
        print(f"✏️  Updating issue {issue_iid} in project {project_id}...")
        
        # Load users for validation
        self._load_users(project_id)
        
        # Validate assignees if provided
        if assignees:
            valid_assignees = []
            for username in assignees:
                user = self.user_manager.get_user_by_username(username)
                if user:
                    valid_assignees.append(username)
                else:
                    print(f"⚠️  Warning: User '{username}' not found in project members")
            
            if not valid_assignees and assignees:
                print(f"❌ Error: No valid assignees found")
                return {
                    "success": False,
                    "error": "No valid assignees found"
                }
            
            assignees = valid_assignees
        
        # Get current issue
        try:
            current_issue = self.api_client.get_issue(project_id, issue_iid)
        except Exception as e:
            print(f"❌ Error fetching issue {issue_iid}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        
        # Update assignees
        if assignees:
            self.api_client.update_issue_assignees(project_id, issue_iid, assignees)
        
        # Update labels
        if labels:
            self.api_client.update_issue(
                project_id, 
                issue_iid, 
                description=current_issue.get('description'),
                labels=labels
            )
        
        # Get updated issue
        updated_issue = self.api_client.get_issue(project_id, issue_iid)
        
        result = {
            "success": True,
            "issue": {
                "iid": updated_issue.get('iid'),
                "assignees": [a.get('username') for a in updated_issue.get('assignees', [])],
                "labels": updated_issue.get('labels', [])
            }
        }
        
        print(f"✅ Issue {issue_iid} updated successfully")
        return result
    
    
    def export_issues_to_csv(
        self,
        project_id: int,
        output_file: str,
        title_prefixes: Optional[List[str]] = None,
        status_filters: Optional[List[str]] = None,
        columns_to_export: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Export issues from issue_main table to CSV with filters
        
        Args:
            project_id: Project ID
            output_file: Path to output CSV file
            title_prefixes: List of title prefixes to filter (e.g., ['STM', 'BCM', 'IDM'])
            status_filters: List of latest_status values to include
            columns_to_export: List of column names to export (if None, export all columns)
            
        Returns:
            Dictionary containing:
            - success: True if export succeeded
            - total_issues: Total number of issues matching filters
            - output_file: Path to the exported CSV file
        """
        print(f"📤 Exporting issues to CSV for project {project_id}...")
        
        if output_file is None:
            output_file = f"exports/worklist-{datetime.now().strftime('%Y-%m-%d')}.csv"

        # Validate output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"📁 Created output directory: {output_dir}")
        
        # Query issues with filters
        issues = self.db.get_issues_with_filters(
            project_id=project_id,
            title_prefixes=title_prefixes,
            status_filters=status_filters,
            columns=columns_to_export
        )
        
        if not issues:
            print(f"⚠️  No issues found matching the filters")
            return {
                "success": True,
                "total_issues": 0,
                "output_file": output_file
            }
        
        # Determine columns to write
        if columns_to_export:
            # Filter to only columns that exist in the data
            available_columns = set(issues[0].keys())
            export_columns = [col for col in columns_to_export if col in available_columns]
        else:
            export_columns = list(issues[0].keys())
        
        print(f"📊 Found {len(issues)} issues matching filters")
        print(f"📝 Exporting {len(export_columns)} columns: {', '.join(export_columns)}")
        
        # Write to CSV
        try:
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=export_columns, extrasaction='ignore')
                
                # Write header
                writer.writeheader()
                
                # Write data rows
                for issue in issues:
                    row = {}
                    for col in export_columns:
                        value = issue.get(col, '')
                        # Convert list fields (labels, assignees) to comma-separated strings
                        if isinstance(value, list):
                            row[col] = ', '.join(str(v) for v in value)
                        else:
                            row[col] = value
                    writer.writerow(row)
            
            print(f"✅ Successfully exported {len(issues)} issues to {output_file}")
            
            return {
                "success": True,
                "total_issues": len(issues),
                "output_file": output_file
            }
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_issues": 0,
                "output_file": output_file
            }


# Convenience functions

def clone_snapshot(project_id: int) -> Dict[str, Any]:
    """
    Convenience function: Clone issue snapshot
    Args:
        project_id: Project ID
    Returns:
        Dictionary containing statistics
    """
    manager = IssueManager()
    return manager.clone_snapshot(project_id)

def get_summary(project_id: int, start_date: str, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function: Get issue summary
    Args:
        project_id: Project ID
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    Returns:
        Dictionary containing summary
    """
    manager = IssueManager()
    return manager.get_summary(project_id, start_date, end_date)

def update_issue(
    project_id: int,
    issue_iid: int,
    assignees: Optional[List[str]] = None,
    labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function: Update issue
    
    Args:
        project_id: Project ID
        issue_iid: Issue IID
        assignees: List of assignee usernames
        labels: List of labels
        
    Returns:
        Dictionary containing update result
    """
    manager = IssueManager()
    return manager.update_issue(project_id, issue_iid, assignees, labels)

def export_issues_to_csv(
    project_id: int,
    output_file: str,
    title_prefixes: Optional[List[str]] = None,
    status_filters: Optional[List[str]] = None,
    columns_to_export: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function: Export issues to CSV with filters
    
    Args:
        project_id: Project ID
        output_file: Path to output CSV file
        title_prefixes: List of title prefixes to filter (e.g., ['STM', 'BCM', 'IDM'])
        status_filters: List of latest_status values to include
        columns_to_export: List of column names to export (if None, export all columns)
        
    Returns:
        Dictionary containing export result with total_issues and output_file path
    """
    manager = IssueManager()
    return manager.export_issues_to_csv(
        project_id,
        output_file,
        title_prefixes,
        status_filters,
        columns_to_export
    )


if __name__ == "__main__":
    # Example: Clone snapshot
    # result = clone_snapshot(project_id=4)
    # print(result)

    # Example: Export issues with specific columns only
    pre_filter = ['STM','BCM','IDM','QSM','DMM','DOP','QMS','CYLIMS','D3M']
    status_filter = ["待开发","开发中","待修复","测试中","已完成"]
    table_to_export = ["iid", "title", "latest_status", "assignees", "milestone"]
    result = export_issues_to_csv(
        project_id=4,
        output_file=None,
        title_prefixes=pre_filter,
        status_filters=status_filter,
        columns_to_export=table_to_export
    )
    print(result)
