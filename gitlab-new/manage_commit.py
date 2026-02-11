"""
Commit Management Module

Provides functionality for:
1. Get commit summary statistics
2. Get commit snapshots
3. Query commits by issue
4. Update issue based on commit information
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from .api.client import GitLabClient
from .db.database import get_database
from .user.manager import UserManager
from .config import Config


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
        self.user_manager: Optional[UserManager] = None
    
    def _load_users(self, project_id: int):
        """Load users for the project"""
        if self.user_manager is None:
            self.user_manager = UserManager(self.config, project_id)
    
    def get_summary(
        self,
        project_id: int,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        获取指定时间范围内 Commit 的统计概要数据
        
        Args:
            project_id: 项目 ID
            start_date: 开始日期 (格式: YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYY-MM-DD)
            
        Returns:
            Dictionary containing commit summary statistics
        """
        print(f"📊 Getting commit summary for project {project_id} from {start_date} to {end_date}...")
        
        summary = self.db.get_commits_summary(project_id, start_date, end_date)
        
        print(f"✅ Commit summary: {summary}")
        return summary
    
    def get_snapshot(
        self,
        project_id: int,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        获取指定时间范围内所有 Commit 的详细信息快照
        
        Args:
            project_id: 项目 ID
            start_date: 开始日期 (格式: YYYY-MM-DD)
            end_date: 结束日期 (格式: YYYY-MM-DD)
            
        Returns:
            Dictionary containing list of commits
        """
        print(f"🔄 Cloning commit snapshot for project {project_id} from {start_date} to {end_date}...")
        
        # Get commits from GitLab API
        # Convert dates to ISO format for API
        since_date = f"{start_date}T00:00:00Z"
        until_date = f"{end_date}T23:59:59Z"
        
        commits_data = self.api_client.get_commits(
            project_id,
            since=since_date,
            until=until_date,
            all_commits=True
        )
        
        print(f"✅ Fetched {len(commits_data)} commits from GitLab")
        
        # Process commits to extract issue references
        enriched_commits = []
        for commit in commits_data:
            enriched_commit = self._enrich_commit_with_issue(project_id, commit)
            enriched_commits.append(enriched_commit)
        
        # Insert commits into database (use end_date as snapshot date)
        self.db.insert_commits_batch(project_id, enriched_commits, end_date)
        
        # Format response as per PLAN
        commits_response = [
            {
                "title": commit.get('title'),
                "project": commit.get('project_name', ''),
                "iid": commit.get('short_id'),
                "author_name": commit.get('author_name'),
                "authored_date": commit.get('committed_date'),
                "committed_date": commit.get('committed_date'),
                "short_id": commit.get('short_id'),
                "rate": commit.get('rate', 'normal')  # TODO: Implement rate calculation
            }
            for commit in enriched_commits
        ]
        
        result = {
            "project_id": project_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_count": len(commits_response),
            "commits": commits_response
        }
        
        print(f"✅ Clone snapshot completed: {len(commits_response)} commits")
        return result
    
    def get_commits_by_issue(
        self,
        project_id: int,
        issue_iid: int
    ) -> Dict[str, Any]:
        """
        根据 Issue IID 获取关联的所有 Commit 信息
        
        Args:
            project_id: 项目 ID
            issue_iid: Issue IID
            
        Returns:
            Dictionary containing issue info and commits
        """
        print(f"🔍 Getting commits for issue {issue_iid} in project {project_id}...")
        
        # Get commits from database
        commits = self.db.get_commits_by_issue(project_id, issue_iid)
        
        # Format response as per PLAN
        commits_response = [
            {
                "title": commit.get('title'),
                "project": commit.get('project_name', ''),
                "author_name": commit.get('author_name'),
                "authored_date": commit.get('committed_date'),
                "committed_date": commit.get('committed_date')
            }
            for commit in commits
        ]
        
        result = {
            "issue_iid": issue_iid,
            "project_id": project_id,
            "total_count": len(commits_response),
            "commits": commits_response
        }
        
        print(f"✅ Found {len(commits_response)} commits for issue {issue_iid}")
        return result
    
    def update_issue_by_commit(
        self,
        project_id: int,
        issue_iid: int,
        author_name: str,
        is_frontend: bool = False,
        is_backend: bool = False
    ) -> Dict[str, Any]:
        """
        根据 Commit 作者更新对应 Issue 的指派人和标签
        
        如果前端完成添加 `front_finished` 标签，后端完成添加 `backend_finished` 标签
        
        Args:
            project_id: 项目 ID
            issue_iid: Issue IID
            author_name: Commit 作者用户名
            is_frontend: 是否为前端提交
            is_backend: 是否为后端提交
            
        Returns:
            Dictionary containing update result
        """
        print(f"✏️  Updating issue {issue_iid} based on commit by {author_name}...")
        
        # Load users for validation
        self._load_users(project_id)
        
        # Validate author exists
        user = self.user_manager.get_user_by_username(author_name)
        if not user:
            print(f"❌ Error: User '{author_name}' not found in project members")
            return {
                "success": False,
                "error": f"User '{author_name}' not found in project members"
            }
        
        # Determine labels to add
        labels_to_add = []
        if is_frontend:
            labels_to_add.append("front_finished")
        if is_backend:
            labels_to_add.append("backend_finished")
        
        # Get current issue
        try:
            current_issue = self.api_client.get_issue(project_id, issue_iid)
        except Exception as e:
            print(f"❌ Error fetching issue {issue_iid}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        
        # Update assignees (add author if not already assigned)
        current_assignees = [a.get('username') for a in current_issue.get('assignees', [])]
        new_assignees = list(set(current_assignees + [author_name]))
        
        self.api_client.update_issue_assignees(project_id, issue_iid, new_assignees)
        
        # Add labels
        if labels_to_add:
            self.api_client.add_issue_labels(project_id, issue_iid, labels_to_add)
        
        # Get updated issue
        updated_issue = self.api_client.get_issue(project_id, issue_iid)
        updated_labels = updated_issue.get('labels', [])
        
        result = {
            "success": True,
            "updated": {
                "issue_iid": issue_iid,
                "assignees": new_assignees,
                "added_labels": [l for l in labels_to_add if l in updated_labels],
                "all_labels": updated_labels
            }
        }
        
        print(f"✅ Issue {issue_iid} updated successfully")
        return result
    
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
        # Simple issue reference extraction from commit message
        # Pattern: #123 or !123
        message = commit.get('message', '')
        title = commit.get('title', '')
        
        issue_iid = None
        
        # Try to extract issue ID from message or title
        import re
        patterns = [r'#(\d+)', r'!(\d+)', r'\[(\d+)\]', r'Issue (\d+)']
        
        combined_text = f"{title} {message}"
        
        for pattern in patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            if matches:
                issue_iid = int(matches[0])
                break
        
        # Get project name
        try:
            project = self.api_client.get_project(project_id)
            project_name = project.name
        except Exception:
            project_name = ""
        
        # Add rate (TODO: Implement proper rate calculation logic)
        rate = self._calculate_commit_rate(commit)
        
        enriched = {
            **commit,
            'project_name': project_name,
            'issue_iid': issue_iid,
            'rate': rate
        }
        
        return enriched
    
    def _calculate_commit_rate(self, commit: Dict[str, Any]) -> str:
        """
        Calculate commit rate/priority
        
        TODO: Implement proper rate calculation based on:
        - Number of files changed
        - Lines added/removed
        - Commit message length
        - Keywords indicating importance
        
        Args:
            commit: Commit data
            
        Returns:
            Rate string: 'high', 'medium', or 'normal'
        """
        # Basic placeholder implementation
        title = commit.get('title', '').lower()
        message = commit.get('message', '').lower()
        
        # Check for high-priority keywords
        high_priority_keywords = ['critical', 'urgent', 'fix', 'bug', 'security', 'hotfix', '紧急', '严重']
        
        combined_text = f"{title} {message}"
        
        if any(keyword in combined_text for keyword in high_priority_keywords):
            return 'high'
        
        return 'normal'
    
    def get_commits_by_date_range(
        self,
        project_id: int,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get commits from database for a date range
        
        Args:
            project_id: Project ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of commits
        """
        return self.db.get_commits_by_date_range(project_id, start_date, end_date)


# Convenience functions

def get_summary(project_id: int, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Convenience function: Get commit summary
    
    Args:
        project_id: Project ID
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        Dictionary containing summary
    """
    manager = CommitManager()
    return manager.get_summary(project_id, start_date, end_date)


def get_snapshot(project_id: int, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Convenience function: Get commit snapshot
    
    Args:
        project_id: Project ID
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        Dictionary containing commits
    """
    manager = CommitManager()
    return manager.get_snapshot(project_id, start_date, end_date)


def get_commits_by_issue(project_id: int, issue_iid: int) -> Dict[str, Any]:
    """
    Convenience function: Get commits by issue
    
    Args:
        project_id: Project ID
        issue_iid: Issue IID
        
    Returns:
        Dictionary containing commits
    """
    manager = CommitManager()
    return manager.get_commits_by_issue(project_id, issue_iid)


def update_issue_by_commit(
    project_id: int,
    issue_iid: int,
    author_name: str,
    is_frontend: bool = False,
    is_backend: bool = False
) -> Dict[str, Any]:
    """
    Convenience function: Update issue by commit
    
    Args:
        project_id: Project ID
        issue_iid: Issue IID
        author_name: Commit author username
        is_frontend: Is frontend commit
        is_backend: Is backend commit
        
    Returns:
        Dictionary containing update result
    """
    manager = CommitManager()
    return manager.update_issue_by_commit(
        project_id, issue_iid, author_name, is_frontend, is_backend
    )


if __name__ == "__main__":
    # Example usage
    import os
    
    # Set token for testing
    if not os.getenv('GITLAB_PRIVATE_TOKEN'):
        print("⚠️  Please set GITLAB_PRIVATE_TOKEN environment variable")
        exit(1)
    
    # Example: Get commit snapshot
    # result = get_snapshot(
    #     project_id=4,
    #     start_date="2025-01-15",
    #     end_date="2025-01-21"
    # )
    # print(result)
    
    # Example: Get commit summary
    # summary = get_summary(
    #     project_id=4,
    #     start_date="2025-01-15",
    #     end_date="2025-01-21"
    # )
    # print(summary)
    
    # Example: Get commits by issue
    # commits = get_commits_by_issue(project_id=4, issue_iid=123)
    # print(commits)
    
    # Example: Update issue by commit
    # result = update_issue_by_commit(
    #     project_id=4,
    #     issue_iid=261,
    #     author_name="username",
    #     is_frontend=True
    # )
    # print(result)
