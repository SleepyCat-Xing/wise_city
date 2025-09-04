#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法规知识库数据模型
智慧城管系统 - 法规解读功能
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime


class RegulationLevel(Enum):
    """法规层级"""
    NATIONAL = "国家法律法规"
    PROVINCIAL = "省级法规"
    MUNICIPAL = "市级法规"
    LOCAL = "地方条例"


class ViolationType(Enum):
    """违章类型枚举"""
    ILLEGAL_CONSTRUCTION = "illegal_construction"
    UNAUTHORIZED_PARKING = "unauthorized_parking"  
    TEMPORARY_STRUCTURE = "temporary_structure"
    SHED_STRUCTURE = "shed_structure"
    ILLEGAL_MARKET_STALL = "illegal_market_stall"
    UNAUTHORIZED_STOREFRONT = "unauthorized_storefront"
    ILLEGAL_FENCE = "illegal_fence"
    ILLEGAL_SIGNAGE = "illegal_signage"


class LegalRegulation(BaseModel):
    """法规条文模型"""
    regulation_id: str
    title: str
    content: str
    level: RegulationLevel
    effective_date: datetime
    applicable_violations: List[ViolationType]
    penalty_description: str
    enforcement_procedure: str
    keywords: List[str]
    
    class Config:
        use_enum_values = True


class ViolationLegalBasis(BaseModel):
    """违章建筑法律依据模型"""
    violation_type: ViolationType
    primary_regulations: List[LegalRegulation]
    applicable_penalties: Dict[str, Any]
    enforcement_guidelines: str
    typical_cases: List[str]
    
    class Config:
        use_enum_values = True


class LegalAdvice(BaseModel):
    """法律建议模型"""
    violation_type: ViolationType
    severity_level: str
    applicable_laws: List[str]
    recommended_actions: List[str]
    penalty_range: str
    legal_basis: str
    enforcement_priority: int  # 1-5, 5为最高优先级
    
    class Config:
        use_enum_values = True


# 法规知识库数据
LEGAL_REGULATIONS_DATABASE = {
    "building_construction": [
        LegalRegulation(
            regulation_id="UCL_001",
            title="中华人民共和国城乡规划法",
            content="第六十四条：未取得建设工程规划许可证或者未按照建设工程规划许可证的规定进行建设的，由县级以上地方人民政府城乡规划主管部门责令停止建设。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(2008, 1, 1),
            applicable_violations=[ViolationType.ILLEGAL_CONSTRUCTION],
            penalty_description="责令停止建设；尚可采取改正措施消除对规划实施的影响的，限期改正，处建设工程造价百分之五以上百分之十以下的罚款；无法采取改正措施消除影响的，限期拆除，不能拆除的，没收实物或者违法收入，可以并处建设工程造价百分之十以下的罚款。",
            enforcement_procedure="发现→调查取证→责令停止→限期整改→执行处罚",
            keywords=["建设工程规划许可证", "违法建设", "城乡规划"]
        ),
        LegalRegulation(
            regulation_id="UCL_002", 
            title="城市市容和环境卫生管理条例",
            content="第三十六条：有下列行为之一的，由城市人民政府市容环境卫生行政主管部门或者其委托的单位责令停止违法行为，限期清理、拆除或者采取其他补救措施，并可处以罚款。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(1992, 8, 1), 
            applicable_violations=[ViolationType.TEMPORARY_STRUCTURE, ViolationType.ILLEGAL_MARKET_STALL],
            penalty_description="责令停止违法行为，限期清理、拆除或者采取其他补救措施，并可处以罚款。",
            enforcement_procedure="发现违法→责令停止→限期整改→执行处罚",
            keywords=["市容环境", "临时建筑", "违法搭建"]
        )
    ],
    "parking_violations": [
        LegalRegulation(
            regulation_id="TRF_001",
            title="中华人民共和国道路交通安全法",
            content="第五十六条：机动车应当在规定地点停放。禁止在人行道、车行道、无障碍通道上停放机动车；但是，停车场、停车泊位外及依法施划的临时停车泊位外，任何单位和个人不得设置固定或者可移动的障碍物阻止机动车停放。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(2004, 5, 1),
            applicable_violations=[ViolationType.UNAUTHORIZED_PARKING],
            penalty_description="由公安机关交通管理部门处二十元以上二百元以下罚款；情节严重的，处二百元以上二千元以下罚款。",
            enforcement_procedure="发现违法→拍照取证→告知处罚→执行处罚",
            keywords=["机动车停放", "违法停车", "道路交通"]
        )
    ],
    "commercial_violations": [
        LegalRegulation(
            regulation_id="COM_001",
            title="城市道路管理条例",
            content="第二十七条：任何单位和个人不得擅自占用城市道路。因特殊需要临时占用城市道路的，须经市政工程行政主管部门和公安交通管理部门批准。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(1996, 10, 1),
            applicable_violations=[ViolationType.ILLEGAL_MARKET_STALL, ViolationType.UNAUTHORIZED_STOREFRONT],
            penalty_description="责令限期清除占用物，恢复城市道路原状，并可处以二万元以下的罚款。",
            enforcement_procedure="发现违法→调查核实→责令清除→执行处罚",
            keywords=["占用道路", "临时占用", "摊点经营"]
        )
    ]
}


