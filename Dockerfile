FROM python:3.12-slim

# 只安装必要依赖（不更换系统源）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    default-mysql-client \
    redis-tools \
    libaio1 \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*


# 设置工作目录
WORKDIR /case_auto_hub

# 复制依赖文件
COPY requirements.txt .

#RUN pip install --upgrade pip

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/


# 复制项目文件
COPY . .

RUN chmod +x wait-for.sh

# 暴露端口
EXPOSE 5050

CMD ["./wait-for.sh", "gunicorn", "-c", "gunicorn_config.py", "main:hub"]