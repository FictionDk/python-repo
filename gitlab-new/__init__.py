"""
GitLab Package - A Python package for managing GitLab issues and commits
"""

__version__ = "0.1.0"

from .config import Config
from .api.client import GitLabClient
from .graphql.client import GraphQLClient
from .user.manager import UserManager
from .manage_issue import IssueManager
from .manage_commit import CommitManager

__all__ = [
    "Config",
    "GitLabClient",
    "GraphQLClient",
    "UserManager",
    "IssueManager",
    "CommitManager",
]
