from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.models.violation_types import ViolationCategory, ViolationSeverity, ViolationStatus

Base = declarative_base()

class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    detection_results = relationship("DetectionResultDB", back_populates="user", cascade="all, delete-orphan")

class DetectionResultDB(Base):
    """检测结果表"""
    __tablename__ = "detection_results"
    
    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String(500), nullable=False)
    image_filename = Column(String(255), nullable=False)
    image_size = Column(Integer)  # 文件大小（字节）
    image_width = Column(Integer)
    image_height = Column(Integer)
    image_format = Column(String(20))
    
    total_violations = Column(Integer, default=0)
    confidence_threshold = Column(Float, default=0.5)
    iou_threshold = Column(Float, default=0.45)
    processing_time = Column(Float)  # 处理耗时（秒）
    
    status = Column(Enum(ViolationStatus), default=ViolationStatus.DETECTED)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 外键
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # JSON字段存储额外信息
  # metadata = Column(JSON)
    extra_metadata = Column("metadata", JSON)
    
    # 关系
    user = relationship("User", back_populates="detection_results")
    detections = relationship("ViolationDetectionDB", back_populates="result", cascade="all, delete-orphan")

class ViolationDetectionDB(Base):
    """违章检测详情表"""
    __tablename__ = "violation_detections"
    
    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("detection_results.id"), nullable=False)
    
    class_id = Column(Integer, nullable=False)
    class_name = Column(String(100), nullable=False)
    violation_category = Column(Enum(ViolationCategory))
    confidence = Column(Float, nullable=False)
    
    # 边界框信息
    bbox_x = Column(Float, nullable=False)
    bbox_y = Column(Float, nullable=False)
    bbox_width = Column(Float, nullable=False)
    bbox_height = Column(Float, nullable=False)
    area = Column(Float, nullable=False)
    
    # 违章信息
    severity = Column(Enum(ViolationSeverity))
    description = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    
    # 关系
    result = relationship("DetectionResultDB", back_populates="detections")

class SystemLog(Base):
    """系统日志表"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)  # 操作类型
    resource = Column(String(100))  # 操作资源
    resource_id = Column(Integer)  # 资源ID
    ip_address = Column(String(45))  # IP地址
    user_agent = Column(String(500))  # 用户代理
    status_code = Column(Integer)  # 状态码
    message = Column(Text)  # 详细信息
    created_at = Column(DateTime, default=func.now())
    
    # 关系
    user = relationship("User")

class ViolationStatisticsDB(Base):
    """违章统计表"""
    __tablename__ = "violation_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    
    total_detections = Column(Integer, default=0)
    total_violations = Column(Integer, default=0)
    
    # 按严重程度统计
    low_severity_count = Column(Integer, default=0)
    medium_severity_count = Column(Integer, default=0)
    high_severity_count = Column(Integer, default=0)
    critical_severity_count = Column(Integer, default=0)
    
    # 按类别统计 (JSON格式存储详细分布)
    category_distribution = Column(JSON)
    severity_distribution = Column(JSON)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
