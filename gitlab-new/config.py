"""
Configuration management for GitLab package
"""

import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Configuration for GitLab API connections and database"""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        private_token: Optional[str] = None,
        db_path: Optional[str] = None
    ):
        """
        Initialize configuration
        
        Args:
            base_url: GitLab base URL (default: from environment or https://gitlab.stpass.com)
            private_token: GitLab private token (default: from environment)
            db_path: SQLite database path (default: ./gitlab.db)
        """
        load_dotenv()
        self.base_url = base_url or os.getenv('GITLAB_BASE_URL', 'https://gitlab.stpass.com')
        self.private_token = private_token or os.getenv('GITLAB_PRIVATE_TOKEN')
        self.graphql_url = f"{self.base_url}/api/graphql"
        self.db_path = db_path or os.getenv('GITLAB_DB_PATH', './gitlab.db')
        self.ssl_verify = False  # Default to False for internal GitLab instances
    
    def validate(self) -> bool:
        """
        Validate configuration
        
        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.private_token:
            print("Warning: GITLAB_PRIVATE_TOKEN not set")
            return False
        return True


# Default configuration instance
default_config = Config()
