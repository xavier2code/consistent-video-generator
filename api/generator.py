import os
from http import HTTPStatus
from dashscope import VideoSynthesis
import dashscope
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
from config import get_settings

router = APIRouter()

# 加载配置
settings = get_settings()

# 设置DashScope base URL
dashscope.base_http_api_url = settings.DASHSCOPE_BASE_URL

# 配置
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)


class VideoGenerateResponse(BaseModel):
    task_id: str
    status: str
    message: str = "任务已提交"


class VideoStatusResponse(BaseModel):
    task_id: str
    task_status: str
    message: Optional[str] = None
    video_url: Optional[str] = None
    code: Optional[str] = None


@router.post("/generate", response_model=VideoGenerateResponse, tags=["generator"])
async def generate_video(
    files: List[UploadFile] = File(...),
    prompt: Optional[str] = None
):
    """
    上传2个图片并生成视频（一步完成）
    
    参数：
    - files: 2个图片文件（第1个为首帧，第2个为末帧）
    - prompt: 视频生成提示词（可选，默认为空）
    
    其他参数使用默认值：
    - model: wan2.2-kf2v-flash
    - resolution: 720P
    - prompt_extend: True
    """
    if not settings.DASHSCOPE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="DASHSCOPE_API_KEY 未配置，请在 .env 文件中设置"
        )
    
    # 检查文件数量
    if len(files) != 2:
        raise HTTPException(
            status_code=400,
            detail=f"必须上传2个图片文件，当前上传了 {len(files)} 个"
        )
    
    uploaded_filenames = []
    
    # 上传并保存文件
    for idx, file in enumerate(files):
        try:
            # 检查文件扩展名
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件 {file.filename} 格式不支持。支持的格式: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            
            # 读取文件内容以检查大小
            contents = await file.read()
            file_size = len(contents)
            
            # 检查文件大小
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件 {file.filename} 大小 ({file_size / 1024 / 1024:.2f}MB) 超过限制 (10MB)"
                )
            
            # 生成唯一文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            safe_filename = f"{timestamp}_{unique_id}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, safe_filename)
            
            # 保存文件
            with open(file_path, "wb") as f:
                f.write(contents)
            
            uploaded_filenames.append(safe_filename)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"保存文件 {file.filename} 失败: {str(e)}"
            )
    
    # Use file:// URLs for local files
    first_frame_url = "file://" + os.path.abspath(os.path.join(UPLOAD_DIR, uploaded_filenames[0]))
    print(first_frame_url)
    last_frame_url = "file://" + os.path.abspath(os.path.join(UPLOAD_DIR, uploaded_filenames[1]))
    
    # 使用默认prompt（如果未提供）
    video_prompt = prompt if prompt else settings.DEFAULT_PROMPT
    
    try:
        # 异步调用视频生成API
        rsp = VideoSynthesis.async_call(
            api_key=settings.DASHSCOPE_API_KEY,
            model="wan2.2-kf2v-flash",
            prompt=video_prompt,
            first_frame_url=first_frame_url,
            last_frame_url=last_frame_url,
            resolution="720P",
            prompt_extend=True
        )
        
        if rsp.status_code == HTTPStatus.OK:
            # 删除本地文件
            try:
                for filename in uploaded_filenames:
                    file_path = os.path.join(UPLOAD_DIR, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except Exception as e:
                # 文件删除失败不影响返回结果，仅记录日志
                print(f"删除本地文件失败: {str(e)}")
            
            return VideoGenerateResponse(
                task_id=rsp.output.task_id,
                status="submitted",
                message=f"视频生成任务已提交，使用文件: {uploaded_filenames[0]}, {uploaded_filenames[1]}"
            )
        else:
            # 提交失败也删除本地文件
            try:
                for filename in uploaded_filenames:
                    file_path = os.path.join(UPLOAD_DIR, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except Exception:
                pass
            
            raise HTTPException(
                status_code=rsp.status_code,
                detail=f"任务提交失败: {rsp.message}"
            )
    
    except HTTPException:
        # HTTP异常也删除本地文件
        try:
            for filename in uploaded_filenames:
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception:
            pass
        raise
    except Exception as e:
        # 其他异常也删除本地文件
        try:
            for filename in uploaded_filenames:
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception:
            pass
        raise HTTPException(
            status_code=500,
            detail=f"调用视频生成API失败: {str(e)}"
        )


@router.get("/status/{task_id}", response_model=VideoStatusResponse, tags=["generator"])
async def get_status(task_id: str):
    """
    查询视频生成任务状态
    
    返回任务当前状态，不等待任务完成
    """
    if not settings.DASHSCOPE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="DASHSCOPE_API_KEY 未配置"
        )
    
    try:
        # 获取任务状态
        status = VideoSynthesis.fetch(
            task=task_id,
            api_key=settings.DASHSCOPE_API_KEY
        )
        
        if status.status_code == HTTPStatus.OK:
            response = VideoStatusResponse(
                task_id=task_id,
                task_status=status.output.task_status,
                message=f"任务状态: {status.output.task_status}"
            )
            
            # 如果任务完成，返回视频URL
            if hasattr(status.output, 'video_url') and status.output.video_url:
                response.video_url = status.output.video_url
            
            return response
        else:
            raise HTTPException(
                status_code=status.status_code,
                detail=f"查询任务状态失败: {status.message}"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"查询任务状态失败: {str(e)}"
        )


@router.get("/wait/{task_id}", response_model=VideoStatusResponse, tags=["generator"])
async def wait_completion(task_id: str):
    """
    等待视频生成任务完成
    
    此接口会阻塞直到任务完成或失败，可能需要较长时间
    """
    if not settings.DASHSCOPE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="DASHSCOPE_API_KEY 未配置"
        )
    
    try:
        # 等待任务完成
        rsp = VideoSynthesis.wait(
            task=task_id,
            api_key=settings.DASHSCOPE_API_KEY
        )
        
        if rsp.status_code == HTTPStatus.OK:
            return VideoStatusResponse(
                task_id=task_id,
                task_status=rsp.output.task_status,
                video_url=rsp.output.video_url if hasattr(rsp.output, 'video_url') else None,
                message="任务已完成"
            )
        else:
            raise HTTPException(
                status_code=rsp.status_code,
                detail=f"任务失败: {rsp.message}"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"等待任务完成失败: {str(e)}"
        )
