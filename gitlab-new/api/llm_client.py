"""
LLM API client wrapper for OpenAI-compatible local models
"""

from typing import Optional, Dict, Any, Tuple
from config import Config
import requests
import json


class LLMClient:
    """Wrapper for LLM API interactions using OpenAI-compatible format"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize LLM client
        
        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config()
        self.base_url = self.config.llm_base_url.rstrip('/')
        self.api_key = self.config.llm_api_key
        self.model = self.config.llm_model
    
    def generate_response(
        self,
        type: str,
        req_content: str,
        create_at: str,
        db_instance
    ) -> Tuple[str, bool]:
        """
        Generate LLM response and store in database
        
        Args:
            type: The type of request (e.g., "日汇总", "周汇总", "提交评价")
            req_content: The request content sent to LLM
            create_at: The timestamp for this record (ISO 8601 format)
            db_instance: Database instance to store history
            
        Returns:
            Tuple of (response_content, success_status)
        """
        # Insert initial record into database
        record_id = db_instance.insert_llm_history(
            type=type,
            create_at=create_at,
            req_content=req_content
        )
        
        try:
            # Make API call to LLM
            response = self._call_llm_api(req_content)
            
            # Remove thinking content from response if present
            clean_response = self._remove_thinking_content(response)
            
            # Update database with successful response
            db_instance.update_response(
                record_id=record_id,
                resp_content=clean_response,
                success=True
            )
            
            return clean_response, True
            
        except Exception as e:
            error_msg = f"LLM API call failed: {str(e)}"
            print(f"Error: {error_msg}")
            
            # Update database with failure status
            db_instance.update_response(
                record_id=record_id,
                resp_content=error_msg,
                success=False
            )
            
            return error_msg, False
    
    def _call_llm_api(self, prompt: str) -> str:
        """
        Make API call to LLM service using OpenAI-compatible format
        
        Args:
            prompt: The user prompt/request
            
        Returns:
            The raw LLM response text
            
        Raises:
            Exception: If the API call fails
        """
        # Construct OpenAI-compatible API endpoint
        api_url = f"{self.base_url}/v1/chat/completions"
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json'
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        # Prepare payload
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.7,
            'max_tokens': 2000
        }
        
        # Make the request
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=60  # 60 second timeout
        )
        
        # Check for errors
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        # Extract the message content
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content']
        else:
            raise Exception("Invalid response format from LLM API")
    
    def _remove_thinking_content(self, response: str) -> str:
        """
        Remove thinking content from LLM response
        
        This method removes content within <thinking>...</thinking> tags
        as specified in PLAN.md (剔除thinking)
        
        Args:
            response: The raw response from LLM
            
        Returns:
            Response with thinking content removed
        """
        # Remove <thinking>...</thinking> blocks
        import re
        thinking_pattern = r'<thinking>.*?</thinking>'
        clean_response = re.sub(thinking_pattern, '', response, flags=re.DOTALL)
        
        # Clean up extra whitespace
        clean_response = clean_response.strip()
        
        return clean_response
    
    def health_check(self) -> bool:
        """
        Check if LLM service is accessible
        
        Returns:
            True if service is accessible, False otherwise
        """
        try:
            api_url = f"{self.base_url}/v1/models"
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = requests.get(api_url, headers=headers, timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"LLM service health check failed: {e}")
            return False
