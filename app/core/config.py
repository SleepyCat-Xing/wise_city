from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # 项目基本信息
    PROJECT_NAME: str = "违章建筑智能检测系统"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: Optional[str] = None
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI模型配置
    MODEL_PATH: str = "./models/yolov8_violation.pt"
    CONFIDENCE_THRESHOLD: float = 0.5
    IOU_THRESHOLD: float = 0.45
    
    # 文件存储配置
    UPLOAD_DIR: str = "./data/uploads"
    RESULT_DIR: str = "./data/results"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()