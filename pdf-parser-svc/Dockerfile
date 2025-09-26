# 使用官方的 Python 运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

ENV PIP_INDEX_URL https://pypi.tuna.tsinghua.edu.cn/simple/
ENV PIP_TRUSTED_HOST pypi.tuna.tsinghua.edu.cn

# # 安装系统依赖（用于编译 cryptography 等包）
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libffi-dev \
#     && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 并安装 Python 依赖
# 为了效率，先复制并安装依赖，再复制代码
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到工作目录
COPY . .

# 暴露应用端口
EXPOSE 8188

# 定义环境变量文件（运行时需提供）
ENV ENV_FILE_PATH .env

# 运行应用
CMD ["python", "main.py"]
