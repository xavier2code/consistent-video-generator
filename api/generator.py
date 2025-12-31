import os
from http import HTTPStatus
from dashscope import VideoSynthesis
import dashscope
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
from config import get_settings
import httpx
import asyncio
import ffmpeg

router = APIRouter()

# 加载配置
settings = get_settings()

# 设置DashScope base URL
dashscope.base_http_api_url = settings.DASHSCOPE_BASE_URL

# 配置
UPLOAD_DIR = "uploads"
VIDEO_DIR = "videos"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


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


class VideoSequenceResponse(BaseModel):
    task_id: str
    status: str
    message: str
    total_videos: int
    processed_videos: int = 0
    merged_video_url: Optional[str] = None


# 辅助函数：下载视频
async def download_video(url: str, save_path: str) -> bool:
    """下载视频到本地"""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            return True
    except Exception as e:
        print(f"下载视频失败: {str(e)}")
        return False


# 辅助函数：合并视频
def merge_videos(video_files: List[str], output_path: str) -> bool:
    """使用ffmpeg合并多个视频"""
    try:
        # 创建一个临时文件列表
        list_file = output_path.replace('.mp4', '_list.txt')
        
        with open(list_file, 'w', encoding='utf-8') as f:
            for video_file in video_files:
                # 使用绝对路径并转义
                abs_path = os.path.abspath(video_file).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")
        
        # 使用ffmpeg合并视频
        (
            ffmpeg
            .input(list_file, format='concat', safe=0)
            .output(output_path, c='copy')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        # 删除临时文件列表
        if os.path.exists(list_file):
            os.remove(list_file)
        
        return True
    except Exception as e:
        print(f"合并视频失败: {str(e)}")
        return False


# 辅助函数：等待任务完成并获取视频URL
async def wait_for_video(task_id: str) -> Optional[str]:
    """等待视频生成完成并返回URL"""
    max_retries = 180  # 最多等待6分钟（每2秒检查一次）
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            status = VideoSynthesis.fetch(
                task=task_id,
                api_key=settings.DASHSCOPE_API_KEY
            )
            
            if status.status_code == HTTPStatus.OK:
                task_status = status.output.task_status
                
                if task_status == 'SUCCEEDED':
                    if hasattr(status.output, 'video_url'):
                        return status.output.video_url
                    else:
                        print(f"任务 {task_id} 完成但未返回视频URL")
                        return None
                elif task_status == 'FAILED':
                    print(f"任务 {task_id} 失败")
                    return None
                # PENDING 或 RUNNING 状态继续等待
            
            await asyncio.sleep(2)
            retry_count += 1
        except Exception as e:
            print(f"查询任务 {task_id} 状态失败: {str(e)}")
            await asyncio.sleep(2)
            retry_count += 1
    
    print(f"任务 {task_id} 超时")
    return None


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
            negative_prompt="低质量, 模糊, 畸形, 变形, 多余的肢体, 错误的解剖结构, 脸部缺陷, 文字, 水印。",
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


@router.post("/generate-sequence", response_model=VideoSequenceResponse, tags=["generator"])
async def generate_video_sequence(
    files: List[UploadFile] = File(...),
    prompt: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """
    上传6张图片生成序列视频（自动合并）
    
    参数：
    - files: 6张图片文件（按顺序）
    - prompt: 视频生成提示词（可选）
    
    流程：
    1. 生成5个视频片段（图片1-2, 2-3, 3-4, 4-5, 5-6）
    2. 下载所有视频片段
    3. 合并成一个完整视频
    4. 返回合并后的视频URL
    """
    if not settings.DASHSCOPE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="DASHSCOPE_API_KEY 未配置，请在 .env 文件中设置"
        )
    
    # 检查文件数量
    if len(files) != 6:
        raise HTTPException(
            status_code=400,
            detail=f"必须上传6张图片文件，当前上传了 {len(files)} 个"
        )
    
    uploaded_filenames = []
    
    # 上传并保存所有文件
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
            safe_filename = f"{timestamp}_{unique_id}_{idx}{file_ext}"
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
    
    # 使用默认prompt（如果未提供）
    video_prompt = prompt if prompt else settings.DEFAULT_PROMPT
    
    # 生成任务ID
    sequence_task_id = f"seq_{uuid.uuid4().hex[:16]}"
    
    try:
        # 生成5个视频片段
        task_ids = []
        
        for i in range(5):
            first_frame_url = "file://" + os.path.abspath(os.path.join(UPLOAD_DIR, uploaded_filenames[i]))
            last_frame_url = "file://" + os.path.abspath(os.path.join(UPLOAD_DIR, uploaded_filenames[i + 1]))
            
            print(f"生成视频片段 {i+1}/5: {uploaded_filenames[i]} -> {uploaded_filenames[i+1]}")
            
            # 异步调用视频生成API
            rsp = VideoSynthesis.async_call(
                api_key=settings.DASHSCOPE_API_KEY,
                model="wan2.2-kf2v-flash",
                prompt=video_prompt,
                negative_prompt="低质量, 模糊, 畸形, 变形, 多余的肢体, 错误的解剖结构, 脸部缺陷, 文字, 水印。",
                first_frame_url=first_frame_url,
                last_frame_url=last_frame_url,
                resolution="720P",
                prompt_extend=True
            )
            
            if rsp.status_code == HTTPStatus.OK:
                task_ids.append(rsp.output.task_id)
                print(f"视频片段 {i+1} 任务已提交: {rsp.output.task_id}")
            else:
                raise HTTPException(
                    status_code=rsp.status_code,
                    detail=f"提交第 {i+1} 个视频任务失败: {rsp.message}"
                )
        
        # 等待所有视频生成完成并下载
        video_files = []
        
        for i, task_id in enumerate(task_ids):
            print(f"等待视频片段 {i+1}/5 完成...")
            video_url = await wait_for_video(task_id)
            
            if video_url:
                # 下载视频
                video_filename = f"{sequence_task_id}_part_{i+1}.mp4"
                video_path = os.path.join(VIDEO_DIR, video_filename)
                
                print(f"下载视频片段 {i+1}/5: {video_url}")
                success = await download_video(video_url, video_path)
                
                if success:
                    video_files.append(video_path)
                    print(f"视频片段 {i+1} 下载完成")
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"下载第 {i+1} 个视频失败"
                    )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"第 {i+1} 个视频生成失败或超时"
                )
        
        # 合并所有视频
        merged_filename = f"{sequence_task_id}_merged.mp4"
        merged_path = os.path.join(VIDEO_DIR, merged_filename)
        
        print(f"合并 {len(video_files)} 个视频片段...")
        merge_success = merge_videos(video_files, merged_path)
        
        if not merge_success:
            raise HTTPException(
                status_code=500,
                detail="视频合并失败"
            )
        
        # 清理临时文件
        try:
            # 删除上传的图片
            for filename in uploaded_filenames:
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # 删除视频片段（保留合并后的视频）
            for video_file in video_files:
                if os.path.exists(video_file):
                    os.remove(video_file)
        except Exception as e:
            print(f"清理临时文件失败: {str(e)}")
        
        # 生成视频访问URL
        merged_video_url = f"{settings.SERVER_URL}/videos/{merged_filename}"
        
        print(f"序列视频生成完成: {merged_video_url}")
        
        return VideoSequenceResponse(
            task_id=sequence_task_id,
            status="completed",
            message="序列视频生成并合并完成",
            total_videos=5,
            processed_videos=5,
            merged_video_url=merged_video_url
        )
    
    except HTTPException:
        # 清理临时文件
        try:
            for filename in uploaded_filenames:
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception:
            pass
        raise
    except Exception as e:
        # 清理临时文件
        try:
            for filename in uploaded_filenames:
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception:
            pass
        raise HTTPException(
            status_code=500,
            detail=f"生成序列视频失败: {str(e)}"
        )
