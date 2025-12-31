# Consistent Video Generator

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.0+-42b883.svg)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0+-646cff.svg)](https://vitejs.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-green.svg)](https://ffmpeg.org/)

一个基于 FastAPI + Vue3 的视频生成全栈应用，使用阿里云DashScope API生成AI视频。

## ✨ 功能特性

- �️ **序列视频生成** - 上传2-6张图片，自动生成并合并成完整视频
- 🤖 集成阿里云DashScope视频生成API（wan2.2-kf2v-flash模型）
- 📊 实时状态查询和自动轮询
- 🎥 视频在线预览和下载
- 🎨 现代化UI设计（Vue 3 + 渐变背景）
- 📱 响应式布局，支持移动端
- 🐳 完整的Docker部署支持
- 🔄 开发环境热重载

## 📁 项目结构

```
.
├── api/                      # 后端API模块
│   ├── __init__.py
│   └── generator.py          # 视频生成API（3个接口）
├── web/                      # 前端Vue3项目
│   ├── src/
│   │   ├── api/             # API服务层
│   │   ├── components/      # Vue组件
│   │   ├── App.vue          # 主应用
│  🛠️ 技术栈

### 后端
- **FastAPI** - 现代、快速的Python Web框架
- **DashScope SDK** - 阿里云视频生成服务
- **Pydantic** - 数据验证和配置管理
- **httpx** - 异步HTTP客户端
- **ffmpeg-python** - 视频处理和合并

### 前端
- **Vue 3** - 渐进式JavaScript框架（Composition API）
- **Vite** - 下一代前端构建工具
- **原生Fetch API** - HTTP请求

### 部署
- **Docker** - 容器化部署（多阶段构建）
- **Docker Compose** - 容器编排
- **FFmpeg** - 视频处理工具
- **Docker Compose** - 容器编排.yml  # 开发环境Docker配置
├── DOCKER.md               # Docker详细文档
└── start-dev.ps1           # 本地开发启动脚本

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

# 查
docs/DOCKER.md](docs/
访问 http://localhost:8000

> 📖 查看 [DOCKER.md](DOCKER.md) 获取完整的Docker部署文档，包括开发环境配置、故障排查等。看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

#### 手动部署

```powershell
# 1. 构建前端
cd web
npm install
npm📡 API 文档

启动服务后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要API端点

| 方法 | 端点 | 说明 |
|------|------|------|
| `POST` | `/api/v1/generate-sequence` | 上传2-6张图片生成序列视频并合并 |
| `GET` | `/api/v1/status/{task_id}` | 查询视频生成任务状态（不等待） |
| `GET` | `/api/v1/wait/{task_id}` | 等待视频生成完成（阻塞） |
| `GET` | `/health` | 健康检查 |
| `GET` | `/api` | API基本信息 |

### API使用示例

**生⚙️ 配置说明

### 环境变量 (.env)

创建 `.env` 文件（复制 `.env.example`）：

```env
# DashScope配置（必需）
DASHSCOPE_API_KEY=your_api_key_here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/api/v1

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true
SERVER_URL=http://localhost:8000

# 视频生成默认配置
DEFAULT_PROMPT=写实风格，高质量视频，流畅的镜头运动
```

### 前端环境配置

开发和生产环境配置：
- `web/.env.development` - 开发环境
- `web/.env.production` - 生产环境

## 🔧 开发指南

### 前端开发

前端项目已配置API代理，在开发环境下：
- 前端地址: http://127.0.0.1:3000
- API代理: `/api` → `http://localhost:8000/api`
- 上传代理: `/uploads` → `http://localhost:8000/uploads`

修改 `web/src/components/VideoGenerator.vue` 来定制UI和功能。

### 后端开发

修改 `api/generator.py` 来添加或修改API逻辑。

**热重载：** FastAPI在DEBUG模式下支持自动重载。

### Docker开发环境

使用开发环境配置支持代码热重载：

```bash
docker-compose -f docker-compose.dev.yml up -d
```

## 📂 文件上传限制

- **支持格式**: JPG, JPEG, PNG, GIF, BMP, WEBP
- **最大文件大小**: 10MB
- **文件数量**: 2-6张图片（按时间顺序上传）

## 🔍 视频生成流程

1. 用户按时间顺序上传2-6张图片
2. 后端根据图片数量生成 n-1 个视频片段
   - 例如：4张图片 → 3个视频（图1→图2, 图2→图3, 图3→图4）
3. 等待所有视频生成完成并下载
4. 使用FFmpeg合并所有视频片段（单视频则跳过）
5. 返回合并后的完整视频URL

**处理时间参考：**
- 2张图片：约30秒-2分钟（1个视频，无需合并）
- 3张图片：约1-4分钟（2个视频 + 合并）
- 4张图片：约2-6分钟（3个视频 + 合并）
- 5张图片：约3-8分钟（4个视频 + 合并）
- 6张图片：约5-15分钟（5个视频 + 合并）

## 🐛 故障排查

### 前端无法连接后端
- 检查后端是否运行在 http://localhost:8000
- 查看浏览器控制台的错误信息
- 确认Vite代理配置正确

### API_KEY未配置
```bash
DASHSCOPE_API_KEY 未配置，请在 .env 文件中设置
```
解决：在 `.env` 文件中添加有效的API密钥

### FFmpeg未安装（序列视频功能需要）
```bash
# Windows (使用Chocolatey)
choco install ffmpeg

# 或下载并添加到PATH
# https://ffmpeg.org/download.html

# Linux
sudo apt-get install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg      # CentOS/RHEL

# macOS
brew install ffmpeg
```

### 序列视频生成失败
- 确保已安装FFmpeg并添加到系统PATH
- 检查磁盘空间是否充足（每个视频约10-30MB）
- 确认图片按正确顺序上传
- 查看后端日志了解详细错误信息

### Docker容器无法启动
```bashDOCKER.md) 的故障排查部分。

## 📚 相关文档

- [Docker部署指南](docs/DOCKER.md) - 完整的Docker部署文档
- [FastAPI文档](https://fastapi.tiangolo.com/) - FastAPI官方文档
- [Vue 3文档](https://vuejs.org/) - Vue.js官方文档
- [DashScope文档](https://help.aliyun.com/document_detail/2712520.html) - 阿里云视频生成API
- [FFmpeg文档](https://ffmpeg.org/documentation.html) - FFmpeg官方文档

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！端运行在 http://127.0.0.1:3000
- API请求会自动代理到后端 http://localhost:8000

### 后端开发

修改 `api/generator.py` 来添加或修改API逻辑。FastAPI会自动重载更改。

## 许可证

MIT
