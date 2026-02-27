# GitLab Task Scheduler - Docker 部署指南

本文档介绍如何使用 Docker 部署和运行 GitLab 定时任务调度器。

## 📋 前置要求

- Docker 已安装 (v20.10+)
- Docker Compose (可选，推荐)

## 🚀 快速开始

### 1. 准备配置文件

确保在项目根目录下有 `.env` 文件，包含以下必要配置：

```env
# GitLab 配置
GITLAB_BASE_URL=https://gitlab.stpass.com
GITLAB_PRIVATE_TOKEN=your_private_token_here

# 数据库配置 (可选，默认为 ./gitlab.db)
GITLAB_DB_PATH=./gitlab.db

# LLM 配置 (可选)
LLM_BASE_URL=http://localhost:11434
LLM_API_KEY=
LLM_MODEL=qwen2.5:7b
```

### 2. 构建 Docker 镜像

```bash
scp -r .\gitlab-new\* 13dev:~/gitlab/
cd gitlab-new
docker build -t gitlab-tasks:latest .
```

### 3. 运行容器

#### 运行方式

```bash
docker run -d \
  --name gitlab-tasks \
  --add-host=gitlab.stpass.com:192.168.110.18 \
  --env-file $(pwd)/.env \
  -v $(pwd)/gitlab.db:/app/gitlab.db \
  -e PROJECT_ID=4 \
  gitlab-tasks:latest \
  python task.py --mode scheduler --project-id 4
```

#### 挂载输出目录

如果需要持久化导出的 CSV 文件：

```bash
docker cp gitlab-tasks:/app/exports ./exports
```


#### 手动测试任务

```bash
docker exec gitlab-tasks python task.py --mode daily --project-id 4
```

#### 拉取数据库

```bash
scp 13dev:~/gitlab/gitlab.db gitlab.db
```


#### issue统计分析

```sql
-- 统计
SELECT 
    SUBSTRING(title, 1, 3) AS mode,
    COUNT(*) AS total_count, -- 总数
    SUM(CASE WHEN latest_status = '待开发' THEN 1 ELSE 0 END) AS 待开发, -- 待开发数量
    SUM(CASE WHEN latest_status = '开发中' THEN 1 ELSE 0 END) AS 开发中, -- 开发中数量
    SUM(CASE WHEN latest_status = '测试中' THEN 1 ELSE 0 END) AS 测试中 -- 开发中数量
FROM 
    issue_main 
WHERE
    latest_status in ('待开发','开发中','测试中') 
    AND milestone != 'BSMS α1.5 版发布' 
    AND milestone like 'BSMS%' 
    AND labels not like '%Bug::dev%' 
    AND mode not in ('CYL','LIM','App')
GROUP BY 
    SUBSTRING(title, 1, 3);

-- 详情
select * from issue_main where SUBSTRING(title, 1, 3) = 'DMM' and latest_status = '待开发' 
```


