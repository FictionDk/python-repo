"""
REST API client wrapper for GitLab
"""

from typing import Optional, List, Dict, Any
from gitlab import Gitlab as GitLabSDK
from config import Config


class GitLabClient:
    """Wrapper around python-gitlab SDK"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize GitLab client
        
        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config()
        self.gl = GitLabSDK(
            self.config.base_url,
            private_token=self.config.private_token,
            ssl_verify=self.config.ssl_verify
        )
    
    def get_project(self, project_id: int):
        """
        Get project by ID
        
        Args:
            project_id: Project ID
            
        Returns:
            GitLab Project object
        """
        return self.gl.projects.get(project_id)
    
    # ================== Issue Operations ==================
    
    def get_issues(self, project_id: int, all_issues: bool = True) -> List[Dict[str, Any]]:
        """
        Get all issues for a project
        
        Args:
            project_id: Project ID
            all_issues: Whether to fetch all issues (pagination)
            
        Returns:
            List of issue dictionaries
        """
        project = self.get_project(project_id)
        issues = project.issues.list(all=all_issues)
        
        return [self._issue_to_dict(issue) for issue in issues]
    
    def get_issue(self, project_id: int, issue_iid: int) -> Dict[str, Any]:
        """
        Get a specific issue
        
        Args:
            project_id: Project ID
            issue_iid: Issue IID
            
        Returns:
            Issue dictionary
        """
        project = self.get_project(project_id)
        issue = project.issues.get(issue_iid)
        return self._issue_to_dict(issue)
    
    def create_issue(
        self, 
        project_id: int, 
        title: str, 
        description: str = "",
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue
        
        Args:
            project_id: Project ID
            title: Issue title
            description: Issue description
            labels: List of labels
            assignees: List of assignee usernames
            
        Returns:
            Created issue dictionary
        """
        project = self.get_project(project_id)
        
        issue_data = {
            'title': title,
            'description': description
        }
        
        if labels:
            issue_data['labels'] = ','.join(labels)
        
        issue = project.issues.create(issue_data)
        issue_dict = self._issue_to_dict(issue)
        
        if assignees:
            self.update_issue_assignees(project_id, issue_iid=issue.iid, assignees=assignees)
        
        return issue_dict
    
    def update_issue(
        self, 
        project_id: int, 
        issue_iid: int, 
        description: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update issue properties
        
        Args:
            project_id: Project ID
            issue_iid: Issue IID
            description: New description
            labels: New labels (replaces existing)
            
        Returns:
            Updated issue dictionary
        """
        project = self.get_project(project_id)
        issue = project.issues.get(issue_iid)
        
        if description:
            issue.description = description
        
        if labels is not None:
            issue.labels = labels
        
        issue.save()
        return self._issue_to_dict(issue)
    
    def update_issue_assignees(
        self, 
        project_id: int, 
        issue_iid: int, 
        assignees: List[str]
    ) -> Dict[str, Any]:
        """
        Update issue assignees by username
        
        Args:
            project_id: Project ID
            issue_iid: Issue IID
            assignees: List of assignee usernames
            
        Returns:
            Updated issue dictionary
        """
        project = self.get_project(project_id)
        issue = project.issues.get(issue_iid)
        
        # Get user IDs from usernames
        assignee_ids = []
        for username in assignees:
            try:
                user = self.gl.users.list(username=username)[0]
                assignee_ids.append(user.id)
            except Exception as e:
                print(f"Warning: Could not find user {username}: {e}")
        
        if assignee_ids:
            issue.assignee_ids = assignee_ids
            issue.save()
        
        return self._issue_to_dict(issue)
    
    def add_issue_labels(
        self, 
        project_id: int, 
        issue_iid: int, 
        labels: List[str]
    ) -> Dict[str, Any]:
        """
        Add labels to issue (preserves existing labels)
        
        Args:
            project_id: Project ID
            issue_iid: Issue IID
            labels: Labels to add
            
        Returns:
            Updated issue dictionary
        """
        project = self.get_project(project_id)
        issue = project.issues.get(issue_iid)
        
        current_labels = issue.labels
        new_labels = list(set(current_labels + labels))
        
        issue.labels = new_labels
        issue.save()
        
        return self._issue_to_dict(issue)
    
    def remove_issue_labels(
        self, 
        project_id: int, 
        issue_iid: int, 
        labels: List[str]
    ) -> Dict[str, Any]:
        """
        Remove labels from issue
        
        Args:
            project_id: Project ID
            issue_iid: Issue IID
            labels: Labels to remove
            
        Returns:
            Updated issue dictionary
        """
        project = self.get_project(project_id)
        issue = project.issues.get(issue_iid)
        
        current_labels = issue.labels
        new_labels = [label for label in current_labels if label not in labels]
        
        issue.labels = new_labels
        issue.save()
        
        return self._issue_to_dict(issue)
    
    def _issue_to_dict(self, issue) -> Dict[str, Any]:
        """Convert GitLab issue object to dictionary"""
        return {
            'id': issue.id,
            'iid': issue.iid,
            'title': issue.title,
            'description': issue.description,
            'state': issue.state,
            'labels': list(issue.labels) if issue.labels else [],
            'assignees': [
                {
                    'id': a['id'],
                    'username': a['username'],
                    'name': a['name']
                }
                for a in issue.assignees
            ],
            'created_at': issue.created_at,
            'updated_at': issue.updated_at,
            'web_url': issue.web_url
        }
    
    # ================== Commit Operations ==================
    
    def get_commits(
        self, 
        project_id: int, 
        since: Optional[str] = None,
        until: Optional[str] = None,
        all_commits: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get commits for a project
        
        Args:
            project_id: Project ID
            since: Start date (ISO 8601 format)
            until: End date (ISO 8601 format)
            all_commits: Whether to fetch all commits
            
        Returns:
            List of commit dictionaries
        """
        project = self.get_project(project_id)
        
        kwargs = {'all': all_commits}
        if since:
            kwargs['since'] = since
        if until:
            kwargs['until'] = until
        
        commits = project.commits.list(**kwargs)
        
        return [self._commit_to_dict(commit) for commit in commits]
    
    def get_commit(self, project_id: int, commit_sha: str) -> Dict[str, Any]:
        """
        Get a specific commit
        
        Args:
            project_id: Project ID
            commit_sha: Commit SHA
            
        Returns:
            Commit dictionary
        """
        project = self.get_project(project_id)
        commit = project.commits.get(commit_sha)
        return self._commit_to_dict(commit)
    
    def get_commits_by_issue(
        self, 
        project_id: int, 
        issue_iid: int
    ) -> List[Dict[str, Any]]:
        """
        Get commits associated with an issue
        
        Args:
            project_id: Project ID
            issue_iid: Issue IID (e.g., reference like #123)
            
        Returns:
            List of commit dictionaries
        """
        project = self.get_project(project_id)
        
        # Get issue reference
        issue = project.issues.get(issue_iid)
        reference = issue.references.get('full', f"#{issue_iid}")
        
        # Get commits mentioning this issue
        commits = project.commits.list(all=True)
        
        matching_commits = []
        for commit in commits:
            commit_dict = self._commit_to_dict(commit)
            if reference in commit_dict.get('message', '') or reference in commit_dict.get('title', ''):
                matching_commits.append(commit_dict)
        
        return matching_commits
    
    def _commit_to_dict(self, commit) -> Dict[str, Any]:
        """Convert GitLab commit object to dictionary"""
        committer = commit.author_email if hasattr(commit, 'author_email') else commit.committer_email
        authored_date = commit.authored_date if hasattr(commit, 'authored_date') else commit.created_at
        
        return {
            'id': commit.id,
            'short_id': commit.short_id,
            'title': commit.title,
            'message': commit.message,
            'author_name': commit.author_name,
            'author_email': getattr(commit, 'author_email', ''),
            'committed_date': authored_date,
            'web_url': commit.web_url
        }
    
    # ================== User/Member Operations ==================
    
    def get_project_members(self, project_id: int, all_members: bool = True) -> List[Dict[str, Any]]:
        """
        Get all project members
        
        Args:
            project_id: Project ID
            all_members: Whether to fetch all members
            
        Returns:
            List of member dictionaries
        """
        project = self.get_project(project_id)
        members = project.members_all.list(all=all_members)
        
        return [
            {
                'id': member.id,
                'name': member.name,
                'username': member.username,
                'state': member.state,
                'locked': member.locked,
                'avatar_url': member.avatar_url
            }
            for member in members
        ]
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username
        
        Args:
            username: Username
            
        Returns:
            User dictionary or None
        """
        try:
            users = self.gl.users.list(username=username)
            if users:
                user = users[0]
                return {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'state': user.state,
                    'avatar_url': user.avatar_url,
                    'web_url': user.web_url
                }
        except Exception as e:
            print(f"Error fetching user {username}: {e}")
        
        return None
    
    # ================== Project Operations ==================
    
    def get_project_info(self, project_id: int) -> Dict[str, Any]:
        """
        Get project information
        
        Args:
            project_id: Project ID
            
        Returns:
            Project information dictionary
        """
        project = self.get_project(project_id)
        return {
            'id': project.id,
            'name': project.name,
            'path': project.path,
            'path_with_namespace': project.path_with_namespace,
            'default_branch': project.default_branch,
            'web_url': project.web_url,
            'created_at': project.created_at,
            'last_activity_at': project.last_activity_at
        }
