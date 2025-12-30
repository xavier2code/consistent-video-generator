# 多阶段构建
# 阶段1: 构建前端
FROM node:18-alpine AS frontend-builder

WORKDIR /app/web
COPY web/package*.json ./
RUN npm install
COPY web/ ./
RUN npm run build

# 阶段2: Python后端 + 前端静态文件
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY main.py config.py ./
COPY api/ ./api/

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/web/dist ./web/dist

# 创建uploads目录
RUN mkdir -p uploads

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
