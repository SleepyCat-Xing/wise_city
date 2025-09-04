import os
import shutil
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException
from PIL import Image
import aiofiles
from pathlib import Path

from app.core.config import settings

class FileService:
    """文件管理服务"""
    
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    def __init__(self):
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.RESULT_DIR).mkdir(parents=True, exist_ok=True)
        Path("./data/thumbnails").mkdir(parents=True, exist_ok=True)
    
    async def validate_file(self, file: UploadFile) -> Dict[str, Any]:
        """验证上传的文件"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 检查文件扩展名
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件格式。支持的格式: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # 检查文件大小
        content = await file.read()
        await file.seek(0)  # 重置文件指针
        
        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"文件大小超过限制 ({self.MAX_FILE_SIZE / 1024 / 1024:.1f}MB)"
            )
        
        # 尝试打开图像验证格式
        try:
            from io import BytesIO
            img = Image.open(BytesIO(content))
            img.verify()
            
            return {
                "filename": file.filename,
                "size": len(content),
                "format": img.format,
                "width": img.size[0] if hasattr(img, 'size') else 0,
                "height": img.size[1] if hasattr(img, 'size') else 0
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"无效的图像文件: {str(e)}")
    
    async def save_upload_file(self, file: UploadFile) -> Dict[str, Any]:
        """保存上传的文件"""
        # 验证文件
        file_info = await self.validate_file(file)
        
        # 生成唯一文件名
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        file_path = Path(settings.UPLOAD_DIR) / unique_filename
        
        try:
            # 异步保存文件
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # 创建缩略图
            thumbnail_path = await self.create_thumbnail(file_path)
            
            return {
                "original_filename": file.filename,
                "saved_filename": unique_filename,
                "file_path": str(file_path),
                "thumbnail_path": thumbnail_path,
                "file_size": file_info["size"],
                "image_width": file_info["width"],
                "image_height": file_info["height"],
                "image_format": file_info["format"],
                "upload_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # 如果保存失败，清理已创建的文件
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")
    
    async def create_thumbnail(self, image_path: Path, size: tuple = (200, 200)) -> str:
        """创建缩略图"""
        try:
            thumbnail_dir = Path("./data/thumbnails")
            thumbnail_filename = f"thumb_{image_path.stem}.jpg"
            thumbnail_path = thumbnail_dir / thumbnail_filename
            
            with Image.open(image_path) as img:
                # 转换为RGB模式（防止RGBA等格式问题）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 创建缩略图
                img.thumbnail(size, Image.Resampling.LANCZOS)
                img.save(thumbnail_path, "JPEG", quality=85)
            
            return str(thumbnail_path)
            
        except Exception as e:
            print(f"创建缩略图失败: {str(e)}")
            return ""
    
    async def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                
                # 同时删除缩略图
                thumbnail_path = Path("./data/thumbnails") / f"thumb_{path.stem}.jpg"
                if thumbnail_path.exists():
                    thumbnail_path.unlink()
                
                return True
            return False
            
        except Exception as e:
            print(f"删除文件失败: {str(e)}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取文件信息"""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            
            # 尝试获取图像信息
            image_info = {}
            try:
                with Image.open(path) as img:
                    image_info = {
                        "width": img.width,
                        "height": img.height,
                        "format": img.format,
                        "mode": img.mode
                    }
            except:
                pass
            
            return {
                "filename": path.name,
                "file_path": str(path),
                "file_size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                **image_info
            }
            
        except Exception as e:
            print(f"获取文件信息失败: {str(e)}")
            return None
    
    def list_uploaded_files(self, limit: int = 100) -> List[Dict[str, Any]]:
        """列出已上传的文件"""
        try:
            upload_dir = Path(settings.UPLOAD_DIR)
            files = []
            
            for file_path in upload_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.ALLOWED_EXTENSIONS:
                    file_info = self.get_file_info(str(file_path))
                    if file_info:
                        files.append(file_info)
            
            # 按修改时间排序
            files.sort(key=lambda x: x["modified_time"], reverse=True)
            
            return files[:limit]
            
        except Exception as e:
            print(f"列出文件失败: {str(e)}")
            return []
    
    def cleanup_old_files(self, days: int = 30) -> int:
        """清理旧文件"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            for directory in [settings.UPLOAD_DIR, settings.RESULT_DIR, "./data/thumbnails"]:
                dir_path = Path(directory)
                if not dir_path.exists():
                    continue
                
                for file_path in dir_path.iterdir():
                    if file_path.is_file():
                        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if mod_time < cutoff_time:
                            try:
                                file_path.unlink()
                                deleted_count += 1
                            except Exception as e:
                                print(f"删除文件失败 {file_path}: {str(e)}")
            
            return deleted_count
            
        except Exception as e:
            print(f"清理文件失败: {str(e)}")
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        try:
            stats = {}
            
            for name, directory in [
                ("uploads", settings.UPLOAD_DIR),
                ("results", settings.RESULT_DIR),
                ("thumbnails", "./data/thumbnails")
            ]:
                dir_path = Path(directory)
                if dir_path.exists():
                    total_size = 0
                    file_count = 0
                    
                    for file_path in dir_path.rglob("*"):
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
                            file_count += 1
                    
                    stats[name] = {
                        "file_count": file_count,
                        "total_size": total_size,
                        "total_size_mb": round(total_size / (1024 * 1024), 2)
                    }
                else:
                    stats[name] = {
                        "file_count": 0,
                        "total_size": 0,
                        "total_size_mb": 0
                    }
            
            return stats
            
        except Exception as e:
            print(f"获取存储统计失败: {str(e)}")
            return {}