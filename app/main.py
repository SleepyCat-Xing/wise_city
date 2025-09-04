#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智慧城管：基于多模态AI的违章建筑智能检测与管理系统
主应用程序入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.api import api_router
from app.core.database import init_database, close_database
import logging
import sys
import os

# 设置编码
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# 配置日志
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("启动智慧城管：基于多模态AI的违章建筑智能检测与管理系统...")
    
    # 启动时初始化数据库
    await init_database()
    logger.info("系统启动完成，已就绪处理请求")
    
    yield
    
    # 关闭时清理资源
    await close_database()
    logger.info("系统已安全关闭")

app = FastAPI(
    title="智慧城管：基于多模态AI的违章建筑智能检测与管理系统",
    version="v1.0.0 - Competition Edition",
    description="""
## 🏗️ 智慧城管系统 - 第十一届中国研究生智慧城市技术与创意设计大赛作品

### 🎯 核心功能
- **多模态AI融合检测**: 基于增强YOLOv8算法，支持多种数据源融合
- **违章建筑智能分类**: 精准识别6大类违章建筑类型  
- **图像增强处理**: 自适应对比度调整、噪声减少、边缘锐化
- **实时性能监控**: 目标mAP≥0.85，响应时间≤3秒

### 🔧 技术特性
- **高性能**: 支持50 FPS@1080p处理速度
- **多格式**: 支持JPG、PNG、BMP、TIF/TIFF、WebP等格式  
- **智能分析**: 建筑结构分析、环境上下文理解、风险评估
- **RESTful API**: 标准化接口，易于集成

### 📊 应用价值
- **管理效率提升**: 全天候自动化监测
- **执法成本降低**: 智能化辅助决策  
- **技术创新**: 多模态AI融合的垂直领域应用

---
*🎓 团队：智城守护者 | 🏆 定向赛道：城市建设与数字更新*
    """,
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
        "demo_url": "/static/demo.html",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)