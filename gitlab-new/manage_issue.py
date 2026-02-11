"""
Issue Management Module

Provides functionality for:
1. Clone issue snapshots to SQLite database
2. Get issue summary statistics
3. Update issue assignees and labels
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

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
        分别更新或插入 issue_main、issue_snapshot
        状态变更才插入 issue_snapshot，否则只是更新 snapshot_at
        
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
        
        # Step 2: Enhance issues with parent_id from GraphQL API
        from graphql.client import get_issue_children
        print(f"🔍 Fetching parent-child relationships from GraphQL...")
        
        total_issues = len(issues_data)
        processed = 0
        
        for issue in issues_data:
            issue_id = issue.get('id')
            if issue_id:
                try:
                    # Extract numeric ID from GraphQL ID (e.g., "gid://gitlab/WorkItem/123")
                    main_status, children = get_issue_children(issue_id)
                    
                    # Update this issue's status for snapshot tracking
                    issue['_main_status'] = main_status
                    
                    # Process children to set their parent_id
                    for child in children:
                        child_iid = child.get('iid')
                        if child_iid in issues_by_iid:
                            # Update child's parent_id
                            issues_by_iid[child_iid]['parent_id'] = issue.get('iid')
                            # Update child's status
                            issues_by_iid[child_iid]['_main_status'] = child.get('status')
                            print(f"   ✓ Linked child {child_iid} to parent {issue.get('iid')}")
                
                except Exception as e:
                    print(f"⚠️  Warning: Failed to get children for issue {issue.get('iid')}: {e}")
                    issue['_main_status'] = ''
            
            # Display progress every 10 issues or on completion
            processed += 1
            if processed % 10 == 0 or processed == total_issues:
                print(f"   📊 Progress: {processed}/{total_issues} issues processed ({processed/total_issues:.1%})")
        
        # Step 3: Insert into legacy issues table for backward compatibility
        self.db.insert_issues_batch(project_id, issues_data, snapshot_at)
        
        # Step 4: Upsert into issue_main table (latest state)
        # Track how many are new vs updated
        issues_before = len(self.db.get_all_issues_main(project_id))
        self.db.upsert_issues_main_batch(project_id, issues_data)
        issues_after = len(self.db.get_all_issues_main(project_id))
        issue_main_new = max(0, issues_after - issues_before)
        print(f"✅ Upserted {issue_total} issues to issue_main table (new: {issue_main_new})")
        
        # Step 5: Create snapshots with status change detection
        # Now each issue has _main_status from GraphQL (either direct or from parent)
        snapshots = []
        for issue in issues_data:
            status = issue.get('_main_status', '')
            snapshots.append({
                'project_id': project_id,
                'iid': issue.get('iid'),
                'status': status,
                'snapshot_at': snapshot_at
            })
        
        # Batch insert snapshots with status change detection
        snapshot_stats = self.db.batch_insert_or_update_snapshots_with_status_change(snapshots)
        print(f"✅ Processed {len(snapshots)} snapshots to issue_snapshot table:")
        print(f"   - New statuses inserted: {snapshot_stats['inserted']}")
        print(f"   - Existing statuses updated: {snapshot_stats['updated']}")
        
        # Step 6: Format response according to PLAN.md specification
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
        
        print(f"📊 Getting issue summary for project {project_id} from {start_date} to {end_date}...")
        
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
    
    def get_issues_by_date_range(
        self,
        project_id: int,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get issues from database for a date range
        
        Args:
            project_id: Project ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of issues
        """
        return self.db.get_issues_by_date_range(project_id, start_date, end_date)


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


if __name__ == "__main__":

    # Example: Clone snapshot
    result = clone_snapshot(project_id=4)
    print(result)
    
    # Example: Get summary
    # summary = get_summary(project_id=4, start_date="2025-01-15")
    # print(summary)
    
    # Example: Update issue
    # result = update_issue(
    #     project_id=4,
    #     issue_iid=261,
    #     assignees=["username1", "username2"],
    #     labels=["bug", "high-priority"]
    # )
    # print(result)
