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

#### 基本运行方式

```bash
docker run -d \
  --name gitlab-tasks \
  --add-host=gitlab.stpass.com:192.168.110.18 \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/gitlab.db:/app/gitlab.db \
  gitlab-tasks:latest
```

#### 带项目 ID 的运行方式

如果需要运行 `clone_snapshot` 任务，需要指定项目 ID：

```bash
docker run -d \
  --name gitlab-tasks \
  --add-host=gitlab.stpass.com:192.168.110.18 \
  -v $(pwd)/.env:/app/.env:ro \
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

## 📝 运行模式说明

### 模式 1: 持续调度模式 (默认)

容器将持续运行，在指定时间自动执行任务：

- 每天 01:00 执行: `clone_all_commit`, `sync_issue_by_commit`, `clone_snapshot`
- 每周一 04:00 执行: `analyze_development_progress`

```bash
docker run -d \
  --name gitlab-tasks \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/gitlab.db:/app/gitlab.db \
  gitlab-tasks:latest
```

### 模式 2: 单次执行日常任务

执行一次日常任务后容器退出：

```bash
docker run --rm \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/gitlab.db:/app/gitlab.db \
  gitlab-tasks:latest \
  python task.py --mode daily --project-id 4
```

### 模式 3: 单次执行周报任务

执行一次周报生成任务后容器退出：

```bash
docker run --rm \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/gitlab.db:/app/gitlab.db \
  gitlab-tasks:latest \
  python task.py --mode weekly
```

## 🔧 容器管理命令

### 查看容器日志

```bash
# 实时查看日志
docker logs -f gitlab-tasks

# 查看最近 100 行日志
docker logs --tail 100 gitlab-tasks

# 查看容器所有日志
docker logs gitlab-tasks
```

### 停止容器

```bash
docker stop gitlab-tasks
```

### 启动已停止的容器

```bash
docker start gitlab-tasks
```

### 重启容器

```bash
docker restart gitlab-tasks
```

### 删除容器

```bash
# 停止并删除容器
docker stop gitlab-tasks
docker rm gitlab-tasks

# 强制删除运行中的容器
docker rm -f gitlab-tasks
```

### 查看容器状态

```bash
docker ps -a | grep gitlab-tasks
```

### 进入容器调试

```bash
docker exec -it gitlab-tasks /bin/bash
```

## 🎯 定时任务说明

### 日常任务 (每天 01:00)

1. **clone_all_commit** - 从 GitLab 拉取所有项目的新提交到数据库
2. **sync_issue_by_commit** - 根据提交信息更新 Issue 的指派人和标签
3. **clone_snapshot** - 创建 Issue 快照并保存到数据库（需要 project_id）

### 周报任务 (每周一 04:00)

1. **analyze_development_progress** - 分析本周开发进度并生成报告

## ⚙️ 高级配置

### 使用 Docker Compose (推荐)

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  gitlab-tasks:
    build: .
    container_name: gitlab-tasks
    restart: unless-stopped
    volumes:
      - ./.env:/app/.env:ro
      - ./gitlab.db:/app/gitlab.db
      - ./exports:/app/exports
    environment:
      - TZ=Asia/Shanghai
      - PROJECT_ID=4  # 可选，用于 clone_snapshot 任务
    command: python task.py --mode scheduler --project-id 4
```

启动服务：

```bash
# 启动
docker-compose up -d

# 停止
docker-compose down

# 查看日志
docker-compose logs -f

# 重启
docker-compose restart
```

### 自定义时区

容器默认时区为 `Asia/Shanghai`，如需修改：

```bash
docker run -d \
  --name gitlab-tasks \
  -e TZ=America/New_York \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/gitlab.db:/app/gitlab.db \
  gitlab-tasks:latest
```

### 资源限制

限制容器资源使用：

```bash
docker run -d \
  --name gitlab-tasks \
  --memory="512m" \
  --cpus="1.0" \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/gitlab.db:/app/gitlab.db \
  gitlab-tasks:latest
```

## 🐛 故障排查

### 问题 1: 容器启动失败

检查日志：

```bash
docker logs gitlab-tasks
```

常见原因：
- `.env` 文件未正确配置
- `GITLAB_PRIVATE_TOKEN` 无效
- 数据库文件权限问题

### 问题 2: 任务未按预期执行

1. 检查容器时区设置

```bash
docker exec gitlab-tasks date
```

2. 查看任务调度日志

```bash
docker logs gitlab-tasks | grep "Scheduled"
```

3. 手动测试任务

```bash
docker exec gitlab-tasks python task.py --mode daily
```

### 问题 3: 数据库文件权限问题

确保数据库文件有正确的读写权限：

```bash
chmod 666 gitlab.db
```

或者在 Docker 命令中指定用户：

```bash
docker run -d \
  --name gitlab-tasks \
  -u $(id -u):$(id -g) \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/gitlab.db:/app/gitlab.db \
  gitlab-tasks:latest
```

## 📊 监控和日志

### 导出日志到文件

```bash
docker logs gitlab-tasks > gitlab-tasks.log 2>&1
```

### 使用日志驱动

配置日志轮转：

```bash
docker run -d \
  --name gitlab-tasks \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/gitlab.db:/app/gitlab.db \
  gitlab-tasks:latest
```

## 🔐 安全建议

1. **不要在 Dockerfile 中包含敏感信息** - 使用 .env 文件和环境变量
2. **限制容器权限** - 使用非 root 用户运行
3. **定期更新基础镜像** - `docker pull python:3.9.4-slim`
4. **使用只读卷** - 对 .env 文件使用 `:ro` 标志
5. **网络隔离** - 在生产环境中考虑使用 Docker 网络

## 📦 镜像优化

### 多阶段构建 (可选)

如果需要更小的镜像尺寸，可以使用多阶段构建：

```dockerfile
FROM python:3.9.4-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.9.4-slim

WORKDIR /app
ENV PATH="/root/.local/bin:$PATH"
TZ=Asia/Shanghai

COPY --from=builder /root/.local /root/.local
COPY . .

CMD ["python", "task.py", "--mode", "scheduler"]
```

## 🔗 相关链接

- [Docker 官方文档](https://docs.docker.com/)
- [Python 镜像](https://hub.docker.com/_/python)
- [项目 README](README.md)
- [任务调度说明](task.py)



