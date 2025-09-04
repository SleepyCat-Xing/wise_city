from fastapi import APIRouter
from app.api.v1 import detection, system, files, legal

api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(
    detection.router, 
    prefix="/detection", 
    tags=["违建检测"]
)

api_router.include_router(
    legal.router,
    prefix="/legal",
    tags=["法规解读"]
)

api_router.include_router(
    system.router, 
    prefix="/system", 
    tags=["系统管理"]
)

api_router.include_router(
    files.router, 
    prefix="/files", 
    tags=["文件管理"]
)