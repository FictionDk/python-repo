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
    
    def get_summary(
        self,
        project_id_arr: list[int],
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Get commits summary by issue within specified project list and date range
        
        Args:
            project_id_arr: List of project IDs
            start_date: Start date in format YYYY-MM-DD
            end_date: End date in format YYYY-MM-DD
            
        Returns:
            Dictionary containing total commits count and issue summary list
            Format:
            {
                "total": 99,
                "issue_list": [
                    {
                        "iid": 198,
                        "related_group_arr": ["front"],
                        "closed_group_arr": ["front", "server"],
                        "author_arr": ["zyh", "hek"],
                        "count": 2
                    }
                ]
            }
        """
        # Get commits from database
        rows = self.db.get_commits_summary(project_id_arr, start_date, end_date)
        
        # Initialize result structure
        issue_stats: Dict[int, Dict[str, Any]] = {}
        
        for row in rows:
            commit = {
                'group_name': row['group_name'],
                'author_name': row['author_name'],
                'issue_iid': row['issue_iid'],
                'operation': row['operation']
            }
            
            # Handle multiple issue_iids (comma-separated)
            issue_iids = []
            if commit['issue_iid']:
                issue_iids = [iid.strip() for iid in commit['issue_iid'].split(',') if iid.strip()]
            
            # If no issue_iid, skip this commit
            if not issue_iids:
                continue
            
            # Process each issue_id
            for iid_str in issue_iids:
                try:
                    iid = int(iid_str)
                except (ValueError, TypeError):
                    continue
                
                # Initialize issue stats if not exists
                if iid not in issue_stats:
                    issue_stats[iid] = {
                        'iid': iid,
                        'related_group_arr': [],
                        'closed_group_arr': [],
                        'author_arr': [],
                        'count': 0
                    }
                
                # Update statistics
                stats = issue_stats[iid]
                stats['count'] += 1
                
                # Add group to related_group_arr (deduplicate later)
                if commit['group_name'] and commit['group_name'] not in stats['related_group_arr']:
                    stats['related_group_arr'].append(commit['group_name'])
                
                # Add group to closed_group_arr if operation is 'closed'
                if commit['operation'] and commit['operation'].lower() == 'closed':
                    if commit['group_name'] and commit['group_name'] not in stats['closed_group_arr']:
                        stats['closed_group_arr'].append(commit['group_name'])
                
                # Add author (deduplicate later)
                if commit['author_name'] and commit['author_name'] not in stats['author_arr']:
                    stats['author_arr'].append(commit['author_name'])
        
        # Convert issue_stats dict to list
        issue_list = list(issue_stats.values())
        
        # Build result
        result = {
            'total': len(rows),
            'issue_list': issue_list
        }
        
        return result

def clone_all_commit(project_id: int) -> int:
    manager = CommitManager()
    if project_id == None:
        manager.clone_all_commit()
    else:
        manager.clone_commit(project_id)

if __name__ == "__main__":
    clone_all_commit(None)
