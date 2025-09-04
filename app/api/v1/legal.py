#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法规解读API端点
智慧城管系统 - 大语言模型法规解读功能
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.services.legal_service import legal_service
from app.services.detection_service import DetectionService
from app.services.file_service import FileService

router = APIRouter()
detection_service = DetectionService()
file_service = FileService()


class LegalAnalysisRequest(BaseModel):
    """法律分析请求模型"""
    violation_description: str
    image_analysis_result: Optional[Dict[str, Any]] = None
    use_llm: bool = True
    

class LegalSearchRequest(BaseModel):
    """法律搜索请求模型"""
    keywords: List[str]
    violation_type: Optional[str] = None


@router.post("/analyze/comprehensive")
async def comprehensive_legal_analysis(
    file: UploadFile = File(..., description="违章建筑图像"),
    violation_description: str = Form(..., description="违章情况描述"),
    use_llm: bool = Form(True, description="是否使用大语言模型分析")
):
    """
    综合法律分析 - 图像检测 + 法规解读
    结合多模态AI和大语言模型提供全面的法律分析
    """
    try:
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="请上传图像文件")
        
        # 保存并分析图像
        file_info = await file_service.save_upload_file(file)
        
        # 多模态图像分析
        multimodal_analysis = detection_service.ai_service.get_multimodal_analysis(
            file_info["file_path"]
        )
        
        # 违章检测
        detection_result = await detection_service.detect_image(
            file=file,
            confidence_threshold=0.5,
            iou_threshold=0.45
        )
        
        # 法规解读分析
        legal_analysis = await legal_service.analyze_violation_with_llm(
            violation_description=violation_description,
            image_analysis=multimodal_analysis
        )
        
        return {
            "success": True,
            "message": "综合法律分析完成",
            "data": {
                "file_info": {
                    "filename": file_info["original_filename"],
                    "file_size": file_info["file_size"],
                    "image_format": file_info["image_format"]
                },
                "image_analysis": multimodal_analysis,
                "violation_detection": {
                    "total_violations": detection_result.total_violations,
                    "detections": [detection.dict() for detection in detection_result.detections],
                    "processing_time": detection_result.processing_time
                },
                "legal_analysis": legal_analysis,
                "analysis_metadata": {
                    "use_llm": use_llm,
                    "analysis_version": "v1.0",
                    "knowledge_base_enhanced": legal_analysis.get("enhanced_by_knowledge_base", False)
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"综合分析失败: {str(e)}")


@router.post("/analyze/text")
async def text_legal_analysis(request: LegalAnalysisRequest):
    """
    文本法律分析 - 纯文本描述的法规解读
    """
    try:
        # 如果没有图像分析结果，使用默认值
        image_analysis = request.image_analysis_result or {
            "risk_assessment": {"risk_score": 30, "risk_level": "中"},
            "building_features": {"complexity_level": "中"},
            "environmental_context": {"lighting_condition": "良好"}
        }
        
        # 进行法规解读
        legal_analysis = await legal_service.analyze_violation_with_llm(
            violation_description=request.violation_description,
            image_analysis=image_analysis
        )
        
        return {
            "success": True,
            "message": "文本法律分析完成",
            "data": {
                "input_description": request.violation_description,
                "legal_analysis": legal_analysis,
                "analysis_type": "text_only",
                "use_llm": request.use_llm
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文本分析失败: {str(e)}")


@router.get("/violations/{violation_type}/legal-summary")
async def get_violation_legal_summary(violation_type: str):
    """
    获取特定违章类型的法律摘要
    """
    try:
        legal_summary = legal_service.get_violation_legal_summary(violation_type)
        
        if "error" in legal_summary:
            raise HTTPException(status_code=404, detail=legal_summary["error"])
        
        return {
            "success": True,
            "message": "法律摘要获取成功",
            "data": legal_summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取法律摘要失败: {str(e)}")


@router.post("/search/regulations")
async def search_legal_regulations(request: LegalSearchRequest):
    """
    搜索相关法律法规
    """
    try:
        search_results = legal_service.search_legal_cases(request.keywords)
        
        return {
            "success": True,
            "message": f"找到 {len(search_results)} 条相关法规",
            "data": {
                "keywords": request.keywords,
                "results": search_results,
                "search_type": "regulations"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索法规失败: {str(e)}")


@router.get("/knowledge-base/statistics")
async def get_knowledge_base_statistics():
    """
    获取法规知识库统计信息
    """
    try:
        stats = legal_service.knowledge_base.get_enforcement_statistics()
        
        return {
            "success": True,
            "message": "知识库统计信息获取成功",
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/violation-types")
async def get_supported_violation_types():
    """
    获取支持的违章类型列表
    """
    try:
        from app.models.legal_regulations import ViolationType
        
        violation_types = []
        for vt in ViolationType:
            # 获取该违章类型的法律摘要
            legal_summary = legal_service.get_violation_legal_summary(vt.value)
            
            violation_types.append({
                "type": vt.value,
                "name": vt.value.replace("_", " ").title(),
                "applicable_laws_count": legal_summary.get("applicable_laws_count", 0),
                "has_legal_basis": not legal_summary.get("error")
            })
        
        return {
            "success": True,
            "message": "支持的违章类型获取成功",
            "data": {
                "violation_types": violation_types,
                "total_types": len(violation_types)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取违章类型失败: {str(e)}")


@router.get("/llm/status")
async def get_llm_status():
    """
    获取大语言模型集成状态
    """
    try:
        llm_config = legal_service.llm_config
        
        return {
            "success": True,
            "message": "LLM状态获取成功",
            "data": {
                "llm_enabled": llm_config["enabled"],
                "model_name": llm_config["model_name"],
                "api_configured": bool(llm_config["api_endpoint"] and llm_config["api_key"]),
                "fallback_mode": "local_rule_engine",
                "status": "可用" if llm_config["enabled"] else "使用本地规则引擎"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取LLM状态失败: {str(e)}")


@router.post("/demo/mock-llm-analysis")
async def demo_mock_llm_analysis(violation_description: str = Form(...)):
    """
    演示用模拟LLM分析 - 用于展示系统功能
    """
    try:
        # 模拟图像分析结果
        mock_image_analysis = {
            "image_properties": {
                "quality_metrics": {
                    "quality_rating": "高",
                    "blur_score": 150.0,
                    "brightness": 120.0,
                    "contrast": 85.0
                }
            },
            "building_features": {
                "structural_features": {
                    "edge_density": 0.12,
                    "regularity_score": 0.4
                },
                "complexity_level": "高"
            },
            "environmental_context": {
                "scene_type": "城市",
                "environmental_factors": {
                    "lighting_condition": "良好"
                }
            },
            "risk_assessment": {
                "risk_score": 45,
                "risk_level": "中",
                "risk_factors": ["建筑结构复杂，需要重点关注"],
                "confidence": 0.85
            },
            "recommendations": ["建筑结构复杂，建议多角度拍摄进行综合分析"]
        }
        
        # 使用本地规则分析（模拟LLM）
        legal_analysis = await legal_service.analyze_violation_with_llm(
            violation_description=violation_description,
            image_analysis=mock_image_analysis
        )
        
        return {
            "success": True,
            "message": "模拟LLM分析完成（演示模式）",
            "data": {
                "input_description": violation_description,
                "mock_image_analysis": mock_image_analysis,
                "legal_analysis": legal_analysis,
                "demo_mode": True,
                "note": "这是演示模式，实际部署时将使用真实的大语言模型进行分析"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模拟分析失败: {str(e)}")