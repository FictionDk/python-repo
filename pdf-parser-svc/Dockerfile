# 使用官方的 Python 运行时作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

RUN \
    # 删除默认源
    rm -f /etc/apt/sources.list.d/debian.sources && \
    \
    # 写入主源：trixie, trixie-updates, trixie-backports
    printf 'Types: deb\nURIs: https://mirrors.tuna.tsinghua.edu.cn/debian\nSuites: trixie trixie-updates trixie-backports\nComponents: main contrib non-free non-free-firmware\nSigned-By: /usr/share/keyrings/debian-archive-keyring.gpg\n' \
        > /etc/apt/sources.list.d/tuna-main.sources && \
    \
    # 写入安全源：trixie-security
    printf 'Types: deb\nURIs: https://mirrors.tuna.tsinghua.edu.cn/debian-security\nSuites: trixie-security\nComponents: main contrib non-free non-free-firmware\nSigned-By: /usr/share/keyrings/debian-archive-keyring.gpg\n' \
        > /etc/apt/sources.list.d/tuna-security.sources && \
    \
    # 更新并安装依赖
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        poppler-utils \
    && \
    rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 并安装 Python 依赖
# 为了效率，先复制并安装依赖，再复制代码
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到工作目录
COPY . .

# 暴露应用端口
EXPOSE 8188

# 运行应用
CMD ["python", "main.py"]
