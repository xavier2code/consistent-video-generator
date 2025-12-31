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
DEFAULT_PROMPT=同一人物在不同时期的平滑过渡，保持面部特征一致性，背景自然变化，光影真实，色彩丰富，高质量视频。

# 序列视频配置
# 支持2-6张图片，n张图片生成n-1个视频片段
# 视频合并需要FFmpeg支持
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
   - 使用 Node.js 18 Alpine 构建前端
   - 生成优化的静态文件（Vue 3 + Vite）
   - 仅复制必要的构建产物

2. **阶段2 (最终镜像)**:
   - 基于 Python 3.10 slim 镜像
   - 安装系统依赖（curl + FFmpeg）
   - 复制前端构建产物
   - 安装Python依赖（FastAPI, DashScope等）
   - 配置非root用户运行

### 关键依赖

- **FFmpeg**: 用于序列视频合并功能
  - 容器内已自动安装
  - 支持2-6张图片生成并合并视频
- **httpx**: 异步HTTP客户端，用于下载生成的视频
- **ffmpeg-python**: Python FFmpeg绑定

## 安全特性

- ✅ 非root用户运行（appuser）
- ✅ 最小化基础镜像（slim）
- ✅ 健康检查
- ✅ 只暴露必要端口
- ✅ 使用 .dockerignore 减小构建上下文

## 持久化数据

项目使用volume挂载持久化数据：

### 上传文件目录
```yaml
volumes:
  - ./uploads:/app/uploads  # 用户上传的图片
```

### 生成视频目录
```yaml
volumes:
  - ./videos:/app/videos    # 生成并合并的视频文件
```

**存储说明：**
- `uploads/`: 临时存储上传的图片（生成后自动清理）
- `videos/`: 持久化存储合并后的视频文件
- 单个视频文件约10-30MB（取决于分辨率和长度）
- 建议定期清理`videos/`目录以节省空间

## 故障排查

### 容器无法启动
```bash
# 查看详细日志
docker-compose logs app

# 检查配置
docker-compose config

# 验证FFmpeg安装
docker-compose exec app ffmpeg -version
```

### API_KEY未配置
确保 `.env` 文件存在且包含 `DASHSCOPE_API_KEY`

```bash
# 检查环境变量
docker-compose exec app printenv | grep DASHSCOPE
```

### 端口冲突
如果8000端口被占用，修改 `docker-compose.yml`：
```yaml
ports:
  - "8080:8000"  # 改为其他端口
```

### 序列视频生成失败

**症状**: 视频合并失败或超时

**可能原因**:
1. FFmpeg未正确安装
   ```bash
   docker-compose exec app which ffmpeg
   ```

2. 磁盘空间不足
   ```bash
   docker-compose exec app df -h
   ```

3. 内存不足（多视频并发生成）
   - 增加Docker内存限制
   - 减少并发请求

4. 网络问题（下载视频超时）
   - 检查与DashScope API的连接
   - 增加下载超时时间

**解决方案**:
```bash
# 重新构建镜像确保FFmpeg安装
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 检查videos目录权限
ls -la videos/
chmod 755 videos/
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
       
       # 增加上传大小限制（支持多图片上传）
       client_max_body_size 100M;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           
           # 增加超时时间（序列视频生成可能需要10-15分钟）
           proxy_read_timeout 900s;
           proxy_connect_timeout 900s;
           proxy_send_timeout 900s;
       }
       
       # 静态文件缓存
       location /uploads/ {
           alias /path/to/uploads/;
           expires 7d;
       }
       
       location /videos/ {
           alias /path/to/videos/;
           expires 30d;
       }
   }
   ```

3. **启用HTTPS**
   使用 Let's Encrypt 或其他SSL证书

4. **监控和日志**
   - 配置日志收集
   - 设置容器资源限制
   - 启用自动重启
   - 监控磁盘空间（videos目录增长）

5. **定期清理**
   ```bash
   # 创建清理脚本（删除7天前的视频）
   find ./videos -name "*.mp4" -mtime +7 -delete
   
   # 添加到crontab
   0 2 * * * /path/to/cleanup-videos.sh
   ```

## 扩展配置

### 增加workers数量
编辑 `Dockerfile`：
```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**注意**: 序列视频生成是I/O密集型任务，增加workers可能帮助不大，建议使用异步处理。

### 配置资源限制
编辑 `docker-compose.yml`：
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G  # 序列视频需要更多内存
        reservations:
          cpus: '1'
          memory: 1G
```

### 优化视频存储

**使用对象存储**（推荐生产环境）：
```python
# 配置AWS S3或阿里云OSS
# 自动上传生成的视频到云存储
# 节省本地磁盘空间
```

**设置视频过期策略**：
```yaml
# docker-compose.yml
volumes:
  - ./videos:/app/videos
  
# 配合定时任务清理旧文件
```

### 性能优化建议

1. **并发限制**: 限制同时处理的视频生成任务
2. **队列系统**: 使用Celery或RQ处理长时间任务
3. **缓存策略**: 相同图片组合可复用视频
4. **CDN加速**: 视频文件通过CDN分发
5. **异步处理**: 使用WebSocket推送生成进度
