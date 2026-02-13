"""
REST API module for GitLab package
"""

from .client import GitLabClient
from .llm_client import LLMClient

__all__ = [
    "GitLabClient",
    "LLMClient",
]
