"""
User manager for GitLab package
"""

import json
from typing import Optional, Dict, Any, List
from gitlab import Gitlab as GitLabSDK
from config import Config
from db.database import get_database


class User:
    """Standard user object"""
    
    def __init__(
        self,
        id: int,
        username: str,
        name: str,
        state: str = "active",
        locked: bool = False,
        avatar_url: Optional[str] = None,
        web_url: Optional[str] = None
    ):
        """
        Initialize user object
        
        Args:
            id: User ID
            username: Username
            name: User display name
            state: User state (e.g., 'active', 'blocked')
            locked: Whether the user is locked
            avatar_url: Avatar URL
            web_url: User web URL
        """
        self.id = id
        self.username = username
        self.name = name
        self.state = state
        self.locked = locked
        self.avatar_url = avatar_url
        self.web_url = web_url
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'state': self.state,
            'locked': self.locked,
            'avatar_url': self.avatar_url,
            'web_url': self.web_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User from dictionary"""
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            name=data.get('name'),
            state=data.get('state', 'active'),
            locked=data.get('locked', False),
            avatar_url=data.get('avatar_url'),
            web_url=data.get('web_url')
        )
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, username='{self.username}', name='{self.name}', state='{self.state}', locked={self.locked})"


class UserManager:
    """User management operations"""
    
    def __init__(self, config: Optional[Config] = None, project_id: Optional[int] = None):
        """
        Initialize user manager
        
        Args:
            config: Configuration object (uses default if not provided)
            project_id: Optional project ID to fetch users from
        """
        self.config = config or Config()
        self.project_id = project_id
        self.users_mapper: Dict[str, User] = {}
        
        if project_id:
            self._load_users_from_project(project_id)
    
    def _load_users_from_project(self, project_id: int):
        """
        Load users from project members
        
        Args:
            project_id: Project ID
        """
        gl = GitLabSDK(
            self.config.base_url,
            private_token=self.config.private_token,
            ssl_verify=self.config.ssl_verify
        )
        
        try:
            project = gl.projects.get(project_id)
            members = project.members_all.list(all=True)
            
            self.users_mapper = {}
            for member in members:
                user = User(
                    id=member.id,
                    username=member.username,
                    name=member.name,
                    state=member.state,
                    locked=member.locked,
                    avatar_url=member.avatar_url
                )
                self.users_mapper[member.username] = user
            
            print(f"✅ Loaded {len(self.users_mapper)} users from project {project_id}")
        except Exception as e:
            print(f"❌ Error loading users from project: {e}")
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username
            
        Returns:
            User object or None
        """
        return self.users_mapper.get(username, None)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None
        """
        for user in self.users_mapper.values():
            if user.id == user_id:
                return user
        return None
    
    def add_user(self, user: User):
        """
        Add user to manager
        
        Args:
            user: User object
        """
        self.users_mapper[user.username] = user
    
    def get_all_users(self) -> List[User]:
        """
        Get all users
        
        Returns:
            List of User objects
        """
        return list(self.users_mapper.values())
    
    def save_to_json(self, file_path: str = 'members.json'):
        """
        Save users to JSON file
        
        Args:
            file_path: JSON file path
        """
        users_data = [user.to_dict() for user in self.users_mapper.values()]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(self.users_mapper)} users to {file_path}")
    
    def load_from_json(self, file_path: str = 'members.json'):
        """
        Load users from JSON file
        
        Args:
            file_path: JSON file path
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            self.users_mapper = {}
            for data in users_data:
                user = User.from_dict(data)
                self.users_mapper[user.username] = user
            
            print(f"✅ Loaded {len(self.users_mapper)} users from {file_path}")
            return list(self.users_mapper.values())
        except FileNotFoundError:
            print(f"⚠️  File not found: {file_path}")
            return []
        except Exception as e:
            print(f"❌ Error loading users from JSON: {e}")
            return []
    
    def save_to_database(self):
        """Save users to database"""
        db = get_database()
        
        for user in self.users_mapper.values():
            db.insert_or_update_user(user.to_dict())
        
        print(f"✅ Saved {len(self.users_mapper)} users to database")
    
    def load_from_database(self):
        """Load users from database"""
        db = get_database()
        users_data = db.get_all_users()
        
        self.users_mapper = {}
        for data in users_data:
            user = User.from_dict(data)
            self.users_mapper[user.username] = user
        
        print(f"✅ Loaded {len(self.users_mapper)} users from database")
        return list(self.users_mapper.values())
    
    def __repr__(self) -> str:
        return f"UserManager(users_count={len(self.users_mapper)})"


# Convenience functions

def batch_insert_users(users: List[User], file_path: str = 'members.json'):
    """
    Batch insert users to JSON file (legacy function for compatibility)
    
    Args:
        users: List of User objects
        file_path: JSON file path
    """
    users_data = [user.to_dict() for user in users]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Batch inserted {len(users)} users to {file_path}")


if __name__ == "__main__":
    # Example usage
    from ..config import default_config
    
    # Load users from a project
    manager = UserManager(config=default_config, project_id=4)
    
    # Print all users
    for username, user in manager.users_mapper.items():
        print(f"{username}: {user.to_dict()}")
    
    # Save to JSON
    manager.save_to_json('members.json')
    
    # Load from JSON
    manager2 = UserManager()
    users = manager2.load_from_json('members.json')
    print(f"\nLoaded {len(users)} users from JSON")
