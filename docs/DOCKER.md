# Docker 部署指南

## 快速开始

### 生产环境

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建
docker-compose up -d --build
```

访问：http://localhost:8000

### 开发环境（支持热重载）

```bash
# 使用开发环境配置
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f

# 停止
docker-compose -f docker-compose.dev.yml down
```

## 环境变量配置

确保在项目根目录有 `.env` 文件：

```env
# DashScope配置（必需）
DASHSCOPE_API_KEY=your_api_key_here

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false
SERVER_URL=http://localhost:8000

# 视频生成默认配置
DEFAULT_PROMPT=写实风格，高质量视频，流畅的镜头运动
```

## Docker命令参考

### 查看容器状态
```bash
docker-compose ps
```

### 查看容器健康状态
```bash
docker inspect video-generator --format='{{.State.Health.Status}}'
```

### 进入容器
```bash
docker-compose exec app bash
```

### 清理所有容器和卷
```bash
docker-compose down -v
```

### 仅重启应用
```bash
docker-compose restart app
```

## 多阶段构建说明

Dockerfile使用多阶段构建优化镜像大小：

1. **阶段1 (frontend-builder)**: 
   - 使用 Node.js 构建前端
   - 生成优化的静态文件

2. **阶段2 (最终镜像)**:
   - 仅包含 Python 运行时
   - 复制前端构建产物
   - 安装Python依赖

## 安全特性

- ✅ 非root用户运行（appuser）
- ✅ 最小化基础镜像（slim）
- ✅ 健康检查
- ✅ 只暴露必要端口
- ✅ 使用 .dockerignore 减小构建上下文

## 持久化数据

上传的文件存储在 `./uploads` 目录，通过volume挂载：

```yaml
volumes:
  - ./uploads:/app/uploads
```

## 故障排查

### 容器无法启动
```bash
# 查看详细日志
docker-compose logs app

# 检查配置
docker-compose config
```

### API_KEY未配置
确保 `.env` 文件存在且包含 `DASHSCOPE_API_KEY`

### 端口冲突
如果8000端口被占用，修改 `docker-compose.yml`：
```yaml
ports:
  - "8080:8000"  # 改为其他端口
```

## 生产环境建议

1. **使用环境变量文件**
   ```bash
   # 创建生产环境配置
   cp .env.example .env.production
   # 编辑配置
   nano .env.production
   ```

2. **配置反向代理（Nginx）**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **启用HTTPS**
   使用 Let's Encrypt 或其他SSL证书

4. **监控和日志**
   - 配置日志收集
   - 设置容器资源限制
   - 启用自动重启

## 扩展配置

### 增加workers数量
编辑 `Dockerfile`：
```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 配置资源限制
编辑 `docker-compose.yml`：
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
```
