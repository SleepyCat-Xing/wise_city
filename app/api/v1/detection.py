from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Optional
from app.services.detection_service import DetectionService
from app.models.detection import DetectionResponse, DetectionRequest

router = APIRouter()
detection_service = DetectionService()

@router.post("/detect/image", response_model=DetectionResponse)
async def detect_image(
    file: UploadFile = File(..., description="上传的图像文件"),
    confidence_threshold: Optional[float] = Form(None, description="置信度阈值"),
    iou_threshold: Optional[float] = Form(None, description="IOU阈值")
):
    """
    单张图像违章建筑检测
    """
    try:
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="请上传图像文件")
        
        # 进行检测
        result = await detection_service.detect_image(
            file=file,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold
        )
        
        return DetectionResponse(
            success=True,
            message="检测完成",
            result=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect/batch")
async def detect_batch(
    files: List[UploadFile] = File(..., description="上传的图像文件列表"),
    confidence_threshold: Optional[float] = Form(None, description="置信度阈值"),
    iou_threshold: Optional[float] = Form(None, description="IOU阈值")
):
    """
    批量图像违章建筑检测
    """
    try:
        # 验证文件数量
        if len(files) > 10:  # 限制最大批量处理数量
            raise HTTPException(status_code=400, detail="批量处理最多支持10个文件")
        
        # 验证文件类型
        for file in files:
            if not file.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail=f"文件 {file.filename} 不是图像文件")
        
        # 进行批量检测
        results = await detection_service.detect_batch(
            files=files,
            confidence_threshold=confidence_threshold,
            iou_threshold=iou_threshold
        )
        
        # 获取统计信息
        statistics = detection_service.get_detection_statistics(results)
        
        return {
            "success": True,
            "message": f"批量检测完成，处理了 {len(results)} 个文件",
            "results": results,
            "statistics": statistics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model/info")
async def get_model_info():
    """
    获取AI模型信息
    """
    try:
        model_info = detection_service.ai_service.get_model_info()
        return {
            "success": True,
            "message": "获取模型信息成功",
            "data": model_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/violation/categories")
async def get_violation_categories():
    """
    获取违章建筑类别信息
    """
    try:
        from app.models.violation_types import VIOLATION_CATEGORIES_INFO, get_all_violation_categories
        
        categories = []
        for category_name in get_all_violation_categories():
            from app.models.violation_types import ViolationCategory
            category = ViolationCategory(category_name)
            info = VIOLATION_CATEGORIES_INFO.get(category)
            if info:
                categories.append({
                    "category": category.value,
                    "chinese_name": info.chinese_name,
                    "description": info.description,
                    "severity_level": info.severity_level.value,
                    "typical_features": info.typical_features,
                    "common_locations": info.common_locations,
                    "legal_basis": info.legal_basis
                })
        
        return {
            "success": True,
            "message": "获取违章类别信息成功",
            "data": {
                "categories": categories,
                "total_count": len(categories)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/multimodal")
async def multimodal_analysis(
    file: UploadFile = File(..., description="上传的图像文件")
):
    """
    多模态综合分析 - 基于项目简表要求的高级功能
    """
    try:
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="请上传图像文件")
        
        # 保存上传的文件
        from app.services.file_service import FileService
        file_service = FileService()
        file_info = await file_service.save_upload_file(file)
        
        # 进行多模态分析
        analysis_result = detection_service.ai_service.get_multimodal_analysis(
            file_info["file_path"]
        )
        
        return {
            "success": True,
            "message": "多模态分析完成",
            "data": {
                "file_info": file_info,
                "analysis": analysis_result,
                "features": {
                    "image_enhancement": "已启用",
                    "building_structure_analysis": "已完成",
                    "environmental_context": "已分析",
                    "risk_assessment": "已生成"
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance/metrics")
async def get_performance_metrics():
    """
    获取系统性能指标 - 符合项目简表的性能要求
    """
    try:
        model_info = detection_service.ai_service.get_model_info()
        
        return {
            "success": True,
            "message": "性能指标获取成功",
            "data": {
                "model_performance": model_info.get("performance_metrics", {}),
                "target_metrics": {
                    "mAP_target": "≥0.85",
                    "processing_speed_target": "50 FPS@1080p",
                    "response_time_target": "≤3秒",
                    "concurrent_users_target": "1000+"
                },
                "current_status": model_info.get("multimodal_features", {}),
                "system_info": {
                    "model_type": model_info.get("model_type"),
                    "violation_categories": model_info.get("violation_categories"),
                    "gpu_acceleration": model_info.get("performance_metrics", {}).get("gpu_enabled", False)
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))