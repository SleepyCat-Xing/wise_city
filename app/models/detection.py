from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.violation_types import ViolationCategory, ViolationSeverity, ViolationStatus

class BoundingBox(BaseModel):
    x: float = Field(..., description="边界框左上角X坐标")
    y: float = Field(..., description="边界框左上角Y坐标") 
    width: float = Field(..., description="边界框宽度")
    height: float = Field(..., description="边界框高度")
    
    def get_center(self) -> tuple[float, float]:
        """获取边界框中心点坐标"""
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    def get_area(self) -> float:
        """获取边界框面积"""
        return self.width * self.height

class ViolationDetection(BaseModel):
    """违章建筑检测结果"""
    class_id: int = Field(..., description="检测类别ID")
    class_name: str = Field(..., description="检测类别名称")
    violation_category: Optional[ViolationCategory] = Field(None, description="违章建筑类别")
    confidence: float = Field(..., ge=0.0, le=1.0, description="检测置信度")
    bbox: BoundingBox = Field(..., description="边界框")
    area: float = Field(..., description="检测区域面积")
    severity: Optional[ViolationSeverity] = Field(None, description="违章严重程度")
    description: Optional[str] = Field(None, description="检测描述")
    
    def __post_init__(self):
        """后处理，根据类别自动设置违章信息"""
        if self.violation_category:
            from app.models.violation_types import get_violation_info
            info = get_violation_info(self.violation_category)
            if info:
                self.severity = info.severity_level
                self.description = info.description

class ImageInfo(BaseModel):
    """图像信息"""
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小(字节)")
    width: int = Field(..., description="图像宽度")
    height: int = Field(..., description="图像高度")
    format: str = Field(..., description="图像格式")
    upload_time: datetime = Field(default_factory=datetime.utcnow, description="上传时间")

class DetectionResult(BaseModel):
    """检测结果模型"""
    id: Optional[int] = Field(None, description="结果ID")
    image_path: str = Field(..., description="图像路径")
    image_info: Optional[ImageInfo] = Field(None, description="图像信息")
    detections: List[ViolationDetection] = Field(default_factory=list, description="检测结果列表")
    total_violations: int = Field(0, description="违章建筑总数")
    confidence_threshold: float = Field(0.5, description="置信度阈值")
    iou_threshold: float = Field(0.45, description="IOU阈值")
    processing_time: Optional[float] = Field(None, description="处理耗时(秒)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    status: ViolationStatus = Field(ViolationStatus.DETECTED, description="处理状态")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")
    
    def get_violations_by_severity(self) -> Dict[ViolationSeverity, int]:
        """按严重程度统计违章数量"""
        severity_count = {}
        for detection in self.detections:
            if detection.severity:
                severity_count[detection.severity] = severity_count.get(detection.severity, 0) + 1
        return severity_count
    
    def get_violations_by_category(self) -> Dict[ViolationCategory, int]:
        """按类别统计违章数量"""
        category_count = {}
        for detection in self.detections:
            if detection.violation_category:
                category_count[detection.violation_category] = category_count.get(detection.violation_category, 0) + 1
        return category_count

class DetectionRequest(BaseModel):
    """检测请求参数"""
    confidence_threshold: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="置信度阈值")
    iou_threshold: Optional[float] = Field(0.45, ge=0.0, le=1.0, description="IOU阈值")
    enable_violation_classification: Optional[bool] = Field(True, description="启用违章分类")
    save_result: Optional[bool] = Field(True, description="保存检测结果")

class BatchDetectionRequest(BaseModel):
    """批量检测请求参数"""
    confidence_threshold: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="置信度阈值")
    iou_threshold: Optional[float] = Field(0.45, ge=0.0, le=1.0, description="IOU阈值")
    max_files: Optional[int] = Field(10, ge=1, le=50, description="最大文件数量")
    enable_violation_classification: Optional[bool] = Field(True, description="启用违章分类")
    save_results: Optional[bool] = Field(True, description="保存检测结果")

class DetectionResponse(BaseModel):
    """检测响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    result: Optional[DetectionResult] = Field(None, description="检测结果")
    processing_time: Optional[float] = Field(None, description="处理耗时")
    error_code: Optional[str] = Field(None, description="错误代码")

class BatchDetectionResponse(BaseModel):
    """批量检测响应"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    results: List[DetectionResult] = Field(default_factory=list, description="检测结果列表")
    total_processed: int = Field(0, description="已处理文件数")
    total_violations: int = Field(0, description="违章总数")
    processing_time: Optional[float] = Field(None, description="总处理耗时")
    statistics: Optional[Dict[str, Any]] = Field(None, description="统计信息")
    failed_files: List[str] = Field(default_factory=list, description="处理失败的文件")

class DetectionStatistics(BaseModel):
    """检测统计信息"""
    total_detections: int = Field(0, description="检测总数")
    total_violations: int = Field(0, description="违章总数")
    severity_distribution: Dict[str, int] = Field(default_factory=dict, description="严重程度分布")
    category_distribution: Dict[str, int] = Field(default_factory=dict, description="类别分布")
    daily_stats: Optional[Dict[str, int]] = Field(None, description="每日统计")
    monthly_stats: Optional[Dict[str, int]] = Field(None, description="每月统计")