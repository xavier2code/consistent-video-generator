# 多阶段构建
# 阶段1: 构建前端
FROM node:18-alpine AS frontend-builder

WORKDIR /app/web

# 复制package文件并安装依赖（利用Docker缓存）
COPY web/package*.json ./
RUN npm ci --only=production

# 复制源代码并构建
COPY web/ ./
RUN npm run build

# 阶段2: Python后端 + 前端静态文件
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（如果需要）
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 复制并安装Python依赖（利用Docker缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY main.py config.py ./
COPY api/ ./api/

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/web/dist ./web/dist

# 创建必要的目录
RUN mkdir -p uploads && \
    chmod 755 uploads

# 创建非root用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
