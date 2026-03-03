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
        db_path: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        llm_model: Optional[str] = None,
        dingtalk_webhook_url: Optional[str] = None
    ):
        """
        Initialize configuration
        
        Args:
            base_url: GitLab base URL (default: from environment or https://gitlab.stpass.com)
            private_token: GitLab private token (default: from environment)
            db_path: SQLite database path (default: ./gitlab.db)
            llm_base_url: LLM API base URL (default: from environment)
            llm_api_key: LLM API key (default: from environment)
            llm_model: LLM model name (default: from environment)
            dingtalk_webhook_url: DingTalk webhook URL (default: from environment)
        """
        load_dotenv()
        self.base_url = base_url or os.getenv('GITLAB_BASE_URL', 'https://gitlab.stpass.com')
        self.private_token = private_token or os.getenv('GITLAB_PRIVATE_TOKEN')
        self.graphql_url = f"{self.base_url}/api/graphql"
        self.db_path = db_path or os.getenv('GITLAB_DB_PATH', './gitlab.db')
        self.ssl_verify = False  # Default to False for internal GitLab instances
        
        # LLM configuration
        self.llm_base_url = llm_base_url or os.getenv('LLM_BASE_URL', 'http://localhost:11434')
        self.llm_api_key = llm_api_key or os.getenv('LLM_API_KEY', '')
        self.llm_model = llm_model or os.getenv('LLM_MODEL', 'qwen2.5:7b')
        
        # DingTalk configuration
        self.dingtalk_webhook_url = dingtalk_webhook_url or os.getenv('DINGTALK_WEBHOOK_URL', '')
    
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