class LegalKnowledgeBase:
    """法规知识库"""
    
    def __init__(self):
        self.regulations = LEGAL_REGULATIONS_DATABASE
        self.violation_mapping = self._build_violation_mapping()
    
    def _build_violation_mapping(self) -> Dict[ViolationType, List[LegalRegulation]]:
        """构建违章类型到法规的映射"""
        mapping = {}
        
        for category, regulations in self.regulations.items():
            for regulation in regulations:
                for violation_type in regulation.applicable_violations:
                    if violation_type not in mapping:
                        mapping[violation_type] = []
                    mapping[violation_type].append(regulation)
        
        return mapping
    
    def get_regulations_for_violation(self, violation_type: ViolationType) -> List[LegalRegulation]:
        """获取特定违章类型的相关法规"""
        return self.violation_mapping.get(violation_type, [])
    
    def get_legal_advice(self, violation_type: ViolationType, severity: str = "中") -> LegalAdvice:
        """生成法律建议"""
        regulations = self.get_regulations_for_violation(violation_type)
        
        if not regulations:
            return LegalAdvice(
                violation_type=violation_type,
                severity_level=severity,
                applicable_laws=["相关法规待完善"],
                recommended_actions=["建议咨询法律专家"],
                penalty_range="具体处罚标准参照地方法规",
                legal_basis="相关法律法规",
                enforcement_priority=1
            )
        
        primary_regulation = regulations[0]
        
        # 根据严重程度确定执法优先级
        priority_map = {"低": 1, "中": 3, "高": 4, "严重": 5}
        priority = priority_map.get(severity, 3)
        
        return LegalAdvice(
            violation_type=violation_type,
            severity_level=severity,
            applicable_laws=[reg.title for reg in regulations],
            recommended_actions=[
                "立即责令停止违法行为",
                "调查取证，收集相关材料",
                "按照法定程序进行处罚",
                "监督违法行为人整改落实"
            ],
            penalty_range=primary_regulation.penalty_description,
            legal_basis=f"{primary_regulation.title} {primary_regulation.content}",
            enforcement_priority=priority
        )
    
    def search_regulations(self, keywords: List[str]) -> List[LegalRegulation]:
        """根据关键词搜索法规"""
        results = []
        
        for category, regulations in self.regulations.items():
            for regulation in regulations:
                # 检查标题、内容和关键词
                search_text = f"{regulation.title} {regulation.content} {' '.join(regulation.keywords)}".lower()
                
                for keyword in keywords:
                    if keyword.lower() in search_text:
                        if regulation not in results:
                            results.append(regulation)
                        break
        
        return results
    
    def get_enforcement_statistics(self) -> Dict[str, Any]:
        """获取执法统计信息"""
        total_regulations = sum(len(regs) for regs in self.regulations.values())
        
        violation_coverage = {}
        for violation_type in ViolationType:
            count = len(self.get_regulations_for_violation(violation_type))
            violation_coverage[violation_type.value] = count
        
        return {
            "total_regulations": total_regulations,
            "categories_count": len(self.regulations),
            "violation_type_coverage": violation_coverage,
            "latest_update": datetime.now().isoformat()
        }


# 全局知识库实例
legal_knowledge_base = LegalKnowledgeBase()