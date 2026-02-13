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
    
    def _parse_commit_operations(self, commit_message: str) -> tuple[str, int]:
        """
        解析提交消息中的操作信息
        Args:
            commit_message: 提交消息
        Returns:
            related, 485
        """
        pattern = r'(\w+)#(\d+)'
        match = re.search(pattern, commit_message)
        if match:
            return match.group(1), match.group(2)
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

def clone_all_commit(project_id: int) -> int:
    manager = CommitManager()
    if project_id == None:
        manager.clone_all_commit()
    else:
        manager.clone_commit(project_id)

if __name__ == "__main__":
    clone_all_commit(None)
