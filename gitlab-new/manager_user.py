"""
Member Management Module

Provides functionality for:
1. Sync Members from GitLab to local database
2. Update user aliases for mapping commit author names to GitLab usernames
"""

from typing import Optional, Dict, Any
from api.client import GitLabClient
from db.database import get_database
from config import Config

class MemberManager:
    """Manager for GitLab member operations"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize member manager
        
        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config()
        self.api_client = GitLabClient(self.config)
        self.db = get_database()
    
    def sync_member(self, project_id: int) -> Dict[str, Any]:
        """
        同步 Member
        从client中获取当前项目内所有用户，并插入或更新users表中
        
        Args:
            project_id: 项目 ID

        Returns:
            Dictionary containing:
            - total: 总用户数
            - new: 新增用户数
            - updated: 更新用户数
        """
        print(f"🔄 Syncing members for project {project_id}...")
        
        # Get current users count before sync
        users_before = self.db.get_all_users()
        users_count_before = len(users_before)
        print(f"📊 Current users in database: {users_count_before}")
        
        # Fetch all project members from API
        try:
            members_data = self.api_client.get_project_members(project_id, all_members=True)
            print(f"✅ Fetched {len(members_data)} members from GitLab API")
        except Exception as e:
            print(f"❌ Error fetching members from GitLab: {e}")
            return {
                "success": False,
                "error": str(e),
                "total": 0,
                "new": 0,
                "updated": 0
            }
        
        # Insert or update each member
        new_count = 0
        updated_count = 0
        
        for member in members_data:
            username = member.get('username')
            
            # Check if user already exists
            existing_user = self.db.get_user_by_username(username)
            
            if existing_user is None:
                # New user
                new_count += 1
                print(f"   ➕ New user: {username} ({member.get('name')})")
            else:
                # Existing user
                updated_count += 1
                print(f"   🔄 Updating user: {username} ({member.get('name')})")
            
            # Preserve existing alias if present
            alias = None
            if existing_user and existing_user.get('alias'):
                alias = existing_user.get('alias')
            
            # Prepare user data
            user_data = {
                'id': member.get('id'),
                'username': member.get('username'),
                'name': member.get('name'),
                'state': member.get('state'),
                'locked': member.get('locked', False),
                'avatar_url': member.get('avatar_url'),
                'web_url': None,  # Not available in project members API
                'alias': alias
            }
            
            # Insert or update user
            self.db.insert_or_update_user(user_data)
        
        # Get final user count
        users_after = self.db.get_all_users()
        users_count_after = len(users_after)
        
        result = {
            "success": True,
            "total": len(members_data),
            "new": new_count,
            "updated": updated_count
        }
        
        print(f"✅ Member sync completed:")
        print(f"   - Total members in project: {len(members_data)}")
        print(f"   - New users added: {new_count}")
        print(f"   - Existing users updated: {updated_count}")
        print(f"   - Total users in database: {users_count_after}")
        
        return result
    
    def update_alias(self, alias_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        更新 alias
        用户手工更新alias到users，入参是username到别名的映射字典
        
        Args:
            alias_mapping: 字典，key是users的username，value是别名
                          例如: {"hek": "He Kui, Hek"}

        Returns:
            Dictionary containing:
            - success: 是否成功
            - total: 总更新的数量
            - updated: 成功更新的数量
            - failed: 失败的数量
            - details: 更新详情列表
        """
        print(f"✏️  Updating user aliases for {len(alias_mapping)} users...")
        
        updated_count = 0
        failed_count = 0
        details = []
        
        for username, alias in alias_mapping.items():
            # Check if user exists
            existing_user = self.db.get_user_by_username(username)
            
            if existing_user is None:
                # User doesn't exist
                failed_count += 1
                details.append({
                    "username": username,
                    "alias": alias,
                    "status": "failed",
                    "message": f"User '{username}' not found in database"
                })
                print(f"   ❌ Failed: User '{username}' not found")
                continue
            
            # Update alias
            success = self.db.update_user_alias(username, alias)
            
            if success:
                updated_count += 1
                details.append({
                    "username": username,
                    "alias": alias,
                    "status": "success",
                    "message": "Alias updated successfully"
                })
                print(f"   ✅ Updated: {username} -> '{alias}'")
            else:
                failed_count += 1
                details.append({
                    "username": username,
                    "alias": alias,
                    "status": "failed",
                    "message": "Database update failed"
                })
                print(f"   ❌ Failed to update alias for: {username}")
        
        result = {
            "success": failed_count == 0,
            "total": len(alias_mapping),
            "updated": updated_count,
            "failed": failed_count,
            "details": details
        }
        
        print(f"✅ Alias update completed:")
        print(f"   - Total updates requested: {len(alias_mapping)}")
        print(f"   - Successfully updated: {updated_count}")
        print(f"   - Failed: {failed_count}")
        
        return result


# Convenience functions

def sync_member(project_id: int) -> Dict[str, Any]:
    """
    Convenience function: Sync members from GitLab to local database
    
    Args:
        project_id: Project ID
        
    Returns:
        Dictionary containing statistics
    """
    manager = MemberManager()
    return manager.sync_member(project_id)


def update_alias(alias_mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Convenience function: Update user aliases
    
    Args:
        alias_mapping: Dictionary mapping username to alias string
                      Example: {"hek": "He Kui, Hek"}
        
    Returns:
        Dictionary containing update result
    """
    manager = MemberManager()
    return manager.update_alias(alias_mapping)

if __name__ == "__main__":
    # Example: Sync members from project
    result = sync_member(project_id=4)
    update_alias(
        alias_mapping = {
            "hek": "hek,Fictio",
            "panzhihao": "Pan ZhiHao,panzhihao",
            "xuxf": "Xu Xuefeng",
            "lishuyang": "LiShuYang,Li ShuYang",
            "zhonghaofeng": "zhonghaofeng",
            "zhangyingjie": "Zhang YingJie",
            "qiujingkai": "qiujingkai",
            "oujunhao": "Ezio",
            "zhangyonghui": "zyh",
            "chenjunyu": "",
            "chenyx": "",
            "lanshu": "Alan",
            "lizehua1": "",
            "yanghangh": "",
            "lijj": "",
            "huangzeyue": "",
            "chiyifan": "Chi YiFan",
            "xiongdingan": "xiongdingan",
            "linjie": "",
            "heyuyao": "",
            "zengjiluo": "",
            "liy": "",
            "chenny": "",
            "dingchuankun": "Ding",
            "liangyaoxian": "",
            "wcheng": "",
            "tommy": "",
            "leehwh": "",
            "cody": "",
            "xiaowenhao": "xiaowenhao",
            "kelvin": "",
            "nichole": "",
            "taylor": "",
            "wc.yip": "",
            "jefferyleung": "",
            "josephine": "",
            "kevin": "",
            "alice": "",
            "evie": "",
            "michael": "",
            "huangsy": "黄少毅,shawn huang"
        })

