"""
Commit Management Module

Provides functionality for cloning/syncing commits from GitLab to database
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

from api.client import GitLabClient
from db.database import get_database
from config import Config
from manage_issue import IssueManager

class CommitManager:
    """Manager for GitLab commit operations"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize commit manager
        
        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config()
        self.api_client = GitLabClient(self.config)
        self.db = get_database()
    
    def _get_current_time_utc8(self) -> str:
        """
        Get current time in UTC+8 format
        
        Returns:
            Current time in format: 2026-02-12T15:32:00+08:00
        """
        now = datetime.now(ZoneInfo('Asia/Shanghai'))
        return now.strftime('%Y-%m-%dT%H:%M:%S%z')
    
    def _get_time_days_ago_utc8(self, days: int) -> str:
        """
        Get time N days ago in UTC+8 format
        
        Args:
            days: Number of days ago
            
        Returns:
            Time in format: 2026-02-12T15:32:00+08:00
        """
        time_ago = datetime.now(ZoneInfo('Asia/Shanghai')) - timedelta(days=days)
        return time_ago.strftime('%Y-%m-%dT%H:%M:%S%z')
    
    def _parse_commit_operations(self, commit_message: str) -> tuple[str, Optional[str]]:
        """
        解析提交消息中的操作信息
        支持多个 issue_iid，使用逗号分隔
        
        Args:
            commit_message: 提交消息
            
        Returns:
            (operation, issue_iids) - issue_iids 可以是 None 或 "123,456,789" 格式
            
        Examples:
            "related#123" -> ('related', '123')
            "related#123,456" -> ('related', '123,456')
            "fix#789,1011,1213" -> ('fix', '789,1011,1213')
        """
        # 匹配操作符和后面的数字序列（支持逗号分隔）
        pattern = r'(\w+)#([\d,]+)'
        match = re.search(pattern, commit_message)
        if match:
            operation = match.group(1)
            # 确保数字序列格式正确（移除可能的重复逗号等）
            issue_iids = ','.join(iid.strip() for iid in match.group(2).split(',') if iid.strip())
            return operation, issue_iids
        else:
            return '', None
        
    def clone_all_commit(self, filter=['dev-design','casdoor']):
        projects = self.api_client.get_projects()
        for p in projects:
            if p.name in filter:
                continue
            else:
                self.clone_commit(p.id)

    
    def clone_commit(self, project_id: int) -> int:
        """
        Clone/sync commits from GitLab to database
        
        Flow:
        1. Get last committed_date from database
        2. If none exists, use 60 days ago
        3. Get commits from last_date to now (UTC+8)
        4. Store new commits in database
        5. Return count of newly added commits
        
        Args:
            project_id: Project ID
            
        Returns:
            Number of newly inserted commits
        """
        print(f"🔄 Cloning commits for project {project_id}...")
        
        # Step 1: Get last committed_date from database
        last_commit_date = self.db.get_last_commit_date(project_id)
        
        # Step 2: Determine start date
        if last_commit_date:
            # Use the last commit date
            since_date = last_commit_date
            print(f"  Last commit date in DB: {last_commit_date}")
        else:
            # No commits in DB, use 60 days ago
            since_date = self._get_time_days_ago_utc8(60)
            print(f"  No commits in DB, using 60 days ago: {since_date}")
        
        # Step 3: Get current time in UTC+8
        until_date = self._get_current_time_utc8()
        print(f"  Current time (UTC+8): {until_date}")
        
        # Convert UTC+8 dates to UTC for GitLab API
        # Parse the ISO format dates with timezone info
        since_dt = datetime.fromisoformat(since_date)
        since_utc = since_dt.astimezone(ZoneInfo('UTC')).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        until_dt = datetime.fromisoformat(until_date)
        until_utc = until_dt.astimezone(ZoneInfo('UTC')).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Step 4: Fetch commits from GitLab API
        print(f"  Fetching commits from {since_utc}/{since_dt} to {until_utc}/{until_dt}...")
        commits_data = self.api_client.get_commits(
            project_id,
            since=since_utc,
            until=until_utc,
            all_commits=True
        )
        
        print(f"  ✅ Fetched {len(commits_data)} commits from GitLab")
        
        if not commits_data:
            print(f"✅ No new commits found for project {project_id}")
            return 0
        
        # Step 5: Process and enrich commits
        enriched_commits = []
        for commit in commits_data:
            enriched_commit = self._enrich_commit_with_issue(project_id, commit)
            enriched_commits.append(enriched_commit)
        
        # Step 6: Insert commits into database
        self.db.insert_commits_batch(project_id, enriched_commits)
        
        print(f"✅ Clone completed: {len(enriched_commits)} new commits inserted for project {project_id}")
        
        return len(enriched_commits)
    
    def _enrich_commit_with_issue(
        self,
        project_id: int,
        commit: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich commit data with issue reference information
        
        Args:
            project_id: Project ID
            commit: Commit data from API
            
        Returns:
            Enriched commit data
        """
        message = commit.get('message', '')
        project_name = ""
        group_name = ""
        
        try:
            project_info = self.api_client.get_project_info(project_id)
            project_name = project_info.get('name', '')
            group_name = project_info.get('group', '')
        except Exception:
            project_name = ""
            group_name = ""
        
        # Add rate_message (TODO: Implement proper rate calculation logic)
        rate_message = self._calculate_commit_rate(commit)
        # Parse operations from commit message
        operation, issue_iid = self._parse_commit_operations(message)
        enriched = {
            **commit,
            'project_name': project_name,
            'group_name': group_name,
            'issue_iid': issue_iid,
            'rate_message': rate_message,
            'rate_count': 0,
            'operation': operation
        }
        return enriched
    
    def _calculate_commit_rate(self, commit: Dict[str, Any]) -> str:
        return 'normal'
    
    def sync_issue_by_commit(self) -> Dict[str, Any]:
        """
        根据 Commit 作者更新对应 Issue 的指派人和标签。
        
        指派人更新逻辑：
        - 只要有 commit 关联到 issue，该 commit 的作者就会被指派
        - 不受 commit operation 类型限制
        - 通过别名将 author_name 映射到 GitLab 用户Id
        
        标签更新逻辑（仅当 operation=closed 时）：
        - 如果前端组（front）有 operation=closed 的提交，添加 `front::finished` 标签
        - 如果后端组（server）有 operation=closed 的提交，添加 `backend::finished` 标签
        - 如果两者都有 operation=closed 的提交，同时添加两个标签
        - 如果没有任何 operation=closed 的提交，不添加任何完成标签
        
        执行流程:
        1. 执行db.get_commits_needing_sync获取需要同步的commit列表
        2. 找出所有需要追加`front::finished`标签的issue列表
        3. 找出所有需要追加`backend::finished`标签的issue列表
        4. 为每个issue找到对应的userId列表
        5. 执行issue模块的update_issue方法
        6. 同步执行结果,将已更新的issue使用mark_issue_synced同步回数据库
        
        Returns:
            Dictionary containing:
            - total_issues_processed: Number of issues processed
            - success: Number of successfully updated issues
        """
        print("🔄 Starting issue sync based on commits...")
        
        # Step 1: Get commits needing sync
        commits = self.db.get_commits_needing_sync()
        
        if not commits:
            print("✅ No commits need synchronization")
            return {
                'total_issues_processed': 0,
                'success': 0
            }
        
        print(f"📊 Found {len(commits)} commits needing sync")
        
        # Initialize IssueManager for updating issues
        issue_manager = IssueManager(self.config)
        
        # Step 2 & 3: Organize commits by project and issue
        # Structure: {issue_iid: {'commit_ids': [], 'authors': set(), 'front_closed': bool, 'backend_closed': bool}}
        issues_to_update = {}
        
        for commit in commits:
            issue_iid_str = commit['issue_iid']
            author_name = commit['author_name']
            operation = commit['operation']
            group_name = commit['group_name']
            commit_id = commit['id']
            
            # issue_iid can contain multiple issues separated by commas
            issue_iids = [iid.strip() for iid in issue_iid_str.split(',') if iid.strip()]
            user = self.db.get_user_by_alias(author_name)
            
            for issue_iid in issue_iids:
                if issue_iid not in issues_to_update:
                    issues_to_update[issue_iid] = {
                        'commit_ids': [],
                        'authors': set(),
                        'front_closed': False,
                        'backend_closed': False
                    }
                
                # Add commit ID
                issues_to_update[issue_iid]['commit_ids'].append(commit_id)
                
                # Add author
                if user:
                    issues_to_update[issue_iid]['authors'].add(user['id'])
                
                # Check for operation=closed for label updates
                if operation.lower() == 'closed':
                    # Normalize group name for comparison
                    if group_name and group_name.lower() == 'front':
                        issues_to_update[issue_iid]['front_closed'] = True
                    elif group_name and group_name.lower() == 'server':
                        issues_to_update[issue_iid]['backend_closed'] = True
        
        print(f"📋 Found {sum(len(issues) for issues in issues_to_update.values())} unique issues to update")
        
        # Step 4 & 5: Update each issue
        total_issues_processed = 0
        success_count = 0
        all_synced_commit_ids = []

        for issue_iid, issue_data in issues_to_update.items():
            total_issues_processed += 1

            userIds = list(set(issue_data['authors']))

            # Step 5: Determine labels to add
            labels_to_add = []
            if issue_data['front_closed']:
                labels_to_add.append('front::finished')
            if issue_data['backend_closed']:
                labels_to_add.append('backend::finished')
            
            print(f"   📝 Updating issue {issue_iid}")
            print(f"      - Assignees: {userIds}")
            print(f"      - Labels to add: {labels_to_add}")
            
            # Call issue_manager.update_issue
            result = issue_manager.update_issue(
                project_id=4,
                issue_iid=int(issue_iid),
                assignees=userIds if userIds else None,
                labels=labels_to_add if labels_to_add else None
            )
            
            if result.get('success'):
                success_count += 1
                all_synced_commit_ids.extend(issue_data['commit_ids'])
                print(f"   ✅ Issue {issue_iid} updated successfully")
            else:
                print(f"   ❌ Failed to update issue {issue_iid}: {result.get('error', 'Unknown error')}")
    
        # Step 6: Mark commits as synced
        if all_synced_commit_ids:
            marked_count = self.db.mark_issue_synced(all_synced_commit_ids)
            print(f"✅ Marked {marked_count} commits as synced")
        
        return {
            'total_issues_processed': total_issues_processed,
            'success': success_count
        }

def clone_all_commit(project_id: int) -> int:
    manager = CommitManager()
    if project_id == None:
        manager.clone_all_commit()
    else:
        manager.clone_commit(project_id)


def sync_issue_by_commit() -> Dict[str, Any]:
    """
    Convenience function: Sync issues based on commits
    
    Returns:
        Dictionary containing sync statistics
    """
    manager = CommitManager()
    return manager.sync_issue_by_commit()


if __name__ == "__main__":
    # Example: Clone all commits
    # clone_all_commit(None)
    
    # Example: Sync issues based on commits
    result = sync_issue_by_commit()
    print(f"{result['success']}/{result['total_issues_processed']}")
