"""
GraphQL module for GitLab package
"""

from .client import GraphQLClient, get_issue_children, extract_child_task_details

__all__ = [
    "GraphQLClient",
    "get_issue_children",
    "extract_child_task_details",
]
