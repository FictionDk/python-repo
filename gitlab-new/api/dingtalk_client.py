"""
DingTalk webhook client for sending messages
"""

from typing import Optional, List
from config import Config
import requests


class DingTalkClient:
    """Client for sending messages via DingTalk webhook"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize DingTalk client
        
        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config()
        self.webhook_url = self.config.dingtalk_webhook_url
    
    def send_text(
        self,
        content: str,
        at_mobiles: Optional[List[str]] = None,
        at_all: bool = False
    ) -> bool:
        """
        Send a text message via DingTalk webhook
        
        Args:
            content: The text message content
            at_mobiles: List of mobile numbers to @mention (optional)
            at_all: Whether to @all (notify everyone in the group) (default: False)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.webhook_url:
            print("Error: DingTalk webhook URL not configured")
            return False
        
        if not content:
            print("Error: Message content cannot be empty")
            return False
        
        # Build message payload
        payload = {
            "msgtype": "text",
            "text": {
                "content": content
            },
            "at": {
                "atMobiles": at_mobiles or [],
                "isAtAll": at_all
            }
        }
        
        try:
            # Send POST request to DingTalk webhook
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            # Check response
            response.raise_for_status()
            result = response.json()
            
            # DingTalk returns {"errcode": 0, "errmsg": "ok"} on success
            if result.get('errcode') == 0:
                print(f"DingTalk message sent successfully")
                return True
            else:
                print(f"DingTalk API error: {result.get('errmsg', 'Unknown error')}")
                return False
                
        except requests.exceptions.Timeout:
            print("Error: DingTalk webhook request timed out")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error sending DingTalk message: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error sending DingTalk message: {str(e)}")
            return False
