from enum import Enum
from typing import Dict, List
from pydantic import BaseModel

class ViolationCategory(str, Enum):
    """违章建筑类别枚举"""
    # 主要违章类型
    ILLEGAL_CONSTRUCTION = "illegal_construction"  # 违法建设
    UNAUTHORIZED_EXTENSION = "unauthorized_extension"  # 未经批准扩建
    ROOFTOP_ADDITION = "rooftop_addition"  # 楼顶加建
    BALCONY_ENCLOSURE = "balcony_enclosure"  # 阳台封闭
    TEMPORARY_STRUCTURE = "temporary_structure"  # 临时建筑超期
    
    # 细分类型
    SHED_STRUCTURE = "shed_structure"  # 违建棚屋
    CONTAINER_HOUSE = "container_house"  # 集装箱房屋
    UNAUTHORIZED_WAREHOUSE = "unauthorized_warehouse"  # 无证仓库
    ILLEGAL_FENCE = "illegal_fence"  # 违规围墙
    UNAUTHORIZED_PARKING = "unauthorized_parking"  # 违规停车棚
    
    # 商业违建
    ILLEGAL_SIGNAGE = "illegal_signage"  # 违规广告牌
    UNAUTHORIZED_STOREFRONT = "unauthorized_storefront"  # 违规门面房
    ILLEGAL_MARKET_STALL = "illegal_market_stall"  # 违规市场摊位

class ViolationSeverity(str, Enum):
    """违章建筑严重程度"""
    LOW = "low"  # 轻微违章
    MEDIUM = "medium"  # 一般违章
    HIGH = "high"  # 严重违章
    CRITICAL = "critical"  # 极严重违章

class ViolationStatus(str, Enum):
    """违章建筑处理状态"""
    DETECTED = "detected"  # 已检测
    CONFIRMED = "confirmed"  # 已确认
    IN_PROCESSING = "in_processing"  # 处理中
    RECTIFIED = "rectified"  # 已整改
    DEMOLISHED = "demolished"  # 已拆除
    PENDING_REVIEW = "pending_review"  # 待复查

class ViolationInfo(BaseModel):
    """违章建筑信息模型"""
    category: ViolationCategory
    chinese_name: str
    description: str
    severity_level: ViolationSeverity
    typical_features: List[str]
    common_locations: List[str]
    legal_basis: str

