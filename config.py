from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # API配置
    API_VERSION: str = "v1"
    
    # DashScope配置
    DASHSCOPE_API_KEY: str = "sk-30a9f0814f43457289061dcecf87691a"
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1"
    
    # 服务器URL配置（用于生成文件访问URL）
    SERVER_URL: str = "http://localhost:8000"
    
    # 视频生成默认配置
    DEFAULT_PROMPT: str = "写实风格，高质量视频，流畅的镜头运动"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
