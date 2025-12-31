from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.generator import router as generator_router
import os

app = FastAPI(
    title="Consistent Video Generator API",
    description="后端API服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录，使上传的文件可通过HTTP访问
uploads_dir = "uploads"
videos_dir = "videos"
os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(videos_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/videos", StaticFiles(directory=videos_dir), name="videos")

# 注册API路由
app.include_router(generator_router, prefix="/api/v1")

# 生产环境：托管前端静态文件
frontend_dist = os.path.join("web", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

@app.get("/api")
async def root():
    return {
        "message": "欢迎使用 Consistent Video Generator API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