# 违章建筑类别详细信息
VIOLATION_CATEGORIES_INFO: Dict[ViolationCategory, ViolationInfo] = {
    ViolationCategory.ILLEGAL_CONSTRUCTION: ViolationInfo(
        category=ViolationCategory.ILLEGAL_CONSTRUCTION,
        chinese_name="违法建设",
        description="未经规划许可或违反规划许可内容进行的建设活动",
        severity_level=ViolationSeverity.HIGH,
        typical_features=["无规划许可", "超出批准范围", "改变建筑用途"],
        common_locations=["城市边缘", "农村地区", "工业区"],
        legal_basis="《城乡规划法》第六十四条"
    ),
    
    ViolationCategory.UNAUTHORIZED_EXTENSION: ViolationInfo(
        category=ViolationCategory.UNAUTHORIZED_EXTENSION,
        chinese_name="未经批准扩建",
        description="在原有建筑基础上未经批准进行的扩建活动",
        severity_level=ViolationSeverity.MEDIUM,
        typical_features=["原建筑扩大", "新增建筑面积", "改变原有结构"],
        common_locations=["住宅区", "商业区", "厂房周边"],
        legal_basis="《建筑法》第七条"
    ),
    
    ViolationCategory.ROOFTOP_ADDITION: ViolationInfo(
        category=ViolationCategory.ROOFTOP_ADDITION,
        chinese_name="楼顶加建",
        description="在建筑物顶部未经批准加建的结构物",
        severity_level=ViolationSeverity.HIGH,
        typical_features=["楼顶新建", "彩钢板房", "简易房屋"],
        common_locations=["多层住宅", "商业楼宇", "办公建筑"],
        legal_basis="《城乡规划法》第四十条"
    ),
    
    ViolationCategory.BALCONY_ENCLOSURE: ViolationInfo(
        category=ViolationCategory.BALCONY_ENCLOSURE,
        chinese_name="阳台封闭",
        description="未经批准封闭原设计为开放式的阳台",
        severity_level=ViolationSeverity.LOW,
        typical_features=["玻璃封窗", "增加面积", "改变外观"],
        common_locations=["住宅小区", "公寓楼", "办公建筑"],
        legal_basis="《物业管理条例》第五十三条"
    ),
    
    ViolationCategory.TEMPORARY_STRUCTURE: ViolationInfo(
        category=ViolationCategory.TEMPORARY_STRUCTURE,
        chinese_name="临时建筑超期",
        description="超过批准使用期限仍在使用的临时建筑",
        severity_level=ViolationSeverity.MEDIUM,
        typical_features=["超期使用", "临时变永久", "简易材料"],
        common_locations=["建设工地", "市场周边", "空地"],
        legal_basis="《城乡规划法》第四十五条"
    ),
    
    ViolationCategory.SHED_STRUCTURE: ViolationInfo(
        category=ViolationCategory.SHED_STRUCTURE,
        chinese_name="违建棚屋",
        description="未经批准搭建的简易棚屋结构",
        severity_level=ViolationSeverity.MEDIUM,
        typical_features=["简易材料", "临时搭建", "功能单一"],
        common_locations=["城中村", "农贸市场", "工地周边"],
        legal_basis="《城乡规划法》第六十四条"
    ),
    
    ViolationCategory.CONTAINER_HOUSE: ViolationInfo(
        category=ViolationCategory.CONTAINER_HOUSE,
        chinese_name="集装箱房屋",
        description="未经批准使用集装箱改建的房屋",
        severity_level=ViolationSeverity.MEDIUM,
        typical_features=["集装箱改造", "可移动", "标准化"],
        common_locations=["工地", "临时办公", "商业区"],
        legal_basis="《建筑法》第十三条"
    ),
    
    ViolationCategory.UNAUTHORIZED_WAREHOUSE: ViolationInfo(
        category=ViolationCategory.UNAUTHORIZED_WAREHOUSE,
        chinese_name="无证仓库",
        description="未经规划和建设部门批准建设的仓库",
        severity_level=ViolationSeverity.HIGH,
        typical_features=["大跨度结构", "存储功能", "无证经营"],
        common_locations=["工业区", "物流园", "城乡结合部"],
        legal_basis="《城乡规划法》第三十八条"
    ),
    
    ViolationCategory.ILLEGAL_FENCE: ViolationInfo(
        category=ViolationCategory.ILLEGAL_FENCE,
        chinese_name="违规围墙",
        description="未经批准或超出规定高度的围墙",
        severity_level=ViolationSeverity.LOW,
        typical_features=["超高围墙", "封闭通道", "影响通行"],
        common_locations=["住宅区", "工厂", "学校"],
        legal_basis="《城乡规划法》第四十一条"
    ),
    
    ViolationCategory.UNAUTHORIZED_PARKING: ViolationInfo(
        category=ViolationCategory.UNAUTHORIZED_PARKING,
        chinese_name="违规停车棚",
        description="未经批准搭建的停车棚或车库",
        severity_level=ViolationSeverity.LOW,
        typical_features=["遮雨功能", "钢结构", "占用空地"],
        common_locations=["小区内", "路边", "空地"],
        legal_basis="《物业管理条例》第五十三条"
    ),
    
    ViolationCategory.ILLEGAL_SIGNAGE: ViolationInfo(
        category=ViolationCategory.ILLEGAL_SIGNAGE,
        chinese_name="违规广告牌",
        description="未经批准设置的大型广告牌或招牌",
        severity_level=ViolationSeverity.MEDIUM,
        typical_features=["大型招牌", "影响市容", "安全隐患"],
        common_locations=["商业街", "主干道", "建筑外墙"],
        legal_basis="《广告法》第四十二条"
    ),
    
    ViolationCategory.UNAUTHORIZED_STOREFRONT: ViolationInfo(
        category=ViolationCategory.UNAUTHORIZED_STOREFRONT,
        chinese_name="违规门面房",
        description="未经批准改建或扩建的商业门面",
        severity_level=ViolationSeverity.MEDIUM,
        typical_features=["改变用途", "外扩经营", "占道经营"],
        common_locations=["商业街", "住宅底层", "市场周边"],
        legal_basis="《城乡规划法》第四十条"
    ),
    
    ViolationCategory.ILLEGAL_MARKET_STALL: ViolationInfo(
        category=ViolationCategory.ILLEGAL_MARKET_STALL,
        chinese_name="违规市场摊位",
        description="未经批准搭建的市场摊位或售货亭",
        severity_level=ViolationSeverity.LOW,
        typical_features=["临时摊位", "占用公共空间", "简易结构"],
        common_locations=["市场内", "街道旁", "广场"],
        legal_basis="《城市市容和环境卫生管理条例》"
    )
}

def get_violation_info(category: ViolationCategory) -> ViolationInfo:
    """获取违章类别信息"""
    return VIOLATION_CATEGORIES_INFO.get(category)

def get_all_violation_categories() -> List[str]:
    """获取所有违章类别名称"""
    return [cat.value for cat in ViolationCategory]

def get_severity_color(severity: ViolationSeverity) -> str:
    """根据严重程度获取颜色代码"""
    color_map = {
        ViolationSeverity.LOW: "#28a745",      # 绿色
        ViolationSeverity.MEDIUM: "#ffc107",   # 黄色
        ViolationSeverity.HIGH: "#fd7e14",     # 橙色
        ViolationSeverity.CRITICAL: "#dc3545"  # 红色
    }
    return color_map.get(severity, "#6c757d")  # 默认灰色