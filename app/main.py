from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.api import api_router
from app.core.database import init_database, close_database
import logging

# 配置日志
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("启动违章建筑智能检测系统...")
    
    # 启动时初始化数据库
    await init_database()
    logger.info("系统启动完成")
    
    yield
    
    # 关闭时清理资源
    await close_database()
    logger.info("系统已关闭")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="基于多模态AI的违章建筑智能检测与管理系统",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 挂载静态文件
import os
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {
        "message": "违章建筑智能检测系统API",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "demo_url": "/demo",
        "database_enabled": settings.DATABASE_URL is not None
    }

@app.get("/health")
async def health_check():
    from app.core.database import db_manager
    return {
        "status": "healthy", 
        "message": "系统运行正常",
        "database_status": "connected" if db_manager._initialized and db_manager.engine else "disabled"
    }

@app.get("/demo")
async def demo_page():
    return FileResponse("static/demo.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)