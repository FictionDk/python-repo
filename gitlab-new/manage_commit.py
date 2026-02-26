"""
Commit Management Module

Provides functionality for cloning/syncing commits from GitLab to database
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re

from api.client import GitLabClient
from api.llm_client import LLMClient
from db.database import get_database
from config import Config
from manage_issue import IssueManager
import json

class CommitManager:
    """Manager for GitLab commit operations"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize commit manager
        
        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config()
        self.api_client = GitLabClient(self.config)
        self.db = get_database()
    
    def _get_current_time_utc8(self) -> str:
        """
        Get current time in UTC+8 format
        
        Returns:
            Current time in format: 2026-02-12T15:32:00+08:00
        """
        now = datetime.now(ZoneInfo('Asia/Shanghai'))
        return now.isoformat()
    
    def _get_time_days_ago_utc8(self, days: int) -> str:
        """
        Get time N days ago in UTC+8 format
        
        Args:
            days: Number of days ago
            
        Returns:
            Time in format: 2026-02-12T15:32:00+08:00
        """
        time_ago = datetime.now(ZoneInfo('Asia/Shanghai')) - timedelta(days=days)
        return time_ago.isoformat()
    
    def _parse_commit_operations(self, commit_message: str) -> tuple[str, Optional[str]]:
        """
        解析提交消息中的操作信息
        支持多个 issue_iid，使用逗号分隔
        
        Args:
            commit_message: 提交消息
            
        Returns:
            (operation, issue_iids) - issue_iids 可以是 None 或 "123,456,789" 格式
            
        Examples:
            "related#123" -> ('related', '123')
            "related#123,456" -> ('related', '123,456')
            "fix#789,1011,1213" -> ('fix', '789,1011,1213')
        """
        # 匹配操作符和后面的数字序列（支持逗号分隔）
        pattern = r'(\w+)#([\d,]+)'
        match = re.search(pattern, commit_message)
        if match:
            operation = match.group(1)
            # 确保数字序列格式正确（移除可能的重复逗号等）
            issue_iids = ','.join(iid.strip() for iid in match.group(2).split(',') if iid.strip())
            return operation, issue_iids
        else:
            return '', None
        
    def clone_all_commit(self, filter=['dev-design','casdoor']):
        projects = self.api_client.get_projects()
        for p in projects:
            if p.name in filter:
                continue
            else:
                self.clone_commit(p.id)

    
    def clone_commit(self, project_id: int) -> int:
        """
        Clone/sync commits from GitLab to database
        
        Flow:
        1. Get last committed_date from database
        2. If none exists, use 60 days ago
        3. Get commits from last_date to now (UTC+8)
        4. Store new commits in database
        5. Return count of newly added commits
        
        Args:
            project_id: Project ID
            
        Returns:
            Number of newly inserted commits
        """
        print(f"🔄 Cloning commits for project {project_id}...")
        
        # Step 1: Get last committed_date from database
        last_commit_date = self.db.get_last_commit_date(project_id)
        
        # Step 2: Determine start date
        if last_commit_date:
            # Use the last commit date
            since_date = last_commit_date
            print(f"  Last commit date in DB: {last_commit_date}")
        else:
            # No commits in DB, use 60 days ago
            since_date = self._get_time_days_ago_utc8(60)
            print(f"  No commits in DB, using 60 days ago: {since_date}")
        
        # Step 3: Get current time in UTC+8
        until_date = self._get_current_time_utc8()
        print(f"  Current time (UTC+8): {until_date}")
        
        # Convert UTC+8 dates to UTC for GitLab API
        # Parse the ISO format dates with timezone info
        since_dt = datetime.fromisoformat(since_date)
        since_utc = since_dt.astimezone(ZoneInfo('UTC')).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        until_dt = datetime.fromisoformat(until_date)
        until_utc = until_dt.astimezone(ZoneInfo('UTC')).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Step 4: Fetch commits from GitLab API
        print(f"  Fetching commits from {since_utc}/{since_dt} to {until_utc}/{until_dt}...")
        commits_data = self.api_client.get_commits(
            project_id,
            since=since_utc,
            until=until_utc,
            all_commits=True
        )
        
        print(f"  ✅ Fetched {len(commits_data)} commits from GitLab")
        
        if not commits_data:
            print(f"✅ No new commits found for project {project_id}")
            return 0
        
        # Step 5: Process and enrich commits
        enriched_commits = []
        for commit in commits_data:
            enriched_commit = self._enrich_commit_with_issue(project_id, commit)
            enriched_commits.append(enriched_commit)
        
        # Step 6: Insert commits into database
        self.db.insert_commits_batch(project_id, enriched_commits)
        
        print(f"✅ Clone completed: {len(enriched_commits)} new commits inserted for project {project_id}")
        
        return len(enriched_commits)
    
    def _enrich_commit_with_issue(
        self,
        project_id: int,
        commit: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich commit data with issue reference information
        
        Args:
            project_id: Project ID
            commit: Commit data from API
            
        Returns:
            Enriched commit data
        """
        message = commit.get('message', '')
        project_name = ""
        group_name = ""
        
        try:
            project_info = self.api_client.get_project_info(project_id)
            project_name = project_info.get('name', '')
            group_name = project_info.get('group', '')
        except Exception:
            project_name = ""
            group_name = ""
        
        # Add rate_message (TODO: Implement proper rate calculation logic)
        rate_message = self._calculate_commit_rate(commit)
        # Parse operations from commit message
        operation, issue_iid = self._parse_commit_operations(message)
        enriched = {
            **commit,
            'project_name': project_name,
            'group_name': group_name,
            'issue_iid': issue_iid,
            'rate_message': rate_message,
            'rate_count': 0,
            'operation': operation
        }
        return enriched
    
    def _calculate_commit_rate(self, commit: Dict[str, Any]) -> str:
        return 'normal'
    
    def sync_issue_by_commit(self) -> Dict[str, Any]:
        """
        根据 Commit 作者更新对应 Issue 的指派人和标签。
        
        指派人更新逻辑：
        - 只要有 commit 关联到 issue，该 commit 的作者就会被指派
        - 不受 commit operation 类型限制
        - 通过别名将 author_name 映射到 GitLab 用户Id
        
        标签更新逻辑（仅当 operation=closed 时）：
        - 如果前端组（front）有 operation=closed 的提交，添加 `front::finished` 标签
        - 如果后端组（server）有 operation=closed 的提交，添加 `backend::finished` 标签
        - 如果两者都有 operation=closed 的提交，同时添加两个标签
        - 如果没有任何 operation=closed 的提交，不添加任何完成标签
        
        执行流程:
        1. 执行db.get_commits_needing_sync获取需要同步的commit列表
        2. 找出所有需要追加`front::finished`标签的issue列表
        3. 找出所有需要追加`backend::finished`标签的issue列表
        4. 为每个issue找到对应的userId列表
        5. 执行issue模块的update_issue方法
        6. 同步执行结果,将已更新的issue使用mark_issue_synced同步回数据库
        
        Returns:
            Dictionary containing:
            - total_issues_processed: Number of issues processed
            - success: Number of successfully updated issues
        """
        print("🔄 Starting issue sync based on commits...")
        
        # Step 1: Get commits needing sync
        commits = self.db.get_commits_needing_sync()
        
        if not commits:
            print("✅ No commits need synchronization")
            return {
                'total_issues_processed': 0,
                'success': 0
            }
        
        print(f"📊 Found {len(commits)} commits needing sync")
        
        # Initialize IssueManager for updating issues
        issue_manager = IssueManager(self.config)
        
        # Step 2 & 3: Organize commits by project and issue
        # Structure: {issue_iid: {'commit_ids': [], 'authors': set(), 'front_closed': bool, 'backend_closed': bool}}
        issues_to_update = {}
        
        for commit in commits:
            issue_iid_str = commit['issue_iid']
            author_name = commit['author_name']
            operation = commit['operation']
            group_name = commit['group_name']
            commit_id = commit['id']
            
            # issue_iid can contain multiple issues separated by commas
            issue_iids = [iid.strip() for iid in issue_iid_str.split(',') if iid.strip()]
            user = self.db.get_user_by_alias(author_name)
            
            for issue_iid in issue_iids:
                if issue_iid not in issues_to_update:
                    issues_to_update[issue_iid] = {
                        'commit_ids': [],
                        'authors': set(),
                        'front_closed': False,
                        'backend_closed': False
                    }
                
                # Add commit ID
                issues_to_update[issue_iid]['commit_ids'].append(commit_id)
                
                # Add author
                if user:
                    issues_to_update[issue_iid]['authors'].add(user['id'])
                
                # Check for operation=closed for label updates
                if operation.lower() == 'closed':
                    # Normalize group name for comparison
                    if group_name and group_name.lower() == 'front':
                        issues_to_update[issue_iid]['front_closed'] = True
                    elif group_name and group_name.lower() == 'server':
                        issues_to_update[issue_iid]['backend_closed'] = True
        
        print(f"📋 Found {sum(len(issues) for issues in issues_to_update.values())} unique issues to update")
        
        # Step 4 & 5: Update each issue
        total_issues_processed = 0
        success_count = 0
        all_synced_commit_ids = []

        for issue_iid, issue_data in issues_to_update.items():
            total_issues_processed += 1

            userIds = list(set(issue_data['authors']))

            # Step 5: Determine labels to add
            labels_to_add = ['start::dev']
            if issue_data['front_closed']:
                labels_to_add.append('front::finished')
            if issue_data['backend_closed']:
                labels_to_add.append('backend::finished')

            print(f"   📝 Updating issue {issue_iid}")
            print(f"      - Assignees: {userIds}")
            print(f"      - Labels to add: {labels_to_add}")
            
            # Call issue_manager.update_issue
            result = issue_manager.update_issue(
                project_id=4,
                issue_iid=int(issue_iid),
                assignees=userIds if userIds else None,
                labels=labels_to_add if labels_to_add else None
            )
            
            if result.get('success'):
                success_count += 1
                all_synced_commit_ids.extend(issue_data['commit_ids'])
                print(f"   ✅ Issue {issue_iid} updated successfully")
            else:
                print(f"   ❌ Failed to update issue {issue_iid}: {result.get('error', 'Unknown error')}")
    
        # Step 6: Mark commits as synced
        if all_synced_commit_ids:
            marked_count = self.db.mark_issue_synced(all_synced_commit_ids)
            print(f"✅ Marked {marked_count} commits as synced")
        
        return {
            'total_issues_processed': total_issues_processed,
            'success': success_count
        }
    
    def _get_week_date_range(self, date: Optional[datetime] = None) -> tuple[str, str]:
        """
        获取指定日期所在周的周一和周日日期
        
        Args:
            date: Reference date (defaults to current date)
            
        Returns:
            Tuple of (monday_date, sunday_date) in YYYY-MM-DD format
        """
        if date is None:
            date = datetime.now(ZoneInfo('Asia/Shanghai'))
        
        # Get Monday (weekday() returns 0 for Monday)
        days_since_monday = date.weekday()
        monday = date - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)
        
        return monday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d')
    
    def analyze_development_progress(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        project_ids: Optional[list[int]] = None
    ) -> str:
        """
        分析指定时间段内commit记录,输出开发进度
        
        Args:
            start_date: 开始日期 (格式: YYYY-MM-DD), 默认为本周一
            end_date: 结束日期 (格式: YYYY-MM-DD), 默认为本周日
            project_ids: 项目ID列表, 默认为None(查询所有项目)
            
        Returns:
            格式化的开发进度报告字符串
        """
        print("🔄 Analyzing development progress...")
        
        # Step 1: Determine date range
        if start_date is None:
            start_date, end_date = self._get_week_date_range()
        elif end_date is None:
            # Default to one week if only start_date is provided
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = start_dt + timedelta(days=6)
            end_date = end_dt.strftime('%Y-%m-%d')
        
        print(f"  Date range: {start_date} - {end_date}")
        
        # Step 2: Get all projects if not specified
        if project_ids is None:
            project_ids = [1, 8, 9, 6, 17, 10, 22, 25, 12, 7, 11]
            print(f"  Projects: {len(project_ids)} projects")
        
        # Step 3: Query commits
        commits = self.db.get_commits_summary(project_ids, start_date, end_date)
        print(f"  ✅ Found {len(commits)} commits")
        
        if not commits:
            return f"本周（{start_date} - {end_date}）完成了0次提交，暂无开发工作。"
        
        # Step 4: Aggregate statistics
        total_commits = len(commits)
        
        # Collect all issue information
        issue_info = {}  # {(project_id, issue_iid): dict with stats}
        
        for commit in commits:
            issue_iid_str = commit['issue_iid'] if commit['issue_iid'] else None
            if not issue_iid_str:
                continue
            
            project_id = commit['project_id']
            operation = commit['operation'].lower() if commit['operation'] else ''
            group_name = commit['group_name'].lower() if commit['group_name'] else ''
            
            # Handle multiple issue_iids
            issue_iids = [iid.strip() for iid in issue_iid_str.split(',') if iid.strip()]
            
            for issue_iid in issue_iids:
                issue_key = (project_id, int(issue_iid))
                
                if issue_key not in issue_info:
                    issue_info[issue_key] = {
                        'total_count': 0,
                        'related_count': 0,
                        'closed_count': 0,
                        'group': 'front' if group_name == 'front' else 'server' if group_name == 'server' else 'other'
                    }
                
                issue_info[issue_key]['total_count'] += 1
                
                if operation == 'related':
                    issue_info[issue_key]['related_count'] += 1
                elif operation == 'closed':
                    issue_info[issue_key]['closed_count'] += 1
        
        # Step 5: Count unique issues and completed issues
        unique_issues = len(issue_info)
        
        # Count completed issues by group (unique issues with closed_count > 0)
        completed_front = sum(1 for info in issue_info.values() 
                             if info['group'] == 'front' and info['closed_count'] > 0)
        completed_backend = sum(1 for info in issue_info.values() 
                               if info['group'] == 'server' and info['closed_count'] > 0)
        
        print(f"  📊 Stats: {total_commits} commits, {unique_issues} issues, "
              f"{completed_front + completed_backend} completed (front: {completed_front}, back: {completed_backend})")
        
        # Step 6: Get issue titles
        issue_keys = list(issue_info.keys())
        issue_iids_only = [issue_iid for _, issue_iid in issue_keys]
        issue_titles = self.db.get_issue_titles(issue_iids_only)
        
        # Step 7: Prepare data for LLM
        issues_data = []
        for (project_id, issue_iid), info in issue_info.items():
            title = issue_titles.get(issue_iid, f"Issue-{issue_iid}")
            issues_data.append({
                'title': title,
                'group': info['group'],
                'related_count': info['related_count'],
                'closed_count': info['closed_count']
            })
        
        # Sort by total count (most frequent first)
        issues_data.sort(key=lambda x: x['related_count'] + x['closed_count'], reverse=True)
        
        llm_data = {
            'total_commits': total_commits,
            'unique_issues': unique_issues,
            'completed_front': completed_front,
            'completed_backend': completed_backend,
            'issues': issues_data
        }
        
        # Step 8: Generate LLM summary
        llm_summary = "暂无详细总结"
        try:
            llm_client = LLMClient(self.config)
            
            prompt = f"""请根据以下开发数据生成简洁的中文总结（建议不超过300字），描述本周主要完成的工作内容：

{json.dumps(llm_data, ensure_ascii=False, indent=2)}

要求：
1. 以自然语言总结主要功能和改进点
2. 不要重复罗列issue标题
3. 重点描述完成的功能和修复的问题
4. 简洁明了突出重点"""
            
            create_at = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
            response, success = llm_client.generate_response(
                type='开发进度总结',
                req_content=prompt,
                create_at=create_at,
                db_instance=self.db
            )
            
            if success:
                llm_summary = response
                print(f"  ✅ LLM summary generated")
            else:
                print(f"  ⚠️  LLM summary generation failed: {response}")
            
        except Exception as e:
            print(f"  ⚠️  LLM summary generation error: {e}")
        
        # Step 9: Format output
        output = (f"本周（{start_date} - {end_date}）完成了{total_commits}次提交，"
                 f"关联{unique_issues}个issue,完成{completed_front + completed_backend}个issue开发"
                 f"（前端{completed_front}个，后端{completed_backend}个），"
                 f"主要处理内容为:{llm_summary}")
        
        print(f"✅ Development progress analysis completed")
        return output

def clone_all_commit(project_id: int) -> int:
    manager = CommitManager()
    if project_id == None:
        manager.clone_all_commit()
    else:
        manager.clone_commit(project_id)


def sync_issue_by_commit() -> Dict[str, Any]:
    """
    Convenience function: Sync issues based on commits
    
    Returns:
        Dictionary containing sync statistics
    """
    manager = CommitManager()
    return manager.sync_issue_by_commit()


def analyze_development_progress(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    project_ids: Optional[list[int]] = None
) -> str:
    """
    Convenience function: Analyze development progress for a time period
    
    Args:
        start_date: Start date (YYYY-MM-DD), defaults to this week's Monday
        end_date: End date (YYYY-MM-DD), defaults to this week's Sunday
        project_ids: List of project IDs, defaults to all projects
        
    Returns:
        Formatted development progress report string
        
    Example:
        # Analyze current week (default)
        report = analyze_development_progress()
        
        # Analyze specific week
        report = analyze_development_progress(
            start_date="2025-02-10",
            end_date="2025-02-16"
        )
        
        # Analyze specific projects
        report = analyze_development_progress(
            project_ids=[4, 5]
        )
    """
    manager = CommitManager()
    return manager.analyze_development_progress(start_date, end_date, project_ids)


if __name__ == "__main__":
    # Example: Clone all commits
    #clone_all_commit(None)
    
    # Example: Sync issues based on commits
    # result = sync_issue_by_commit()
    # print(f"{result['success']}/{result['total_issues_processed']}")
    print(analyze_development_progress())
