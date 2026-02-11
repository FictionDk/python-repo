## Issue管理 manage_issue.py

### 1. 获取 Issue 快照

**方法描述**：获取指定时间点项目 Issue 的详细信息快照，并存入本地sqlite数据库

**方法名**：`clone_snapshot`

**入参**：
- `project_id`: 项目 ID (str/int)
- `start_date`: 开始日期 (格式: YYYY-MM-DD)

**返回**：
```json
{
  "issues": [
    {
      "title": "Issue 标题",
      "iid": 123,
      "assignees": ["用户名1", "用户名2"],
      "status": "opened",
      "labels": ["标签1", "标签2"]
    }
  ]
}
```

### 2. 获取 Issue 概要

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

### 3. 更新 Issue

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

### 4. Issue 存储结构
1. Issue-Main表，主键为iid，如果存在就更新，不存在则插入
2. Issue-Snapshot，主键为自增id，iid和shapshot_at联合唯一，字段为 status，使用graphql_request请求获取的main_status


## Commit管理 manage_commit.py

### 1. 获取 Commit 概要

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

---

### 2. 获取 Commit 快照

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

---

### 3. 按 Issue 统计 Commit

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

### 4. 根据 Commit 更新 Issue

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
