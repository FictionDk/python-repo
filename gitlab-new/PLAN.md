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

### 2.1 表结构
```sql
CREATE TABLE IF NOT EXISTS commits (
    id TEXT PRIMARY KEY,
    short_id TEXT,
    project_id INTEGER NOT NULL,
    project_name TEXT NOT NULL,
    group_name TEXT NOT NULL,
    title TEXT NOT NULL,
    author_name TEXT NOT NULL,
    authored_date TEXT,
    committed_date TEXT,
    message TEXT,
    operation TEXT DEFAULT '',
    issue_iid TEXT,  -- 支持多个 issue_iid，使用逗号分隔，例如: "123" 或 "123,456,789"
    rate_message TEXT DEFAULT 'normal',
    rate_count INTEGER DEFAULT 0,
    issue_synced INTEGER DEFAULT 0  -- 标记是否已同步更新issue: 0=未同步, 1=已同步
)
```

### 2.2.1 同步 Commit 
1. 方法描述：根据当前数据库最近同步时间，从远程获取最新数据更新到commits中
2. 方法名：clone_commit
3. 入参：project_id项目 ID

### 2.2.2 根据 Commit 更新 Issue（TODO）

1. 方法描述：根据 Commit 作者更新对应 Issue 的指派人和标签。如果前端完成添加 `front::finished` 标签，后端完成添加 `backend::finished` 标签，同时根据提交人信息，通过别名获取id，执行指派人更新；
2. 方法名：`sync_issue_by_commit`
3. 入参：无
4. 执行详情
  - a. 执行db/commit.py/get_commits_needing_sync获取列表
  - b. 实现类似get_summary的逻辑，将需要更新issue数据整理（一个issue一行，更新一次）
  - c. 执行issue模块的update_issue方法
  - d. 同步执行结果，将已更新的issue使用mark_issue_synced同步回数据库

### 2.3 数据库方法

#### 2.3.1 mark_issue_synced
- **方法描述**: 批量标记commit的issue同步状态为已完成
- **入参**: `commit_ids` - commit ID列表
- **返回**: 被标记的commit数量
- **用途**: 在成功更新issue后调用，避免重复同步

#### 2.3.2 get_commits_needing_sync
- **方法描述**: 获取需要同步的commit列表
- **入参**:
  - `project_id` (可选): 项目ID
  - `start_date` (可选): 开始日期 (YYYY-MM-DD)
  - `end_date` (可选): 结束日期 (YYYY-MM-DD)
- **返回**: commit对象列表
- **过滤条件**: 
  - `issue_synced = 0` (未同步)
  - `issue_iid IS NOT NULL AND issue_iid != ''` (存在关联issue)


## 三、Member/User管理

### 3.1 表结构
```sql
CREATE TABLE IF NOT EXISTS users (
    id PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    name TEXT,
    state TEXT,
    locked BOOLEAN,
    avatar_url TEXT,
    web_url TEXT,
    alias TEXT, -- git commit中的别称,如果存在多个用逗号分割
    updated_at TEXT
)
```

### 3.2 方法

#### 3.2.1 同步 Member
1. 从client中获取当前组内所有用户，并插入或更新users表中
2. 方法名：`update_issue_by_commit`

#### 3.2.2 更新 alias
1. 用户手工更新alias到users，入参,key是users的username,value是别名
  ```json
  {
    "hek": "He Kui, Hek"
  }
  ```
2. 方法名：`update_alias`
