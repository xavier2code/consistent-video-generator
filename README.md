# Consistent Video Generator

一个基于 FastAPI + Vue3 的视频生成全栈应用。

## 项目结构

```
.
├── api/                    # 后端API模块
│   ├── __init__.py
│   └── generator.py        # 视频生成API
├── web/                    # 前端Vue3项目
│   ├── src/               # Vue源代码
│   ├── public/            # 静态资源
│   ├── package.json       # 前端依赖
│   └── vite.config.js     # Vite配置
├── uploads/               # 上传文件存储
├── venv/                  # Python虚拟环境
├── main.py               # FastAPI应用入口
├── config.py             # 配置管理
├── requirements.txt      # Python依赖
├── Dockerfile           # Docker镜像构建
├── docker-compose.yml   # Docker编排
└── start-dev.ps1        # 开发环境启动脚本

```

## 技术栈

### 后端
- **FastAPI** - 现代、快速的Python Web框架
- **DashScope** - 阿里云视频生成服务
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI服务器

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Vite** - 下一代前端构建工具

## 快速开始

### 开发环境

#### 方式1：使用自动启动脚本（推荐）

```powershell
.\start-dev.ps1
```

这将同时启动前端和后端服务：
- 前端地址: http://127.0.0.1:3000
- 后端地址: http://localhost:8000
- API文档: http://localhost:8000/docs

#### 方式2：手动启动

**后端：**
```powershell
# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 文件，设置 DASHSCOPE_API_KEY

# 启动后端
python main.py
```

**前端：**
```powershell
# 进入前端目录
cd web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 生产环境

#### 使用Docker（推荐）

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 手动部署

```powershell
# 1. 构建前端
cd web
npm install
npm run build
cd ..

# 2. 启动后端（会自动托管前端静态文件）
python main.py
```

访问 http://localhost:8000 即可使用应用。

## API 文档

启动服务后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 主要API端点

- `POST /api/v1/generate` - 上传图片生成视频
- `GET /api/v1/status/{task_id}` - 查询视频生成状态
- `GET /health` - 健康检查
- `GET /api` - API信息

## 配置说明

### 后端配置 (.env)

```env
# DashScope配置
DASHSCOPE_API_KEY=your_api_key_here

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true
SERVER_URL=http://localhost:8000
```

### 前端配置

开发环境和生产环境配置分别在：
- `web/.env.development`
- `web/.env.production`

## 开发指南

### 前端开发

前端项目已配置API代理，在开发环境下：
- 前端运行在 http://127.0.0.1:3000
- API请求会自动代理到后端 http://localhost:8000

### 后端开发

修改 `api/generator.py` 来添加或修改API逻辑。FastAPI会自动重载更改。

## 许可证

MIT
