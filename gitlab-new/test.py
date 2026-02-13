"""
Simple test script for GitLab API operations
Run this file and modify parameters as needed
"""

from api.client import GitLabClient
from config import Config

# Initialize GitLab client
# Make sure you have .env file with GITLAB_PRIVATE_TOKEN configured
try:
    client = GitLabClient()
    print("✓ GitLab client initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize client: {e}")
    exit(1)

# ===================== Test append_issue_assignees =====================
def test_append_issue_assignees():
    """
    Test appending assignees to an issue
    
    Parameters:
        project_id: Project ID (integer)
        issue_iid: Issue IID (integer)
        assignees: List of user IDs to add as assignees (list of integers)
    
    Note: The assignees parameter should be user IDs (integers), not usernames
    """
    
    # TODO: Modify these parameters for your test
    project_id = 4  # e.g., 123
    issue_iid = 300   # e.g., 456
    assignees = [10]     # e.g., [101, 102]
    
    print(f"\n{'='*60}")
    print(f"Testing append_issue_assignees")
    print(f"Project ID: {project_id}")
    print(f"Issue IID: {issue_iid}")
    print(f"Assignees (user IDs): {assignees}")
    print(f"{'-'*60}")
    
    # Check required parameters
    if not project_id or not issue_iid or not assignees:
        print("⚠ Warning: Please set project_id, issue_iid, and assignees")
        print("Modify the parameters above and run again")
        return None
    
    # CAUTION: There are bugs in the original code:
    # 1. Line 132: if not project: - references undefined 'project' variable
    # 2. Line 139: if issue: - logic is inverted (returns None when issue exists)
    # 3. Line 142: Combines IDs with assignees list, but assignees should be user IDs, not usernames
    
    try:
        client.append_issue_assignees(project_id, issue_iid, assignees)
        result = client.get_issue(project_id, issue_iid)
        print("✓ Assignees appended successfully")
        print(f"\nResult:")
        print(f"  Issue ID: {result.get('id')}")
        print(f"  Issue IID: {result.get('iid')}")
        print(f"  Title: {result.get('title')}")
        print(f"  Assignees:")
        for assignee in result.get('assignees', []):
            print(f"    - {assignee.get('username')} ({assignee.get('name')}) [ID: {assignee.get('id')}]")
    
        return result
        
    except Exception as e:
        print(f"✗ Error occurred: {e}")
        return None


# ===================== Helper Methods =====================
def get_project_members(project_id):
    """Helper to get project member IDs for testing"""
    try:
        members = client.get_project_members(project_id)
        print(f"\nProject Members (Project ID: {project_id}):")
        for member in members:
            print(f"  - {member['username']} ({member['name']}) [ID: {member['id']}]")
        return members
    except Exception as e:
        print(f"✗ Error fetching members: {e}")
        return None


def get_issue_info(project_id, issue_iid):
    """Helper to get current issue information"""
    try:
        issue = client.get_issue(project_id, issue_iid)
        print(f"\nCurrent Issue Info (Project ID: {project_id}, Issue IID: {issue_iid}):")
        print(f"  Title: {issue.get('title')}")
        print(f"  Current Assignees:")
        for assignee in issue.get('assignees', []):
            print(f"    - {assignee.get('username')} ({assignee.get('name')}) [ID: {assignee.get('id')}]")
        return issue
    except Exception as e:
        print(f"✗ Error fetching issue: {e}")
        return None


# ===================== Main Execution =====================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("GitLab API Test Script")
    print("="*60)
    
    # Uncomment the methods you want to use
    
    # 1. Test append_issue_assignees
    result = test_append_issue_assignees()
    
    # 2. Get project members to find user IDs
    # get_project_members(project_id=123)
    
    # 3. Get current issue info before testing
    # get_issue_info(project_id=123, issue_iid=456)
    
    print(f"\n{'='*60}")
    print("Test completed")
    print("="*60 + "\n")
