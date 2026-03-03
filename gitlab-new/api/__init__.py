"""
REST API module for GitLab package
"""

from .gl_client import GitLabClient
from .llm_client import LLMClient

__all__ = [
    "GitLabClient",
    "LLMClient",
]
