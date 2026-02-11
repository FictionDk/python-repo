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
        同时写入 issue_main 表和 issue_snapshot 表
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Dictionary containing list of issues
        """
        # Use current date as snapshot date
        snapshot_at = datetime.now().strftime('%Y-%m-%d')
        print(f"🔄 Cloning issue snapshot for project {project_id} from {snapshot_at}...")
        
        # Get issues from GitLab API
        issues_data = self.api_client.get_issues(project_id, all_issues=True)
        
        print(f"✅ Fetched {len(issues_data)} issues from GitLab")
        
        # Insert into legacy issues table for backward compatibility
        self.db.insert_issues_batch(project_id, issues_data, snapshot_at)
        
        # Upsert into issue_main table (latest state)
        self.db.upsert_issues_main_batch(project_id, issues_data)
        print(f"✅ Upserted {len(issues_data)} issues to issue_main table")
        
        # Get main_status from GraphQL API and insert to issue_snapshot
        from .graphql.client import get_issue_children
        snapshots = []
        for issue in issues_data:
            issue_id = issue.get('id')
            if issue_id:
                # Extract numeric ID from GraphQL ID (e.g., "gid://gitlab/WorkItem/123")
                try:
                    numeric_id = int(issue_id.split('/')[-1])
                    main_status, children = get_issue_children(
                        numeric_id,
                        self.config.private_token,
                        self.config.graphql_url
                    )
                    snapshots.append({
                        'project_id': project_id,
                        'iid': issue.get('iid'),
                        'status': main_status,
                        'snapshot_at': snapshot_at
                    })
                except Exception as e:
                    print(f"⚠️  Warning: Failed to get main_status for issue {issue.get('iid')}: {e}")
                    # Still insert snapshot with empty status
                    snapshots.append({
                        'project_id': project_id,
                        'iid': issue.get('iid'),
                        'status': '',
                        'snapshot_at': snapshot_at
                    })
        
        # Batch insert snapshots
        self.db.insert_issue_snapshots_batch(snapshots)
        print(f"✅ Inserted {len(snapshots)} snapshots to issue_snapshot table")
        
        # Format response (only include essential fields as per PLAN)
        issues_response = [
            {
                "title": issue.get('title'),
                "iid": issue.get('iid'),
                "assignees": [a.get('username') for a in issue.get('assignees', [])],
                "status": issue.get('state'),
                "labels": issue.get('labels', [])
            }
            for issue in issues_data
        ]
        
        result = {
            "project_id": project_id,
            "snapshot_date": snapshot_at,
            "total_count": len(issues_response),
            "issues": issues_response
        }
        
        print(f"✅ Clone snapshot completed: {len(issues_response)} issues")
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
    
    def clone_snapshot_filtered(
        self,
        project_id: int
    ) -> Dict[str, Any]:
        """
        Clone issue snapshot with filtering based on test_export_issues logic
        Only processes issues starting with module prefixes: STM, BCM, IDM, QSM, DMM, DOP
        Handles parent and child issues separately, tracking relationships
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary containing statistics and processed issues
        """
        from .graphql.client import get_issue_children
        
        snapshot_at = datetime.now().strftime('%Y-%m-%d')
        print(f"🔄 Cloning filtered issue snapshot for project {project_id} from {snapshot_at}...")
        
        # Get issues from GitLab API (same as test_export_issues)
        # Use the raw python-gitlab SDK for direct access matching test_export_issues
        project = self.api_client.gl.projects.get(project_id)
        issues = project.issues.list(all=True)
        
        print(f"✅ Fetched {len(issues)} total issues from GitLab")
        
        # Module prefixes to filter (same as test_export_issues)
        module_prefixes = ('STM', 'BCM', 'IDM', 'QSM', 'DMM', 'DOP')
        
        exported = []
        issue_desc = {}
        issue_data = []
        issue_messages = []
        
        count = 0
        skipped_count = 0
        
        for issue in issues:
            # Check if already processed as a child
            if issue.iid in exported:
                print(f"   - Child skip - {issue.iid}")
                issue_desc[issue.iid] = issue.description
                skipped_count += 1
                continue
            
            # Filter by module prefix
            if not str(issue.title).startswith(module_prefixes):
                skipped_count += 1
                continue
            
            # Get main_status and children from GraphQL
            main_status, children = get_issue_children(
                issue.id,
                self.config.private_token,
                self.config.graphql_url
            )
            
            # Extract module prefix
            module = issue.title[:3] if issue.title[:3] in module_prefixes else ''
            
            # Process parent issue
            parent_issue_dict = {
                'id': issue.id,
                'iid': issue.iid,
                'title': issue.title,
                'module': module,
                'parent_id': issue.iid,  # Parent is its own parent
                'description': issue.description,
                'labels': issue.labels,  # Already a list
                'state': issue.state,
                'main_status': main_status,
                'assignees': [
                    {
                        'id': a['id'],
                        'username': a['username'],
                        'name': a['name']
                    }
                    for a in issue.assignees
                ],
                'created_at': issue.created_at,
                'updated_at': issue.updated_at
            }
            issue_data.append(parent_issue_dict)
            exported.append(issue.iid)
            count += 1
            issue_messages.append(f"   ✓ Parent issue {issue.iid}: {issue.title[:50]}...")
            
            # Process child issues
            for child in children:
                if child['iid'] in exported:
                    print(f"   - Child skip - {child['iid']}")
                    skipped_count += 1
                    continue
                
                # Process child issue
                child_issue_dict = {
                    'id': child.get('id'),
                    'iid': child['iid'],
                    'title': child['title'],
                    'module': module,
                    'parent_id': issue.iid,  # Child's parent is the parent issue's iid
                    'description': '',
                    'labels': [label['title'] for label in child.get('labels', [])],
                    'state': child.get('state'),
                    'main_status': child.get('status'),
                    'assignees': [
                        {
                            'id': a.get('id'),
                            'username': a.get('username'),
                            'name': a.get('name')
                        }
                        for a in child.get('assignees', [])
                    ],
                    'created_at': child.get('createdAt'),
                    'updated_at': child.get('createdAt')
                }
                issue_data.append(child_issue_dict)
                exported.append(child['iid'])
                count += 1
                issue_messages.append(f"     → Child issue {child['iid']}")
        
        # Parent descriptions (for issues that were first encountered as children)
        for iid, desc in issue_desc.items():
            for i, issue in enumerate(issue_data):
                if issue['iid'] == iid:
                    issue_data[i]['description'] = desc
                    break
        
        print(f"\n📊 Processing {len(issue_data)} issues...")
        for msg in issue_messages[:10]:  # Show first 10
            print(msg)
        if len(issue_messages) > 10:
            print(f"   ... and {len(issue_messages) - 10} more")
        
        # Insert into legacy issues table
        self.db.insert_issues_batch(project_id, issue_data, snapshot_at)
        
        # Upsert into issue_main table
        self.db.upsert_issues_main_batch(project_id, issue_data)
        print(f"✅ Upserted {len(issue_data)} issues to issue_main table")
        
        # Insert to issue_snapshot table
        snapshots = []
        for issue in issue_data:
            snapshots.append({
                'project_id': project_id,
                'iid': issue['iid'],
                'status': issue.get('main_status', ''),
                'snapshot_at': snapshot_at
            })
        self.db.insert_issue_snapshots_batch(snapshots)
        print(f"✅ Inserted {len(snapshots)} snapshots to issue_snapshot table")
        
        result = {
            "project_id": project_id,
            "snapshot_date": snapshot_at,
            "total_issues_fetched": len(issues),
            "issues_processed": count,
            "issues_skipped": skipped_count,
            "module_prefixes": list(module_prefixes),
            "statistics": {
                'parent_issues': len([i for i in issue_data if i['iid'] == i['parent_id']]),
                'child_issues': len([i for i in issue_data if i['iid'] != i['parent_id']])
            }
        }
        
        print(f"✅ Clone filtered snapshot completed:")
        print(f"   - Total fetched: {result['total_issues_fetched']}")
        print(f"   - Processed: {result['issues_processed']}")
        print(f"   - Skipped: {result['issues_skipped']}")
        print(f"   - Parent issues: {result['statistics']['parent_issues']}")
        print(f"   - Child issues: {result['statistics']['child_issues']}")
        
        return result
    
    def clone_snapshot_with_child_tasks(
        self,
        project_id: int,
        start_date: str
    ) -> Dict[str, Any]:
        """
        Clone issue snapshot including child tasks from GraphQL
        
        Args:
            project_id: Project ID
            start_date: Snapshot date
            
        Returns:
            Dictionary containing issues with child tasks
        """
        from .graphql.client import get_issue_children
        
        print(f"🔄 Cloning issue snapshot with child tasks for project {project_id}...")
        
        # Get issues from API
        issues_data = self.api_client.get_issues(project_id, all_issues=True)
        
        # Enrich with child tasks
        enriched_issues = []
        for issue in issues_data:
            # Get child tasks via GraphQL
            main_status, children = get_issue_children(
                issue.get('id'),
                self.config.private_token,
                self.config.graphql_url
            )
            
            enriched_issue = {
                **issue,
                'main_status': main_status,
                'children': children
            }
            enriched_issues.append(enriched_issue)
        
        # Convert to format for database storage
        issues_to_store = []
        for issue in enriched_issues:
            issues_to_store.append(self._simplify_issue_for_db(issue))
        
            # Store child tasks as separate issues
            for child in issue.get('children', []):
                child_issue = {
                    'iid': child.get('iid'),
                    'title': child.get('title'),
                    'description': '',
                    'state': child.get('state'),
                    'labels': [l.get('title') for l in child.get('labels', [])],
                    'assignees': [a.get('username') for a in child.get('assignees', [])],
                    'created_at': child.get('createdAt'),
                    'updated_at': child.get('createdAt'),
                }
                issues_to_store.append(child_issue)
        
        # Store in database
        self.db.insert_issues_batch(project_id, issues_to_store, start_date)
        
        print(f"✅ Cloned {len(issues_to_store)} issues (including child tasks)")
        
        return {
            "project_id": project_id,
            "snapshot_date": start_date,
            "total_count": len(enriched_issues),
            "issues": enriched_issues
        }
    
    def _simplify_issue_for_db(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify issue dict for database storage"""
        return {
            'id': issue.get('id'),
            'iid': issue.get('iid'),
            'title': issue.get('title'),
            'description': issue.get('description'),
            'state': issue.get('state'),
            'labels': issue.get('labels', []),
            'assignees': issue.get('assignees', []),
            'created_at': issue.get('created_at'),
            'updated_at': issue.get('updated_at'),
        }


# Convenience functions

def clone_snapshot(project_id: int) -> Dict[str, Any]:
    """
    Convenience function: Clone issue snapshot
    
    Args:
        project_id: Project ID
        
    Returns:
        Dictionary containing issues
    """
    manager = IssueManager()
    return manager.clone_snapshot(project_id)


def clone_snapshot_filtered(project_id: int) -> Dict[str, Any]:
    """
    Convenience function: Clone filtered issue snapshot (module-based filtering)
    Only processes issues starting with STM, BCM, IDM, QSM, DMM, DOP
    Handles parent and child issues
    
    Args:
        project_id: Project ID
        
    Returns:
        Dictionary containing statistics and processed issues
    """
    manager = IssueManager()
    return manager.clone_snapshot_filtered(project_id)


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
    # Example usage
    import os
    
    # Set token for testing
    # if not os.getenv('GITLAB_PRIVATE_TOKEN'):
    #     print("⚠️  Please set GITLAB_PRIVATE_TOKEN environment variable")
    #     exit(1)
    
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
