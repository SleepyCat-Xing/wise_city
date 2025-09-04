from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from typing import List, Optional
from pathlib import Path

from app.services.file_service import FileService

router = APIRouter()
file_service = FileService()

@router.post("/upload")
async def upload_file(file: UploadFile = File(..., description="上传的图像文件")):
    """
    上传图像文件
    """
    try:
        result = await file_service.save_upload_file(file)
        
        return {
            "success": True,
            "message": "文件上传成功",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.post("/upload/batch")
async def upload_batch_files(
    files: List[UploadFile] = File(..., description="批量上传的图像文件列表")
):
    """
    批量上传图像文件
    """
    if len(files) > 20:  # 限制批量上传数量
        raise HTTPException(status_code=400, detail="批量上传最多支持20个文件")
    
    try:
        results = []
        failed_files = []
        
        for file in files:
            try:
                result = await file_service.save_upload_file(file)
                results.append(result)
            except HTTPException as e:
                failed_files.append({
                    "filename": file.filename,
                    "error": str(e.detail)
                })
            except Exception as e:
                failed_files.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "message": f"批量上传完成，成功 {len(results)} 个，失败 {len(failed_files)} 个",
            "data": {
                "successful_uploads": results,
                "failed_uploads": failed_files,
                "total_uploaded": len(results),
                "total_failed": len(failed_files)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量上传失败: {str(e)}")

@router.get("/list")
async def list_files(limit: int = Query(100, ge=1, le=500, description="返回文件数量限制")):
    """
    获取已上传文件列表
    """
    try:
        files = file_service.list_uploaded_files(limit=limit)
        
        return {
            "success": True,
            "message": "获取文件列表成功",
            "data": {
                "files": files,
                "total_count": len(files)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")

@router.get("/info/{filename}")
async def get_file_info(filename: str):
    """
    获取指定文件信息
    """
    try:
        from app.core.config import settings
        file_path = Path(settings.UPLOAD_DIR) / filename
        file_info = file_service.get_file_info(str(file_path))
        
        if not file_info:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return {
            "success": True,
            "message": "获取文件信息成功",
            "data": file_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件信息失败: {str(e)}")

@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    下载文件
    """
    try:
        from app.core.config import settings
        file_path = Path(settings.UPLOAD_DIR) / filename
        
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")

@router.get("/thumbnail/{filename}")
async def get_thumbnail(filename: str):
    """
    获取文件缩略图
    """
    try:
        # 构建缩略图路径
        file_stem = Path(filename).stem
        thumbnail_filename = f"thumb_{file_stem}.jpg"
        thumbnail_path = Path("./data/thumbnails") / thumbnail_filename
        
        if not thumbnail_path.exists():
            raise HTTPException(status_code=404, detail="缩略图不存在")
        
        return FileResponse(
            path=str(thumbnail_path),
            media_type='image/jpeg'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缩略图失败: {str(e)}")

@router.delete("/{filename}")
async def delete_file(filename: str):
    """
    删除指定文件
    """
    try:
        from app.core.config import settings
        file_path = Path(settings.UPLOAD_DIR) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        success = await file_service.delete_file(str(file_path))
        
        if success:
            return {
                "success": True,
                "message": f"文件 {filename} 删除成功"
            }
        else:
            raise HTTPException(status_code=500, detail="删除文件失败")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文件失败: {str(e)}")

@router.post("/cleanup")
async def cleanup_old_files(days: int = Query(30, ge=1, le=365, description="保留天数")):
    """
    清理指定天数之前的旧文件
    """
    try:
        deleted_count = file_service.cleanup_old_files(days=days)
        
        return {
            "success": True,
            "message": f"清理完成，删除了 {deleted_count} 个文件",
            "data": {
                "deleted_count": deleted_count,
                "days": days
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理文件失败: {str(e)}")

@router.get("/stats")
async def get_storage_stats():
    """
    获取存储统计信息
    """
    try:
        stats = file_service.get_storage_stats()
        
        return {
            "success": True,
            "message": "获取存储统计成功",
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取存储统计失败: {str(e)}")