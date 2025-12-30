# Consistent Video Generator API

一个基于 FastAPI 的后端 API 服务。

## 功能特性

- RESTful API 设计
- 自动生成的 API 文档（Swagger UI）
- CORS 支持
- 数据验证（Pydantic）

## 安装

1. 激活虚拟环境：
```bash
.\venv\Scripts\Activate.ps1
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
copy .env.example .env
```

## 运行

启动开发服务器：
```bash
python main.py
```

或使用 uvicorn：
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

- `GET /` - 根路径，返回欢迎信息
- `GET /health` - 健康检查
- `GET /api/v1/items` - 获取所有项目
- `GET /api/v1/items/{item_id}` - 获取单个项目
- `POST /api/v1/items` - 创建新项目
- `PUT /api/v1/items/{item_id}` - 更新项目
- `DELETE /api/v1/items/{item_id}` - 删除项目

## 项目结构

```
.
├── main.py              # 主应用入口
├── requirements.txt     # 项目依赖
├── .env.example        # 环境变量示例
├── .gitignore          # Git 忽略文件
├── api/                # API 路由模块
│   ├── __init__.py
│   └── routes.py       # API 路由定义
└── venv/               # 虚拟环境
```

## 开发

根据需要修改 `api/routes.py` 来添加你的业务逻辑和 API 端点。
