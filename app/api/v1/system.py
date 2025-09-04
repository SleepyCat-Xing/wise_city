from fastapi import APIRouter, HTTPException
import psutil
import os
from datetime import datetime
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    系统健康检查
    """
    try:
        # 获取系统信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 检查关键目录
        directories_status = {}
        for dir_name, dir_path in [
            ("uploads", settings.UPLOAD_DIR),
            ("results", settings.RESULT_DIR),
            ("models", "./models"),
            ("logs", "./logs")
        ]:
            directories_status[dir_name] = {
                "exists": os.path.exists(dir_path),
                "writable": os.access(dir_path, os.W_OK) if os.path.exists(dir_path) else False
            }
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "memory_available": f"{memory.available / (1024**3):.2f} GB",
                "disk_usage": f"{disk.percent}%",
                "disk_free": f"{disk.free / (1024**3):.2f} GB"
            },
            "directories": directories_status,
            "config": {
                "project_name": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "model_path": settings.MODEL_PATH,
                "confidence_threshold": settings.CONFIDENCE_THRESHOLD
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")

@router.get("/stats/summary")
async def get_system_stats():
    """
    获取系统统计信息
    """
    try:
        # 统计上传文件数量
        upload_count = 0
        upload_size = 0
        if os.path.exists(settings.UPLOAD_DIR):
            for filename in os.listdir(settings.UPLOAD_DIR):
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                if os.path.isfile(file_path):
                    upload_count += 1
                    upload_size += os.path.getsize(file_path)
        
        # 统计结果文件数量
        result_count = 0
        result_size = 0
        if os.path.exists(settings.RESULT_DIR):
            for filename in os.listdir(settings.RESULT_DIR):
                file_path = os.path.join(settings.RESULT_DIR, filename)
                if os.path.isfile(file_path):
                    result_count += 1
                    result_size += os.path.getsize(file_path)
        
        return {
            "success": True,
            "data": {
                "uploads": {
                    "count": upload_count,
                    "total_size_mb": round(upload_size / (1024**2), 2)
                },
                "results": {
                    "count": result_count,
                    "total_size_mb": round(result_size / (1024**2), 2)
                },
                "system_uptime": "实时查询暂未实现"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_old_files():
    """
    清理旧文件
    """
    try:
        from app.services.detection_service import DetectionService
        service = DetectionService()
        service.cleanup_old_files(max_age_days=7)
        
        return {
            "success": True,
            "message": "旧文件清理完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))