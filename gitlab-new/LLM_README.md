# LLM管理模块

## 概述

LLM管理模块提供了与本地大语言模型交互的功能，包括API调用、请求历史记录管理等。

## 功能特性

1. **数据库存储** - 存储所有LLM请求和响应历史
2. **API客户端** - 使用OpenAI兼容格式调用本地LLM服务
3. **内容过滤** - 自动移除响应中的thinking内容
4. **配置管理** - 支持环境变量配置

## 配置

### 环境变量

在 `.env` 文件中添加以下配置：

```env
# LLM配置
LLM_BASE_URL=http://localhost:11434
LLM_API_KEY=your_api_key_if_needed
LLM_MODEL=qwen2.5:7b
```

### 默认配置

- `LLM_BASE_URL`: http://localhost:11434 (Ollama默认地址)
- `LLM_API_KEY`:空 (可选)
- `LLM_MODEL`: qwen2.5:7b

## 数据库表结构

```sql
CREATE TABLE llm_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,           -- 类别: 日汇总、周汇总、提交评价
    create_at TEXT NOT NULL,      -- 汇总时间
    req_content TEXT NOT NULL,    -- 提交的内容
    resp_content TEXT NOT NULL,   -- llm响应内容（已剔除thinking）
    sucess BOOLEAN               -- 请求是否成功
)
```

## 使用方法

### 1. 初始化数据库

```python
from db.database import get_database

db = get_database()
# 数据库会自动创建 llm_history 表
```

### 2. 使用LLM客户端

```python
from api.llm_client import LLMClient
from datetime import datetime

# 初始化客户端
client = LLMClient()

# 检查服务健康状态
is_healthy = client.health_check()
print(f"Service healthy: {is_healthy}")

# 生成响应并保存到数据库
create_at = datetime.now().isoformat()
response, success = client.generate_response(
    type="日汇总",
    req_content="请生成今日工作汇总",
    create_at=create_at,
    db_instance=db
)

print(f"Response: {response}")
print(f"Success: {success}")
```

### 3. 查询历史记录

```python
from db.database import get_database

db = get_database()

# 查询最近10条记录
records = db.get_llm_history(limit=10)

# 查询特定类型的记录
daily_summaries = db.get_llm_history(type_filter="日汇总", limit=5)

# 显示记录
for row in records:
    print(f"ID: {row['id']}")
    print(f"Type: {row['type']}")
    print(f"Success: {row['sucess']}")
    print(f"Response: {row['resp_content'][:100]}...")
```

### 4. 直接数据库操作

```python
from db.database import get_database

db = get_database()

# 插入新记录
record_id = db.insert_llm_history(
    type="测试",
    create_at="2026-02-13T17:00:00",
    req_content="测试内容"
)

# 更新响应
success = db.update_response(
    record_id=record_id,
    resp_content="响应内容",
    success=True
)
```

## API端点

LLM客户端使用OpenAI兼容的API格式：

- **端点**: `{base_url}/v1/chat/completions`
- **方法**: POST
- **认证**: Bearer Token (如果配置了API key)

## 支持的LLM服务

支持任何提供OpenAI兼容API的本地LLM服务，包括：

- Ollama
- LocalAI
- vLLM
- 其他兼容服务

## 测试

运行验证脚本：

```bash
python gitlab-new/verify_llm.py
```

运行测试套件：

```bash
python gitlab-new/test_llm.py
```

## 注意事项

1. **Thinking内容移除**: 响应中 `<thinking>...</thinking>` 标签内的内容会被自动移除
2. **错误处理**: 所有失败的请求都会记录在数据库中，success字段标记为False
3. **日期格式**: create_at字段使用ISO 8601格式
4. **超时设置**: API请求默认超时60秒

## 文件结构

```
gitlab-new/
├── api/
│   ├── __init__.py          # 导出LLMClient
│   └── llm_client.py        # LLM客户端实现
├── db/
│   ├── llm_history.py       # LLM历史表混入类
│   └── models.py            # 数据库模型
├── config.py                # 配置管理（已更新LLM配置）
├── test_llm.py             # 测试脚本
└── verify_llm.py           # 验证脚本
```

## 示例场景

### 场景1: 生成日报汇总

```python
from api.llm_client import LLMClient
from db.database import get_database
from datetime import datetime

client = LLMClient()
db = get_database()

prompt = """
今日完成的工作：
1. 完成了用户认证模块
2. 修复了3个bug
3. 代码审查5个PR

请生成日报汇总
"""

response, success = client.generate_response(
    type="日汇总",
    req_content=prompt,
    create_at=datetime.now().isoformat(),
    db_instance=db
)
```

### 场景2: 提交评价

```python
prompt = f"""
提交信息: {commit_message}
作者: {author_name}
提交时间: {commit_date}

请评价这个代码提交
"""

response, success = client.generate_response(
    type="提交评价",
    req_content=prompt,
    create_at=commit_date,
    db_instance=db
)
```

## 后续扩展

可以基于此模块扩展以下功能：

1. 流式响应支持
2. 批量请求处理
3. 响应缓存机制
4. 多轮对话历史
5. 统计分析功能
