# 第一阶段：构建环境（保持不变）
FROM python:3.12-slim-bullseye as builder
WORKDIR /app
# 使用阿里云Debian镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libmagic-dev && \
    pip install --upgrade pip && \
    #pip install --user --no-warn-script-location pydantic-core && \
    #pip install pydantic-core==2.16.3 && \
    pip install --user --no-warn-script-location --no-deps -r requirements.txt && \
    #pip install --user --no-warn-script-location -r requirements.txt && \
    apt-get remove -y gcc python3-dev libmagic-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /root/.cache/pip  # 新增缓存清理

# 第二阶段：运行时环境（关键修复）
FROM python:3.12-slim-bullseye
WORKDIR /app

# 创建系统用户和组（修复用户不存在问题）
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    mkdir -p /app/{logs,screenshots/errors} && \
    chown -R appuser:appuser /app

# 使用阿里云Debian镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libmagic1 \
        ca-certificates \
        tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# 关键修复：复制包到全局路径（/usr/local）而非 /root
COPY --from=builder /root/.local /usr/local
COPY --chown=appuser:appuser . .

# 设置全局PATH
ENV PATH=/usr/local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PLAYWRIGHT_BROWSERS_PATH=/home/appuser/.cache/ms-playwright

RUN mkdir -p ${PLAYWRIGHT_BROWSERS_PATH} && \
    chmod -R 777 ${PLAYWRIGHT_BROWSERS_PATH} && \
    playwright install --with-deps chromium
# 深度缓存清理（优化镜像体积）
RUN find / -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true && \
    rm -rf /tmp/* /var/tmp/*

# 暴露端口
EXPOSE 5050
USER appuser
# 启动命令
CMD ["uvicorn", "main:hub", "--host", "0.0.0.0", "--port", "5050"]