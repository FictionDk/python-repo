# GitLab Package

A Python package for managing GitLab issues and commits with local SQLite database snapshot capabilities.

## Features

- **Issue Management**: Clone issue snapshots, get summary statistics, update assignees and labels
- **Commit Management**: Get commit snapshots, summary statistics, query by issue, auto-update issues based on commits
- **User Management**: Load, save, and manage project users
- **GraphQL Integration**: Query issue child tasks and work item hierarchy
- **SQLite Database**: Local storage for issue and commit snapshots
- **REST API Wrapper**: Simplified interface to GitLab REST API

## Installation

### Requirements

- Python 3.7+
- `python-gitlab` library

```bash
pip install python-gitlab requests
```

### Environment Variables

Set the following environment variables for authentication:

```bash
export GITLAB_BASE_URL="https://gitlab.stpass.com"
export GITLAB_PRIVATE_TOKEN="your-private-token"
export GITLAB_DB_PATH="./gitlab.db"  # Optional, defaults to ./gitlab.db
```

Or set them in your code:

```python
from gitlab_new import Config

config = Config(
    base_url="https://gitlab.stpass.com",
    private_token="your-private-token",
    db_path="./my_database.db"
)
```

## Quick Start

### Issue Management

```python
from gitlab_new.manage_issue import clone_snapshot, get_summary, update_issue

# Clone issue snapshot to database (uses current date)
result = clone_snapshot(project_id=4)
print(f"Cloned {result['total_count']} issues")

# Get issue summary statistics
summary = get_summary(
    project_id=4,
    start_date="2025-01-15",
    end_date="2025-01-22"
)
print(summary)

# Update issue assignees and labels
result = update_issue(
    project_id=4,
    issue_iid=261,
    assignees=["username1", "username2"],
    labels=["bug", "high-priority"]
)
print(result)
```

### Commit Management

```python
from gitlab_new.manage_commit import get_snapshot, get_summary, get_commits_by_issue, update_issue_by_commit

# Get commit snapshot
result = get_snapshot(
    project_id=4,
    start_date="2025-01-15",
    end_date="2025-01-22"
)
print(f"Cloned {result['total_count']} commits")

# Get commit summary
summary = get_summary(
    project_id=4,
    start_date="2025-01-15",
    end_date="2025-01-22"
)
print(summary)

# Get commits for a specific issue
commits = get_commits_by_issue(project_id=4, issue_iid=123)
print(commits)

# Update issue based on commit (auto-assign author and add labels)
result = update_issue_by_commit(
    project_id=4,
    issue_iid=261,
    author_name="username",
    is_frontend=True  # Will add "front_finished" label
)
print(result)
```

### User Management

```python
from gitlab_new.user import UserManager, User

# Load users from project
manager = UserManager(project_id=4)

# Get user by username
user = manager.get_user_by_username("username")
print(user)

# Save users to JSON
manager.save_to_json("members.json")

# Load users from JSON
manager2 = UserManager()
users = manager2.load_from_json("members.json")

# Save to database
manager.save_to_database()
```

## Module Structure

```
gitlab-new/
├── config.py           # Configuration management
├── manage_issue.py     # Issue management operations
├── manage_commit.py    # Commit management operations
├── api/
│   └── client.py       # GitLab REST API client wrapper
├── graphql/
│   └── client.py       # GraphQL client for work item queries
├── user/
│   └── manager.py      # User management
└── db/
    ├── models.py       # Database models
    └── database.py     # Database initialization
```

## API Reference

### IssueManager

#### Clone Snapshot

```python
def clone_snapshot(project_id: int) -> Dict[str, Any]:
    """Clone all issues for a project to the database using current date."""
```

#### Get Summary

```python
def get_summary(
    project_id: int, 
    start_date: str, 
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Get issue summary statistics for a date range."""
```

Returns:
```python
{
    "total": 100,
    "left_pending": 20,
    "to_development": 30,
    "to_testing": 15,
    "to_completed": 25,
    "to_bug": 0,
    "to_fixed": 0
}
```

#### Update Issue

```python
def update_issue(
    project_id: int,
    issue_iid: int,
    assignees: Optional[List[str]] = None,
    labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Update issue assignees and labels."""
```

### CommitManager

#### Get Snapshot

```python
def get_snapshot(
    project_id: int,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """Clone commits for a date range to the database."""
```

#### Get Summary

```python
def get_summary(
    project_id: int,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """Get commit summary statistics."""
```

Returns:
```python
{
    "total": 200,
    "requirements": 80,
    "fixes": 60,
    "closed": 60
}
```

#### Get Commits by Issue

```python
def get_commits_by_issue(project_id: int, issue_iid: int) -> Dict[str, Any]:
    """Get all commits associated with an issue."""
```

#### Update Issue by Commit

```python
def update_issue_by_commit(
    project_id: int,
    issue_iid: int,
    author_name: str,
    is_frontend: bool = False,
    is_backend: bool = False
) -> Dict[str, Any]:
    """
    Update issue based on commit.
    Adds commit author to assignees and adds:
    - 'front_finished' label if is_frontend=True
    - 'backend_finished' label if is_backend=True
    """
```

## Database Schema

### Issues Table

```sql
CREATE TABLE issues (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    iid INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    state TEXT,
    labels TEXT,          -- JSON array
    assignees TEXT,       -- JSON array of usernames
    created_at TEXT,
    updated_at TEXT,
    snapshot_date TEXT NOT NULL,
    UNIQUE(project_id, iid, snapshot_date)
);
```

### Commits Table

```sql
CREATE TABLE commits (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    iid TEXT,
    title TEXT NOT NULL,
    author_name TEXT NOT NULL,
    author_email TEXT,
    authored_date TEXT,
    committed_date TEXT,
    short_id TEXT,
    message TEXT,
    issue_iid INTEGER,
    snapshot_date TEXT NOT NULL,
    rate TEXT DEFAULT 'normal',
    UNIQUE(project_id, short_id, snapshot_date)
);
```

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    name TEXT,
    state TEXT,
    locked BOOLEAN,
    avatar_url TEXT,
    web_url TEXT,
    updated_at TEXT
);
```

## Label Mapping

The issue summary automatically categorizes issues based on labels:

| Label | Category |
|-------|----------|
| 待处理, pending | left_pending |
| 开发中, development | to_development |
| 测试中, testing | to_testing |
| 已完成, completed | to_completed |
| bug | to_bug |
| fixed | to_fixed |

## Notes

- The package stores snapshots with a `snapshot_date` field, allowing you to track changes over time
- Commit categorization (requirements/fixes/closed) is based on analyzing commit messages
- The `rate` field for commits is currently basic - TODO: Implement proper rate calculation
- GraphQL client queries use the GitLab Work Items API for getting child tasks

## License

This package is provided as-is for managing GitLab projects.
