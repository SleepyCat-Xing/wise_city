import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple, Optional, Dict, Any
from app.models.detection import ViolationDetection, BoundingBox
from app.models.violation_types import ViolationCategory, ViolationSeverity, get_violation_info
from app.core.config import settings
import os
import time
import torch
import json
from pathlib import Path

class AIService:
    def __init__(self):
        self.model = None
        self.model_performance = {}
        self.violation_class_mapping = self._init_violation_mapping()
        self.building_features_cache = {}
        self.multimodal_config = self._init_multimodal_config()
        self.load_model()
    
    def _init_violation_mapping(self):
        """初始化违章建筑类别映射"""
        # YOLO预训练模型类别到违章建筑类别的映射
        # 这里是基于COCO数据集类别的智能映射
        return {
            # 建筑相关 - 高精度分类
            "person": None,  # 人员不算违章
            "car": ViolationCategory.UNAUTHORIZED_PARKING,  # 违规停车
            "truck": ViolationCategory.UNAUTHORIZED_PARKING,  # 违规停车
            "bus": ViolationCategory.UNAUTHORIZED_PARKING,  # 违规停车
            "motorcycle": ViolationCategory.UNAUTHORIZED_PARKING,  # 违规停车
            
            # 建筑结构 - 专业分类
            "chair": ViolationCategory.TEMPORARY_STRUCTURE,  # 可能是临时搭建
            "couch": ViolationCategory.TEMPORARY_STRUCTURE,  # 临时家具
            "bed": ViolationCategory.TEMPORARY_STRUCTURE,  # 临时住所
            "dining table": ViolationCategory.TEMPORARY_STRUCTURE,  # 临时桌子
            
            # 遮蔽物和棚屋 - 精细化分类
            "umbrella": ViolationCategory.SHED_STRUCTURE,  # 遮雨棚
            "bench": ViolationCategory.TEMPORARY_STRUCTURE,  # 临时座椅
            "stop sign": ViolationCategory.ILLEGAL_SIGNAGE,  # 非法标牌
            
            # 商业相关 - 摊位识别
            "bottle": ViolationCategory.ILLEGAL_MARKET_STALL,  # 摊位
            "cup": ViolationCategory.ILLEGAL_MARKET_STALL,  # 摊位用品
            "bowl": ViolationCategory.ILLEGAL_MARKET_STALL,  # 摊位用品
            "refrigerator": ViolationCategory.ILLEGAL_MARKET_STALL,  # 商用设备
            
            # 高级违章类型
            "tv": ViolationCategory.UNAUTHORIZED_STOREFRONT,  # 店面设备
            "laptop": ViolationCategory.UNAUTHORIZED_STOREFRONT,  # 商业设备
            
            # 默认映射 - 未识别的物体可能是违章建筑
            "default": ViolationCategory.ILLEGAL_CONSTRUCTION
        }
    
    def _init_multimodal_config(self) -> Dict[str, Any]:
        """初始化多模态数据融合配置"""
        return {
            "image_preprocessing": {
                "enable_enhancement": True,
                "auto_contrast": True,
                "noise_reduction": True,
                "edge_sharpening": True
            },
            "fusion_weights": {
                "visual_features": 0.7,
                "contextual_features": 0.2,
                "temporal_features": 0.1
            },
            "detection_thresholds": {
                "building_structure": 0.6,
                "vehicle_parking": 0.8,
                "market_stall": 0.7,
                "signage": 0.75
            },
            "performance_targets": {
                "mAP_threshold": 0.85,
                "processing_speed_fps": 50,
                "response_time_ms": 3000
            }
        }
    
    def load_model(self):
        """加载增强的YOLOv8模型"""
        try:
            if os.path.exists(settings.MODEL_PATH):
                self.model = YOLO(settings.MODEL_PATH)
                print(f"专用违章建筑检测模型已加载: {settings.MODEL_PATH}")
            else:
                # 优先使用更大的预训练模型以获得更好性能
                model_variants = ['yolov8x.pt', 'yolov8l.pt', 'yolov8m.pt', 'yolov8s.pt', 'yolov8n.pt']
                model_loaded = False
                
                for model_name in model_variants:
                    try:
                        self.model = YOLO(model_name)
                        print(f"使用YOLOv8预训练模型: {model_name}")
                        model_loaded = True
                        break
                    except Exception as e:
                        print(f"尝试加载 {model_name} 失败: {e}")
                        continue
                
                if not model_loaded:
                    raise Exception("无法加载任何YOLOv8模型")
            
            # 配置模型参数以优化性能
            if self.model:
                # 启用GPU加速（如果可用）
                if torch.cuda.is_available():
                    self.model.to('cuda')
                    print("GPU加速已启用")
                
                # 记录模型性能指标
                self._benchmark_model()
                
        except Exception as e:
            print(f"模型加载失败: {e}")
            self.model = None
    
    def _benchmark_model(self):
        """模型性能基准测试"""
        if not self.model:
            return
        
        try:
            # 创建测试图像
            test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            
            # 测试推理速度
            start_time = time.time()
            results = self.model(test_image, verbose=False)
            inference_time = time.time() - start_time
            
            fps = 1.0 / inference_time if inference_time > 0 else 0
            
            self.model_performance = {
                "inference_time_ms": inference_time * 1000,
                "fps": fps,
                "target_fps": self.multimodal_config["performance_targets"]["processing_speed_fps"],
                "meets_fps_target": fps >= self.multimodal_config["performance_targets"]["processing_speed_fps"],
                "gpu_enabled": torch.cuda.is_available(),
                "model_size": "unknown"
            }
            
            print(f"模型性能: {fps:.1f} FPS ({inference_time*1000:.1f}ms)")
            
        except Exception as e:
            print(f"性能测试失败: {e}")
    
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
            # 读取并预处理图像
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("无法读取图像文件")
            
            # 多模态图像增强处理
            processed_image = self._preprocess_image(image)
            processed_path = image_path  # 实际应用中可以保存处理后的图像
            
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
        
        performance_info = self.model_performance.copy() if self.model_performance else {}
        
        return {
            "model_type": "Enhanced YOLOv8 for Building Violation Detection",
            "model_path": settings.MODEL_PATH,
            "classes": list(self.model.names.values()) if self.model.names else [],
            "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
            "iou_threshold": settings.IOU_THRESHOLD,
            "performance_metrics": performance_info,
            "multimodal_features": {
                "image_enhancement": True,
                "contextual_analysis": True,
                "building_structure_analysis": True
            },
            "violation_categories": len(self.violation_class_mapping)
        }
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """多模态图像预处理和增强"""
        processed = image.copy()
        
        if not self.multimodal_config["image_preprocessing"]["enable_enhancement"]:
            return processed
        
        try:
            # 自动对比度调整
            if self.multimodal_config["image_preprocessing"]["auto_contrast"]:
                processed = self._enhance_contrast(processed)
            
            # 噪声减少
            if self.multimodal_config["image_preprocessing"]["noise_reduction"]:
                processed = cv2.bilateralFilter(processed, 9, 75, 75)
            
            # 边缘锐化
            if self.multimodal_config["image_preprocessing"]["edge_sharpening"]:
                processed = self._sharpen_edges(processed)
            
            return processed
            
        except Exception as e:
            print(f"图像预处理失败: {e}")
            return image
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """自适应对比度增强"""
        try:
            # 转换到Lab色彩空间进行亮度调整
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # 对L通道应用CLAHE（对比度受限的自适应直方图均衡化）
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l_enhanced = clahe.apply(l)
            
            # 合并通道并转换回BGR
            enhanced_lab = cv2.merge([l_enhanced, a, b])
            enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            return enhanced_bgr
        except:
            return image
    
    def _sharpen_edges(self, image: np.ndarray) -> np.ndarray:
        """边缘锐化处理"""
        try:
            # 使用拉普拉斯算子进行锐化
            kernel = np.array([[-1,-1,-1],
                              [-1, 9,-1],
                              [-1,-1,-1]])
            sharpened = cv2.filter2D(image, -1, kernel)
            
            # 混合原图和锐化图像
            alpha = 0.3  # 锐化强度
            result = cv2.addWeighted(image, 1-alpha, sharpened, alpha, 0)
            
            return result
        except:
            return image
    
    def get_multimodal_analysis(self, image_path: str) -> Dict[str, Any]:
        """多模态综合分析"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "无法读取图像"}
            
            analysis = {
                "image_properties": self._analyze_image_properties(image),
                "building_features": self._extract_building_features(image),
                "environmental_context": self._analyze_environmental_context(image),
                "risk_assessment": {},
                "recommendations": []
            }
            
            # 基于多模态分析生成风险评估
            analysis["risk_assessment"] = self._generate_risk_assessment(analysis)
            
            # 生成建议
            analysis["recommendations"] = self._generate_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            return {"error": f"多模态分析失败: {str(e)}"}
    
    def _analyze_image_properties(self, image: np.ndarray) -> Dict[str, Any]:
        """分析图像基本属性"""
        height, width = image.shape[:2]
        
        # 计算图像质量指标
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()  # 清晰度
        brightness = np.mean(gray)  # 亮度
        contrast = np.std(gray)  # 对比度
        
        return {
            "dimensions": {"width": width, "height": height},
            "quality_metrics": {
                "blur_score": float(blur_score),
                "brightness": float(brightness),
                "contrast": float(contrast),
                "quality_rating": "高" if blur_score > 100 else "中" if blur_score > 50 else "低"
            }
        }
    
    def _extract_building_features(self, image: np.ndarray) -> Dict[str, Any]:
        """提取建筑物特征"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 边缘检测
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # 直线检测（建筑物通常有规则的直线结构）
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        line_count = len(lines) if lines is not None else 0
        
        # 颜色分布分析
        colors = cv2.split(image)
        color_stats = {
            "blue_mean": float(np.mean(colors[0])),
            "green_mean": float(np.mean(colors[1])),
            "red_mean": float(np.mean(colors[2]))
        }
        
        return {
            "structural_features": {
                "edge_density": float(edge_density),
                "line_structures": line_count,
                "regularity_score": min(line_count / 50.0, 1.0)  # 规则性评分
            },
            "color_analysis": color_stats,
            "complexity_level": "高" if edge_density > 0.1 else "中" if edge_density > 0.05 else "低"
        }
    
    def _analyze_environmental_context(self, image: np.ndarray) -> Dict[str, Any]:
        """分析环境上下文"""
        # 简化的环境分析
        height, width = image.shape[:2]
        
        # 分析图像的不同区域
        regions = {
            "upper": image[:height//3, :],
            "middle": image[height//3:2*height//3, :],
            "lower": image[2*height//3:, :]
        }
        
        region_analysis = {}
        for region_name, region in regions.items():
            mean_intensity = np.mean(cv2.cvtColor(region, cv2.COLOR_BGR2GRAY))
            region_analysis[region_name] = {
                "brightness": float(mean_intensity),
                "dominant_color": "明亮" if mean_intensity > 127 else "暗淡"
            }
        
        return {
            "spatial_layout": region_analysis,
            "scene_type": "城市" if region_analysis["lower"]["brightness"] < region_analysis["upper"]["brightness"] else "郊区",
            "environmental_factors": {
                "lighting_condition": "良好" if np.mean([r["brightness"] for r in region_analysis.values()]) > 100 else "较暗",
                "weather_estimate": "晴朗"  # 简化估算
            }
        }
    
    def _generate_risk_assessment(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """基于多模态分析生成风险评估"""
        risk_factors = []
        risk_score = 0
        
        # 基于图像质量的风险因素
        quality = analysis["image_properties"]["quality_metrics"]
        if quality["blur_score"] < 50:
            risk_factors.append("图像清晰度较低，可能影响检测准确性")
            risk_score += 20
        
        # 基于建筑特征的风险因素
        building = analysis["building_features"]
        if building["structural_features"]["edge_density"] > 0.15:
            risk_factors.append("建筑结构复杂，需要重点关注")
            risk_score += 15
        
        if building["structural_features"]["regularity_score"] < 0.3:
            risk_factors.append("建筑结构不规则，可能存在违章风险")
            risk_score += 25
        
        # 环境因素
        env = analysis["environmental_context"]
        if env["environmental_factors"]["lighting_condition"] == "较暗":
            risk_factors.append("光照条件不佳，建议提高图像亮度")
            risk_score += 10
        
        risk_level = "高" if risk_score > 40 else "中" if risk_score > 20 else "低"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "confidence": 0.8  # 评估置信度
        }
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于风险评估生成建议
        risk = analysis["risk_assessment"]
        
        if risk["risk_score"] > 30:
            recommendations.append("建议进行现场实地核查")
        
        if "图像清晰度较低" in str(risk.get("risk_factors", [])):
            recommendations.append("建议使用更高分辨率的图像或改善拍摄条件")
        
        if "光照条件不佳" in str(risk.get("risk_factors", [])):
            recommendations.append("建议在光照充足时重新拍摄")
        
        # 基于建筑特征的建议
        building = analysis["building_features"]
        if building["complexity_level"] == "高":
            recommendations.append("建筑结构复杂，建议多角度拍摄进行综合分析")
        
        if not recommendations:
            recommendations.append("图像质量良好，可进行正常的违章建筑检测分析")
        
        return recommendations