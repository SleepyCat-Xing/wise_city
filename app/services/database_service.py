from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, asc
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.models.database import DetectionResultDB, ViolationDetectionDB, User, SystemLog, ViolationStatisticsDB
from app.models.detection import DetectionResult, ViolationDetection, ImageInfo
from app.models.violation_types import ViolationCategory, ViolationSeverity, ViolationStatus

logger = logging.getLogger(__name__)

class DatabaseService:
    """数据库服务类"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_detection_result(self, result: DetectionResult, user_id: Optional[int] = None) -> int:
        """保存检测结果到数据库"""
        try:
            # 创建主记录
            db_result = DetectionResultDB(
                image_path=result.image_path,
                image_filename=result.image_info.filename if result.image_info else "",
                image_size=result.image_info.file_size if result.image_info else 0,
                image_width=result.image_info.width if result.image_info else 0,
                image_height=result.image_info.height if result.image_info else 0,
                image_format=result.image_info.format if result.image_info else "",
                total_violations=result.total_violations,
                confidence_threshold=result.confidence_threshold,
                iou_threshold=result.iou_threshold,
                processing_time=result.processing_time,
                status=result.status,
                user_id=user_id,
                metadata=result.metadata
            )
            
            self.session.add(db_result)
            await self.session.flush()  # 获取ID
            
            # 保存检测详情
            for detection in result.detections:
                db_detection = ViolationDetectionDB(
                    result_id=db_result.id,
                    class_id=detection.class_id,
                    class_name=detection.class_name,
                    violation_category=detection.violation_category,
                    confidence=detection.confidence,
                    bbox_x=detection.bbox.x,
                    bbox_y=detection.bbox.y,
                    bbox_width=detection.bbox.width,
                    bbox_height=detection.bbox.height,
                    area=detection.area,
                    severity=detection.severity,
                    description=detection.description
                )
                self.session.add(db_detection)
            
            await self.session.commit()
            logger.info(f"保存检测结果: ID={db_result.id}, 违章数={result.total_violations}")
            return db_result.id
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"保存检测结果失败: {str(e)}")
            raise
    
    async def get_detection_result(self, result_id: int) -> Optional[DetectionResult]:
        """根据ID获取检测结果"""
        try:
            query = select(DetectionResultDB).options(
                selectinload(DetectionResultDB.detections)
            ).where(DetectionResultDB.id == result_id)
            
            result = await self.session.execute(query)
            db_result = result.scalar_one_or_none()
            
            if not db_result:
                return None
            
            # 转换为Pydantic模型
            return await self._convert_db_to_pydantic(db_result)
            
        except Exception as e:
            logger.error(f"获取检测结果失败: {str(e)}")
            raise
    
    async def list_detection_results(
        self, 
        user_id: Optional[int] = None,
        status: Optional[ViolationStatus] = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> List[DetectionResult]:
        """获取检测结果列表"""
        try:
            query = select(DetectionResultDB).options(
                selectinload(DetectionResultDB.detections)
            )
            
            # 筛选条件
            if user_id:
                query = query.where(DetectionResultDB.user_id == user_id)
            if status:
                query = query.where(DetectionResultDB.status == status)
            
            # 排序
            if order_desc:
                query = query.order_by(desc(getattr(DetectionResultDB, order_by)))
            else:
                query = query.order_by(asc(getattr(DetectionResultDB, order_by)))
            
            # 分页
            query = query.offset(skip).limit(limit)
            
            result = await self.session.execute(query)
            db_results = result.scalars().all()
            
            # 转换为Pydantic模型
            results = []
            for db_result in db_results:
                pydantic_result = await self._convert_db_to_pydantic(db_result)
                results.append(pydantic_result)
            
            return results
            
        except Exception as e:
            logger.error(f"获取检测结果列表失败: {str(e)}")
            raise
    
    async def get_detection_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取检测统计信息"""
        try:
            # 构建基础查询
            base_query = select(DetectionResultDB).options(
                selectinload(DetectionResultDB.detections)
            )
            
            # 时间筛选
            if start_date:
                base_query = base_query.where(DetectionResultDB.created_at >= start_date)
            if end_date:
                base_query = base_query.where(DetectionResultDB.created_at <= end_date)
            if user_id:
                base_query = base_query.where(DetectionResultDB.user_id == user_id)
            
            # 执行查询
            result = await self.session.execute(base_query)
            db_results = result.scalars().all()
            
            # 统计信息
            total_detections = len(db_results)
            total_violations = sum(r.total_violations for r in db_results)
            
            # 按严重程度统计
            severity_count = {}
            category_count = {}
            
            for db_result in db_results:
                for detection in db_result.detections:
                    if detection.severity:
                        severity = detection.severity.value
                        severity_count[severity] = severity_count.get(severity, 0) + 1
                    
                    if detection.violation_category:
                        category = detection.violation_category.value
                        category_count[category] = category_count.get(category, 0) + 1
            
            # 每日统计（最近7天）
            daily_stats = {}
            if start_date and end_date:
                current_date = start_date
                while current_date <= end_date:
                    day_str = current_date.strftime('%Y-%m-%d')
                    day_count = sum(1 for r in db_results 
                                  if r.created_at.date() == current_date.date())
                    daily_stats[day_str] = day_count
                    current_date += timedelta(days=1)
            
            return {
                "total_detections": total_detections,
                "total_violations": total_violations,
                "avg_violations_per_detection": total_violations / max(total_detections, 1),
                "severity_distribution": severity_count,
                "category_distribution": category_count,
                "daily_stats": daily_stats,
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                }
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            raise
    
    async def update_detection_status(self, result_id: int, status: ViolationStatus) -> bool:
        """更新检测结果状态"""
        try:
            query = select(DetectionResultDB).where(DetectionResultDB.id == result_id)
            result = await self.session.execute(query)
            db_result = result.scalar_one_or_none()
            
            if not db_result:
                return False
            
            db_result.status = status
            db_result.updated_at = datetime.utcnow()
            
            await self.session.commit()
            logger.info(f"更新检测结果状态: ID={result_id}, 状态={status.value}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"更新检测结果状态失败: {str(e)}")
            raise
    
    async def delete_detection_result(self, result_id: int) -> bool:
        """删除检测结果"""
        try:
            query = select(DetectionResultDB).where(DetectionResultDB.id == result_id)
            result = await self.session.execute(query)
            db_result = result.scalar_one_or_none()
            
            if not db_result:
                return False
            
            await self.session.delete(db_result)
            await self.session.commit()
            logger.info(f"删除检测结果: ID={result_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"删除检测结果失败: {str(e)}")
            raise
    
    async def log_system_action(
        self,
        user_id: Optional[int],
        action: str,
        resource: Optional[str] = None,
        resource_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status_code: int = 200,
        message: Optional[str] = None
    ):
        """记录系统操作日志"""
        try:
            log_entry = SystemLog(
                user_id=user_id,
                action=action,
                resource=resource,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                status_code=status_code,
                message=message
            )
            
            self.session.add(log_entry)
            await self.session.commit()
            
        except Exception as e:
            logger.error(f"记录系统日志失败: {str(e)}")
            # 日志记录失败不应该影响主要业务流程
    
    async def _convert_db_to_pydantic(self, db_result: DetectionResultDB) -> DetectionResult:
        """将数据库模型转换为Pydantic模型"""
        # 转换图像信息
        image_info = ImageInfo(
            filename=db_result.image_filename,
            file_size=db_result.image_size or 0,
            width=db_result.image_width or 0,
            height=db_result.image_height or 0,
            format=db_result.image_format or "",
            upload_time=db_result.created_at
        ) if db_result.image_filename else None
        
        # 转换检测结果
        detections = []
        for db_detection in db_result.detections:
            from app.models.detection import BoundingBox
            
            bbox = BoundingBox(
                x=db_detection.bbox_x,
                y=db_detection.bbox_y,
                width=db_detection.bbox_width,
                height=db_detection.bbox_height
            )
            
            detection = ViolationDetection(
                class_id=db_detection.class_id,
                class_name=db_detection.class_name,
                violation_category=db_detection.violation_category,
                confidence=db_detection.confidence,
                bbox=bbox,
                area=db_detection.area,
                severity=db_detection.severity,
                description=db_detection.description
            )
            detections.append(detection)
        
        return DetectionResult(
            id=db_result.id,
            image_path=db_result.image_path,
            image_info=image_info,
            detections=detections,
            total_violations=db_result.total_violations,
            confidence_threshold=db_result.confidence_threshold,
            iou_threshold=db_result.iou_threshold,
            processing_time=db_result.processing_time,
            created_at=db_result.created_at,
            status=db_result.status,
            metadata=db_result.metadata
        )