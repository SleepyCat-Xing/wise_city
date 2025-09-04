import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import UploadFile
from app.services.ai_service import AIService
from app.models.detection import DetectionResult, ViolationDetection
from app.core.config import settings
import aiofiles

class DetectionService:
    def __init__(self):
        self.ai_service = AIService()
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.RESULT_DIR, exist_ok=True)
    
    async def save_uploaded_file(self, file: UploadFile) -> str:
        """保存上传的文件"""
        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # 异步保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return file_path
    
    async def detect_image(
        self, 
        file: UploadFile,
        confidence_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None
    ) -> DetectionResult:
        """检测单张图像中的违章建筑"""
        try:
            # 保存上传的文件
            image_path = await self.save_uploaded_file(file)
            
            # 进行AI检测
            detections, processing_time = self.ai_service.detect_violations(
                image_path=image_path,
                confidence_threshold=confidence_threshold,
                iou_threshold=iou_threshold
            )
            
            # 获取图像信息
            from PIL import Image
            with Image.open(image_path) as img:
                image_info = {
                    "filename": file.filename,
                    "file_size": len(await file.read()),
                    "width": img.width,
                    "height": img.height,
                    "format": img.format
                }
            
            # 创建检测结果
            result = DetectionResult(
                image_path=image_path,
                detections=detections,
                total_violations=len(detections),
                confidence_threshold=confidence_threshold or settings.CONFIDENCE_THRESHOLD,
                iou_threshold=iou_threshold or settings.IOU_THRESHOLD,
                processing_time=processing_time,
                created_at=datetime.utcnow()
            )
            
            return result
            
        except Exception as e:
            raise Exception(f"图像检测失败: {str(e)}")
    
    async def detect_batch(
        self,
        files: List[UploadFile],
        confidence_threshold: Optional[float] = None,
        iou_threshold: Optional[float] = None
    ) -> List[DetectionResult]:
        """批量检测图像中的违章建筑"""
        results = []
        
        for file in files:
            try:
                result = await self.detect_image(
                    file=file,
                    confidence_threshold=confidence_threshold,
                    iou_threshold=iou_threshold
                )
                results.append(result)
            except Exception as e:
                # 对于批量处理，记录错误但继续处理其他文件
                print(f"处理文件 {file.filename} 时出错: {str(e)}")
                continue
        
        return results
    
    def get_detection_statistics(self, results: List[DetectionResult]) -> dict:
        """获取检测统计信息"""
        if not results:
            return {
                "total_images": 0,
                "total_violations": 0,
                "average_violations_per_image": 0,
                "class_distribution": {}
            }
        
        total_violations = sum(len(result.detections) for result in results)
        class_counts = {}
        
        for result in results:
            for detection in result.detections:
                class_name = detection.class_name
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        return {
            "total_images": len(results),
            "total_violations": total_violations,
            "average_violations_per_image": total_violations / len(results) if results else 0,
            "class_distribution": class_counts
        }
    
    def cleanup_old_files(self, max_age_days: int = 7):
        """清理旧的上传文件"""
        import time
        current_time = time.time()
        cutoff_time = current_time - (max_age_days * 24 * 60 * 60)
        
        for directory in [settings.UPLOAD_DIR, settings.RESULT_DIR]:
            if not os.path.exists(directory):
                continue
                
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    file_time = os.path.getmtime(file_path)
                    if file_time < cutoff_time:
                        try:
                            os.remove(file_path)
                            print(f"已删除旧文件: {file_path}")
                        except Exception as e:
                            print(f"删除文件失败 {file_path}: {str(e)}")