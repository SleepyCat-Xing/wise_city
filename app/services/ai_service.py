import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Optional
from app.models.detection import ViolationDetection, BoundingBox
from app.models.violation_types import ViolationCategory, ViolationSeverity, get_violation_info
from app.core.config import settings
import os
import time

class AIService:
    def __init__(self):
        self.model = None
        self.violation_class_mapping = self._init_violation_mapping()
        self.load_model()
    
    def _init_violation_mapping(self):
        """初始化违章建筑类别映射"""
        # YOLO预训练模型类别到违章建筑类别的映射
        # 这里是基于COCO数据集类别的智能映射
        return {
            # 建筑相关
            "person": None,  # 人员不算违章
            "car": ViolationCategory.UNAUTHORIZED_PARKING,  # 违规停车
            "truck": ViolationCategory.UNAUTHORIZED_PARKING,  # 违规停车
            "bus": ViolationCategory.UNAUTHORIZED_PARKING,  # 违规停车
            
            # 建筑结构
            "chair": ViolationCategory.TEMPORARY_STRUCTURE,  # 可能是临时搭建
            "couch": ViolationCategory.TEMPORARY_STRUCTURE,  # 临时家具
            "bed": ViolationCategory.TEMPORARY_STRUCTURE,  # 临时住所
            
            # 遮蔽物和棚屋
            "umbrella": ViolationCategory.SHED_STRUCTURE,  # 遮雨棚
            "bench": ViolationCategory.TEMPORARY_STRUCTURE,  # 临时座椅
            
            # 商业相关
            "bottle": ViolationCategory.ILLEGAL_MARKET_STALL,  # 可能是摊位
            "cup": ViolationCategory.ILLEGAL_MARKET_STALL,  # 摊位用品
            "bowl": ViolationCategory.ILLEGAL_MARKET_STALL,  # 摊位用品
            
            # 默认映射 - 未识别的物体可能是违章建筑
            "default": ViolationCategory.ILLEGAL_CONSTRUCTION
        }
    
    def load_model(self):
        """加载YOLOv8模型"""
        try:
            if os.path.exists(settings.MODEL_PATH):
                self.model = YOLO(settings.MODEL_PATH)
                print(f"模型已加载: {settings.MODEL_PATH}")
            else:
                # 如果没有自定义模型，使用预训练模型
                self.model = YOLO('yolov8n.pt')
                print("使用YOLOv8预训练模型")
        except Exception as e:
            print(f"模型加载失败: {e}")
            self.model = None
    
    def detect_violations(
        self, 
        image_path: str, 
        confidence_threshold: float = None,
        iou_threshold: float = None,
        enable_violation_classification: bool = True
    ) -> Tuple[List[ViolationDetection], float]:
        """检测违章建筑"""
        if self.model is None:
            raise Exception("模型未加载")
        
        start_time = time.time()
        confidence_threshold = confidence_threshold or settings.CONFIDENCE_THRESHOLD
        iou_threshold = iou_threshold or settings.IOU_THRESHOLD
        
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("无法读取图像文件")
            
            # 进行预测
            results = self.model(
                image_path,
                conf=confidence_threshold,
                iou=iou_threshold,
                verbose=False
            )
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # 获取边界框坐标
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # 获取类别名称
                        class_name = self.model.names[class_id]
                        
                        # 创建BoundingBox对象
                        bbox = BoundingBox(
                            x=float(x1),
                            y=float(y1),
                            width=float(x2 - x1),
                            height=float(y2 - y1)
                        )
                        
                        # 计算面积
                        area = bbox.width * bbox.height
                        
                        # 违章分类
                        violation_category = None
                        severity = None
                        description = None
                        
                        if enable_violation_classification:
                            violation_category = self._classify_violation(class_name, bbox, image.shape)
                            if violation_category:
                                violation_info = get_violation_info(violation_category)
                                if violation_info:
                                    severity = violation_info.severity_level
                                    description = violation_info.description
                        
                        # 创建ViolationDetection对象
                        detection = ViolationDetection(
                            class_id=class_id,
                            class_name=class_name,
                            violation_category=violation_category,
                            confidence=confidence,
                            bbox=bbox,
                            area=area,
                            severity=severity,
                            description=description
                        )
                        
                        detections.append(detection)
            
            processing_time = time.time() - start_time
            return detections, processing_time
            
        except Exception as e:
            raise Exception(f"检测失败: {str(e)}")
    
    def _classify_violation(self, class_name: str, bbox: BoundingBox, image_shape: Tuple[int, int, int]) -> Optional[ViolationCategory]:
        """根据检测类别和特征分类违章建筑类型"""
        # 获取基础映射
        violation_category = self.violation_class_mapping.get(class_name)
        
        # 如果没有直接映射，使用智能分类
        if violation_category is None and class_name not in ["person"]:
            # 基于物体大小和位置的启发式分类
            image_height, image_width = image_shape[:2]
            
            # 计算相对大小
            relative_area = bbox.get_area() / (image_width * image_height)
            aspect_ratio = bbox.width / bbox.height
            
            # 基于特征的分类逻辑
            if relative_area > 0.3:  # 大面积物体
                if aspect_ratio > 3:  # 长条形
                    violation_category = ViolationCategory.ILLEGAL_FENCE
                else:
                    violation_category = ViolationCategory.ILLEGAL_CONSTRUCTION
            elif relative_area > 0.1:  # 中等面积
                if aspect_ratio < 0.5:  # 高瘦形状
                    violation_category = ViolationCategory.UNAUTHORIZED_STOREFRONT
                else:
                    violation_category = ViolationCategory.SHED_STRUCTURE
            else:  # 小面积物体
                violation_category = ViolationCategory.ILLEGAL_MARKET_STALL
        
        return violation_category
    
    def _analyze_building_structure(self, image: np.ndarray, bbox: BoundingBox) -> dict:
        """分析建筑结构特征"""
        # 提取检测区域
        x1, y1 = int(bbox.x), int(bbox.y)
        x2, y2 = int(bbox.x + bbox.width), int(bbox.y + bbox.height)
        roi = image[y1:y2, x1:x2]
        
        if roi.size == 0:
            return {}
        
        # 简单的结构分析
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # 边缘检测
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # 颜色分析
        mean_color = np.mean(roi, axis=(0, 1))
        
        return {
            "edge_density": float(edge_density),
            "mean_color": mean_color.tolist(),
            "size": roi.shape,
            "aspect_ratio": bbox.width / bbox.height
        }
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        if self.model is None:
            return {"status": "模型未加载"}
        
        return {
            "model_type": "YOLOv8",
            "model_path": settings.MODEL_PATH,
            "classes": list(self.model.names.values()) if self.model.names else [],
            "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
            "iou_threshold": settings.IOU_THRESHOLD
        }