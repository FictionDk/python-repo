## 一、Issue管理

### 1.1 表结构

**表1: `issue_main`** - Issue 主表，存储当前最新状态
```sql
CREATE TABLE issue_main (
    project_id INTEGER NOT NULL,
    iid INTEGER NOT NULL,
    parent_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    state TEXT,
    latest_status TEXT,    -- issue_snapshot.status 默认为空
    milestone TEXT,        -- milestone.title
    labels TEXT,           -- JSON 数组，存储标签
    assignees TEXT,        -- JSON 数组，存储指派人
    created_at TEXT,
    updated_at TEXT,
    issue_id TEXT,         -- GraphQL ID (例如: "gid://gitlab/WorkItem/123")
    PRIMARY KEY (project_id, iid)
)
```
- 主键：`(project_id, iid)`
- 行为：UPSERT - 如果记录存在则更新，不存在则插入
- 用途：存储每个 Issue 的最新状态，便于快速查询和更新操作

**表2: `issue_snapshot`** - Issue 快照表，存储历史状态
```sql
CREATE TABLE issue_snapshot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    iid INTEGER NOT NULL,
    status TEXT,           -- 从 GraphQL API 获取的 main_status
    create_at TEXT NOT NULL, -- 当前status插入时间
    snapshot_at TEXT NOT NULL,  -- 快照日期 (格式: YYYY-MM-DD)最后一次的变更日期
    UNIQUE(project_id, iid, status)
)
```
- 主键：自增 `id`
- 唯一约束：`(project_id, iid, snapshot_at)`
- 字段 `status`：存储从 GraphQL API 获取的 `main_status`
- 用途：跟踪 Issue 状态随时间的变化，用于统计分析

### 1.2 方法

#### 1.2.1 同步 Issue 快照

1. 方法描述：获取当前时间点项目 Issue 的详细信息快照，并存入本地sqlite数据库
  - 先通过restful方式（api/client.py）获取指定project项目下所有issue和概要信息(iid、title、labels、assignees)
  - 再使用graphql方式（graphql/client.py）获取指定issue的其他关键信息(parent_id、status)
  - 分别更新或插入issue_main、issue_snapshot
  - 状态方式变更，才插入issue_snapshot，否则只是更新snapshot_at
2. 方法名称`clone_snapshot`
3. 入参：
  - `project_id`项目 ID (str/int)
4. 返回
  - issue总数
  - `issue_main`表此次新增数量
  - `issue_snapshot`表此次新增数量，状态（status）变更的issue数量

### 1.2.2 获取 Issue 概要

**方法描述**：根据 Issue 快照库获取指定时间范围(默认一周)内 Issue 的统计概要数据，包括各状态的 Issue 数量和该时间范围内开发关闭的 Issue 数。

**方法名**：`get_summary`

**入参**：
- `project_id`: 项目 ID (str/int)
- `start_date`: 开始日期 (格式: YYYY-MM-DD)
- `end_date`: 结束日期 (格式: YYYY-MM-DD)

**返回**：
```json
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

### 1.2.3 更新 Issue

**方法描述**：更新指定 Issue 的指派人（assignees）和标签（labels）。

**方法名**：`update_issue`

**入参**：
- `project_id`: 项目 ID (str/int)
- `issue_iid`: Issue IID (int)
- `assignees`: 指派人用户名列表 (Optional[List[str]])
- `labels`: 标签列表 (Optional[List[str]])

**返回**：
```json
{
  "success": true,
  "issue": {
    "iid": 123,
    "assignees": ["用户名1", "用户名2"],
    "labels": ["标签1", "标签2"]
  }
}
```


## 二、Commit管理 manage_commit.py

### 2.1 获取 Commit 概要

**方法描述**：获取指定时间范围内 Commit 的统计概要数据，包括总数、需求数、修复数和关闭提交数。

**方法名**：`get_summary`

**入参**：
- `project_id`: 项目 ID (str/int)
- `start_date`: 开始日期 (格式: YYYY-MM-DD)
- `end_date`: 结束日期 (格式: YYYY-MM-DD)

**返回**：
```json
{
  "total": 200,
  "requirements": 80,
  "fixes": 60,
  "closed": 60
}
```

### 2.2 获取 Commit 快照

**方法描述**：获取指定时间范围内所有 Commit 的详细信息快照。

**方法名**：`get_snapshot`

**入参**：
- `project_id`: 项目 ID (str/int)
- `start_date`: 开始日期 (格式: YYYY-MM-DD)
- `end_date`: 结束日期 (格式: YYYY-MM-DD)

**返回**：
```json
{
  "commits": [
    {
      "title": "提交标题",
      "project": "项目名",
      "iid": 456,
      "author_name": "作者名",
      "authored_date": "2025-01-15T10:30:00+8:00",
      "committed_date": "2025-01-15T10:35:00+8:00",
      "short_id": "abc1234",
      "rate": "high" // TODO
    }
  ]
}
```

### 2.3 按 Issue 统计 Commit

**方法描述**：根据 Issue IID 获取关联的所有 Commit 信息。

**方法名**：`get_commits_by_issue`

**入参**：
- `project_id`: 项目 ID (str/int)
- `issue_iid`: Issue IID (int)

**返回**：
```json
{
  "issue_iid": 123,
  "commits": [
    {
      "title": "提交标题",
      "project": "项目名",
      "author_name": "作者名",
      "authored_date": "2025-01-15T10:30:00Z",
      "committed_date": "2025-01-15T10:35:00Z"
    }
  ]
}
```

### 2.4 根据 Commit 更新 Issue

**方法描述**：根据 Commit 作者更新对应 Issue 的指派人和标签。如果前端完成添加 `front_finished` 标签，后端完成添加 `backend_finished` 标签。

**方法名**：`update_issue_by_commit`

**入参**：
- `project_id`: 项目 ID (str/int)
- `issue_iid`: Issue IID (int)
- `author_name`: Commit 作者用户名 (str)
- `is_frontend`: 是否为前端提交 (bool)
- `is_backend`: 是否为后端提交 (bool)

**返回**：
```json
{
  "success": true,
  "updated": {
    "issue_iid": 123,
    "assignees": ["作者名"],
    "added_labels": ["front_finished"]
  }
}
