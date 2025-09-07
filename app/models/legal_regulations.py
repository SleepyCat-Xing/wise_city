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


# 法规知识库数据 - 扩展版
LEGAL_REGULATIONS_DATABASE = {
    "urban_rural_planning": [  # 城乡规划法
        LegalRegulation(
            regulation_id="URP_001",
            title="中华人民共和国城乡规划法",
            content="第四十条：在城市、镇规划区内进行建筑物、构筑物、道路、管线和其他工程建设的，建设单位或者个人应当向城市、县人民政府城乡规划主管部门或者省、自治区、直辖市人民政府确定的镇人民政府申请办理建设工程规划许可证。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(2008, 1, 1),
            applicable_violations=[ViolationType.ILLEGAL_CONSTRUCTION],
            penalty_description="未取得建设工程规划许可证或者未按照建设工程规划许可证的规定进行建设的，由县级以上地方人民政府城乡规划主管部门责令停止建设；尚可采取改正措施消除对规划实施的影响的，限期改正，处建设工程造价百分之五以上百分之十以下的罚款；无法采取改正措施消除影响的，限期拆除，不能拆除的，没收实物或者违法收入，可以并处建设工程造价百分之十以下的罚款。",
            enforcement_procedure="发现→调查取证→责令停止→限期整改→执行处罚",
            keywords=["建设工程规划许可证", "违法建设", "城乡规划", "建筑物", "构筑物"]
        ),
        LegalRegulation(
            regulation_id="URP_002",
            title="中华人民共和国城乡规划法",
            content="第六十四条：未取得建设工程规划许可证或者未按照建设工程规划许可证的规定进行建设的，由县级以上地方人民政府城乡规划主管部门责令停止建设；尚可采取改正措施消除对规划实施的影响的，限期改正，处建设工程造价百分之五以上百分之十以下的罚款；无法采取改正措施消除影响的，限期拆除，不能拆除的，没收实物或者违法收入，可以并处建设工程造价百分之十以下的罚款。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(2008, 1, 1),
            applicable_violations=[ViolationType.ILLEGAL_CONSTRUCTION, ViolationType.TEMPORARY_STRUCTURE],
            penalty_description="责令停止建设，限期拆除，没收违法收入，并处罚款",
            enforcement_procedure="发现→立案→调查→责令停止→限期拆除→处罚",
            keywords=["违法建设", "限期拆除", "没收", "罚款"]
        ),
        LegalRegulation(
            regulation_id="URP_003",
            title="中华人民共和国城乡规划法",
            content="第六十六条：建设单位或者个人有下列行为之一的，由所在地城市、县人民政府城乡规划主管部门责令限期拆除，可以并处临时建设工程造价一倍以下的罚款：（一）未经批准进行临时建设的；（二）未按照批准内容进行临时建设的；（三）临时建筑物、构筑物超过批准期限不拆除的。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(2008, 1, 1),
            applicable_violations=[ViolationType.TEMPORARY_STRUCTURE, ViolationType.SHED_STRUCTURE],
            penalty_description="责令限期拆除，可以并处临时建设工程造价一倍以下的罚款",
            enforcement_procedure="发现→调查→责令限期拆除→执行处罚",
            keywords=["临时建设", "限期拆除", "临时建筑", "造价罚款"]
        )
    ],
    
    "construction_law": [  # 建筑法
        LegalRegulation(
            regulation_id="CL_001",
            title="中华人民共和国建筑法",
            content="第七条：建筑工程开工前，建设单位应当按照国家有关规定向工程所在地县级以上人民政府建设行政主管部门申请领取施工许可证；但是，国务院建设行政主管部门确定的限额以下的小型工程除外。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(1998, 3, 1),
            applicable_violations=[ViolationType.ILLEGAL_CONSTRUCTION],
            penalty_description="责令停止施工，限期改正，处工程合同价款百分之一以上百分之二以下的罚款",
            enforcement_procedure="发现→责令停止→限期改正→处罚",
            keywords=["施工许可证", "建筑工程", "开工前", "建设行政主管部门"]
        ),
        LegalRegulation(
            regulation_id="CL_002",
            title="中华人民共和国建筑法",
            content="第六十一条：交付竣工验收的建筑工程，必须符合规定的建筑工程质量标准，有完整的工程技术经济资料和经签署的工程保修书，并具备国家规定的其他竣工条件。建筑工程竣工经验收合格后，方可交付使用；未经验收或者验收不合格的，不得交付使用。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(1998, 3, 1),
            applicable_violations=[ViolationType.ILLEGAL_CONSTRUCTION],
            penalty_description="责令改正，处工程合同价款百分之二以上百分之四以下的罚款；造成损失的，依法承担赔偿责任",
            enforcement_procedure="发现→调查→责令改正→处罚→赔偿",
            keywords=["竣工验收", "质量标准", "验收合格", "交付使用"]
        ),
        LegalRegulation(
            regulation_id="CL_003",
            title="中华人民共和国建筑法",
            content="第六十八条：在工程发包与承包中索贿、受贿、行贿，构成犯罪的，依法追究刑事责任；不构成犯罪的，分别处以罚款，没收贿赂的财物，对直接负责的主管人员和其他直接责任人员给予处分。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(1998, 3, 1),
            applicable_violations=[ViolationType.ILLEGAL_CONSTRUCTION],
            penalty_description="构成犯罪的追究刑事责任；不构成犯罪的处以罚款，没收财物",
            enforcement_procedure="发现→调查→依法处理→处罚",
            keywords=["发包承包", "索贿受贿", "刑事责任", "罚款没收"]
        )
    ],
    
    "land_management": [  # 土地管理法
        LegalRegulation(
            regulation_id="LM_001",
            title="中华人民共和国土地管理法",
            content="第四十四条：建设占用土地，涉及农用地转为建设用地的，应当办理农用地转用审批手续。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(2020, 1, 1),
            applicable_violations=[ViolationType.ILLEGAL_CONSTRUCTION],
            penalty_description="限期拆除在非法占用的土地上新建的建筑物和其他设施，恢复土地原状，对符合土地利用总体规划的，没收在非法占用的土地上新建的建筑物和其他设施，可以并处罚款",
            enforcement_procedure="发现→调查→责令拆除→恢复原状→处罚",
            keywords=["农用地转用", "建设用地", "审批手续", "非法占用"]
        ),
        LegalRegulation(
            regulation_id="LM_002",
            title="中华人民共和国土地管理法",
            content="第七十七条：未经批准或者采取欺骗手段骗取批准，非法占用土地的，由县级以上人民政府自然资源主管部门责令退还非法占用的土地，对违反土地利用总体规划擅自将农用地改为建设用地的，限期拆除在非法占用的土地上新建的建筑物和其他设施，恢复土地原状。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(2020, 1, 1),
            applicable_violations=[ViolationType.ILLEGAL_CONSTRUCTION],
            penalty_description="退还非法占用的土地，限期拆除新建建筑物，恢复土地原状，对符合规划的没收建筑物并处罚款",
            enforcement_procedure="发现→调查→责令退还→限期拆除→恢复原状→处罚",
            keywords=["非法占用土地", "土地利用总体规划", "恢复土地原状", "没收建筑物"]
        ),
        LegalRegulation(
            regulation_id="LM_003",
            title="中华人民共和国土地管理法",
            content="第八十三条：依照本法规定，责令限期拆除在非法占用的土地上新建的建筑物和其他设施的，建设单位或者个人必须立即停止施工，自行拆除；对继续施工的，作出处罚决定的机关有权制止。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(2020, 1, 1),
            applicable_violations=[ViolationType.ILLEGAL_CONSTRUCTION, ViolationType.TEMPORARY_STRUCTURE],
            penalty_description="责令立即停止施工，自行拆除；对继续施工的，有权制止",
            enforcement_procedure="发现→责令停止→限期拆除→制止继续施工",
            keywords=["停止施工", "自行拆除", "制止施工", "非法占用"]
        )
    ],
    
    "urban_management": [  # 城市管理条例
        LegalRegulation(
            regulation_id="UM_001",
            title="城市市容和环境卫生管理条例",
            content="第三十六条：有下列行为之一的，由城市人民政府市容环境卫生行政主管部门或者其委托的单位责令停止违法行为，限期清理、拆除或者采取其他补救措施，并可处以罚款：（一）未经城市人民政府市容环境卫生行政主管部门同意，擅自设置大型户外广告，影响市容的；（二）未经城市人民政府市容环境卫生行政主管部门批准，擅自在街道两侧和公共场地堆放物料，搭建建筑物、构筑物或者其他设施，影响市容的。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(1992, 8, 1),
            applicable_violations=[ViolationType.TEMPORARY_STRUCTURE, ViolationType.ILLEGAL_MARKET_STALL, ViolationType.ILLEGAL_SIGNAGE],
            penalty_description="责令停止违法行为，限期清理、拆除或者采取其他补救措施，并可处以罚款",
            enforcement_procedure="发现→责令停止→限期清理→拆除→处罚",
            keywords=["户外广告", "街道两侧", "公共场地", "搭建建筑物", "影响市容"]
        ),
        LegalRegulation(
            regulation_id="UM_002",
            title="城市道路管理条例",
            content="第二十七条：城市道路范围内禁止下列行为：（一）擅自占用或者挖掘城市道路；（二）履带车、铁轮车或者超重、超高、超长车辆擅自在城市道路上行驶；（三）机动车在桥梁或者非指定的城市道路上试刹车；（四）擅自在城市道路上搭建建筑物、构筑物；（五）在桥梁上架设压力在4公斤/平方厘米（0.4兆帕）以上的煤气管道、10千伏以上的高压电力线和其他易燃易爆管线；（六）擅自在桥梁或者路灯设施上设置广告牌或者其他挂浮物；（七）其他损害、侵占城市道路的行为。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(1996, 10, 1),
            applicable_violations=[ViolationType.ILLEGAL_MARKET_STALL, ViolationType.UNAUTHORIZED_STOREFRONT],
            penalty_description="责令限期清除占用物，恢复城市道路原状，并可处以二万元以下的罚款",
            enforcement_procedure="发现→调查核实→责令清除→恢复原状→处罚",
            keywords=["占用道路", "挖掘道路", "搭建建筑物", "侵占道路"]
        )
    ],
    
    "traffic_management": [  # 交通管理
        LegalRegulation(
            regulation_id="TM_001",
            title="中华人民共和国道路交通安全法",
            content="第五十六条：机动车应当在规定地点停放。禁止在人行道、车行道、无障碍通道上停放机动车；但是，依照本法第三十三条规定施划的停车泊位除外。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(2004, 5, 1),
            applicable_violations=[ViolationType.UNAUTHORIZED_PARKING],
            penalty_description="对违反道路交通安全法律、法规关于机动车停放、临时停车规定的，可以指出违法行为，并予以口头警告，令其立即驶离。机动车驾驶人不在现场或者虽在现场但拒绝立即驶离，妨碍其他车辆、行人通行的，处二十元以上二百元以下罚款",
            enforcement_procedure="发现→警告→责令驶离→处罚",
            keywords=["机动车停放", "规定地点", "人行道", "车行道"]
        ),
        LegalRegulation(
            regulation_id="TM_002",
            title="中华人民共和国道路交通安全法实施条例",
            content="第六十三条：机动车在道路上临时停车，应当遵守下列规定：（一）在设有禁停标志、标线的路段，在机动车道与非机动车道、人行道之间设有隔离设施的路段以及人行横道、施工地段，不得停车；（二）交叉路口、铁路道口、急弯路、宽度不足4米的窄路、桥梁、陡坡、隧道以及距离上述地点50米以内的路段，不得停车；（三）公共汽车站、急救站、加油站、消防栓或者消防队（站）门前以及距离上述地点30米以内的路段，除使用上述设施的以外，不得停车；（四）车辆停稳前不得开车门和上下人员，开车门不得妨碍其他车辆和行人通行；（五）路边停车应当紧靠道路右侧，机动车驾驶人不得离车，上下人员或者装卸物品后，立即驶离；（六）城市公共汽车不得在站点以外的路段停车上下乘客。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(2004, 5, 1),
            applicable_violations=[ViolationType.UNAUTHORIZED_PARKING],
            penalty_description="违反停车规定的，处警告或者二十元以上二百元以下罚款",
            enforcement_procedure="发现→取证→处罚",
            keywords=["临时停车", "禁停标志", "交叉路口", "消防栓", "急救站"]
        )
    ],
    
    "commercial_regulation": [  # 商业管理
        LegalRegulation(
            regulation_id="CR_001",
            title="无证无照经营查处办法",
            content="第二条：任何单位或者个人不得违反法律、法规、国务院决定的规定，从事无证无照经营。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(2017, 10, 1),
            applicable_violations=[ViolationType.ILLEGAL_MARKET_STALL, ViolationType.UNAUTHORIZED_STOREFRONT],
            penalty_description="责令停止违法行为，没收违法所得，并处1万元以下的罚款",
            enforcement_procedure="发现→调查→责令停止→没收违法所得→处罚",
            keywords=["无证经营", "无照经营", "查处办法", "违法所得"]
        ),
        LegalRegulation(
            regulation_id="CR_002",
            title="个体工商户条例",
            content="第八条：申请登记为个体工商户，应当向经营场所所在地登记机关申请注册登记。申请人应当提交登记申请书、身份证明和经营场所证明。",
            level=RegulationLevel.NATIONAL,
            effective_date=datetime(2011, 11, 1),
            applicable_violations=[ViolationType.ILLEGAL_MARKET_STALL],
            penalty_description="责令停止经营，没收违法所得，并处以罚款",
            enforcement_procedure="发现→调查→责令停止→处罚",
            keywords=["个体工商户", "登记注册", "经营场所", "申请登记"]
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
            violation_coverage[violation_type.value if hasattr(violation_type, 'value') else str(violation_type)] = count
        
        return {
            "total_regulations": total_regulations,
            "categories_count": len(self.regulations),
            "violation_type_coverage": violation_coverage,
            "latest_update": datetime.now().isoformat()
        }
    
    def get_knowledge_graph(self) -> Dict[str, Any]:
        """获取法规知识图谱数据"""
        knowledge_graph = {
            "nodes": [],
            "edges": [],
            "categories": {},
            "metadata": {
                "total_nodes": 0,
                "total_edges": 0,
                "graph_type": "法律知识图谱",
                "last_updated": datetime.now().isoformat()
            }
        }
        
        # 添加法规类别节点
        category_id = 0
        for category_name, regulations in self.regulations.items():
            category_node = {
                "id": f"category_{category_id}",
                "name": self._get_category_display_name(category_name),
                "type": "category",
                "description": f"{len(regulations)}条相关法规",
                "regulation_count": len(regulations),
                "color": self._get_category_color(category_name)
            }
            knowledge_graph["nodes"].append(category_node)
            knowledge_graph["categories"][category_name] = category_node
            
            # 添加具体法规节点
            for i, regulation in enumerate(regulations):
                regulation_node = {
                    "id": f"reg_{regulation.regulation_id}",
                    "name": regulation.title,
                    "type": "regulation",
                    "content": regulation.content[:100] + "..." if len(regulation.content) > 100 else regulation.content,
                    "level": regulation.level if isinstance(regulation.level, str) else regulation.level.value,
                    "effective_date": regulation.effective_date.isoformat(),
                    "penalty_description": regulation.penalty_description[:50] + "..." if len(regulation.penalty_description) > 50 else regulation.penalty_description,
                    "keywords": regulation.keywords,
                    "category": category_name
                }
                knowledge_graph["nodes"].append(regulation_node)
                
                # 添加类别到法规的边
                knowledge_graph["edges"].append({
                    "source": f"category_{category_id}",
                    "target": f"reg_{regulation.regulation_id}",
                    "type": "contains",
                    "weight": 1.0
                })
                
                # 添加法规到违章类型的边
                for violation_type in regulation.applicable_violations:
                    # Handle both enum objects and string values
                    if hasattr(violation_type, 'value'):
                        violation_value = violation_type.value
                    else:
                        violation_value = violation_type
                    
                    violation_node_id = f"violation_{violation_value}"
                    
                    # 检查是否已存在该违章类型节点
                    existing_violation = next((node for node in knowledge_graph["nodes"] if node["id"] == violation_node_id), None)
                    if not existing_violation:
                        violation_node = {
                            "id": violation_node_id,
                            "name": violation_value.replace("_", " ").title(),
                            "type": "violation",
                            "description": f"违章类型: {violation_value}",
                            "regulation_count": 0
                        }
                        knowledge_graph["nodes"].append(violation_node)
                    
                    # 添加法规到违章类型的边
                    knowledge_graph["edges"].append({
                        "source": f"reg_{regulation.regulation_id}",
                        "target": violation_node_id,
                        "type": "applies_to",
                        "weight": 1.0
                    })
                    
                    # 更新违章类型的法规计数
                    if existing_violation:
                        existing_violation["regulation_count"] += 1
                    else:
                        violation_node["regulation_count"] = 1
            
            category_id += 1
        
        # 更新元数据
        knowledge_graph["metadata"]["total_nodes"] = len(knowledge_graph["nodes"])
        knowledge_graph["metadata"]["total_edges"] = len(knowledge_graph["edges"])
        
        return knowledge_graph
    
    def _get_category_display_name(self, category_name: str) -> str:
        """获取类别显示名称"""
        display_names = {
            "urban_rural_planning": "城乡规划法",
            "construction_law": "建筑法",
            "land_management": "土地管理法",
            "urban_management": "城市管理条例",
            "traffic_management": "交通管理法规",
            "commercial_regulation": "商业管理法规"
        }
        return display_names.get(category_name, category_name)
    
    def _get_category_color(self, category_name: str) -> str:
        """获取类别颜色"""
        colors = {
            "urban_rural_planning": "#667eea",
            "construction_law": "#f093fb",
            "land_management": "#4facfe",
            "urban_management": "#fa709a",
            "traffic_management": "#feca57",
            "commercial_regulation": "#ff6b6b"
        }
        return colors.get(category_name, "#95a5a6")
    
    def get_law_categories_summary(self) -> Dict[str, Any]:
        """获取法律法规类别摘要"""
        summary = {}
        
        for category_name, regulations in self.regulations.items():
            # 统计该类别下的违章类型
            violation_types = set()
            for regulation in regulations:
                for violation_type in regulation.applicable_violations:
                    # Handle both enum objects and string values
                    if hasattr(violation_type, 'value'):
                        violation_types.add(violation_type.value)
                    else:
                        violation_types.add(violation_type)
            
            summary[category_name] = {
                "display_name": self._get_category_display_name(category_name),
                "regulation_count": len(regulations),
                "violation_types": list(violation_types),
                "violation_count": len(violation_types),
                "color": self._get_category_color(category_name),
                "key_regulations": [
                    {
                        "id": reg.regulation_id,
                        "title": reg.title,
                        "keywords": reg.keywords[:3]  # 前3个关键词
                    }
                    for reg in regulations[:2]  # 前2条重要法规
                ]
            }
        
        return summary
    
    def get_legal_knowledge_insights(self) -> Dict[str, Any]:
        """获取法律知识图谱洞察"""
        total_regulations = sum(len(regs) for regs in self.regulations.values())
        
        # 统计各个法规的覆盖情况
        category_stats = {}
        for category_name, regulations in self.regulations.items():
            violation_coverage = {}
            for regulation in regulations:
                for violation_type in regulation.applicable_violations:
                    # Handle both enum objects and string values
                    if hasattr(violation_type, 'value'):
                        violation_value = violation_type.value
                    else:
                        violation_value = violation_type
                    
                    if violation_value not in violation_coverage:
                        violation_coverage[violation_value] = 0
                    violation_coverage[violation_value] += 1
            
            category_stats[category_name] = {
                "display_name": self._get_category_display_name(category_name),
                "regulation_count": len(regulations),
                "covered_violations": len(violation_coverage),
                "violation_coverage": violation_coverage
            }
        
        # 找出覆盖最广的法规
        most_comprehensive = max(category_stats.items(), 
                               key=lambda x: x[1]["covered_violations"])
        
        # 找出覆盖最少的违章类型
        all_violations = set()
        violation_coverage_count = {}
        for category_data in category_stats.values():
            for violation, count in category_data["violation_coverage"].items():
                all_violations.add(violation)
                if violation not in violation_coverage_count:
                    violation_coverage_count[violation] = 0
                violation_coverage_count[violation] += count
        
        least_covered = min(violation_coverage_count.items(), 
                           key=lambda x: x[1]) if violation_coverage_count else (None, 0)
        
        return {
            "total_regulations": total_regulations,
            "total_categories": len(self.regulations),
            "total_violation_types": len(all_violations),
            "category_statistics": category_stats,
            "most_comprehensive_law": {
                "category": most_comprehensive[0],
                "display_name": most_comprehensive[1]["display_name"],
                "covered_violations": most_comprehensive[1]["covered_violations"]
            },
            "coverage_analysis": {
                "average_violations_per_category": sum(stats["covered_violations"] for stats in category_stats.values()) / len(category_stats),
                "least_covered_violation": least_covered[0] if least_covered[0] else "无",
                "minimal_coverage_count": least_covered[1] if least_covered[0] else 0
            },
            "knowledge_graph_quality": {
                "completeness_score": min(len(all_violations) * 10, 100),  # 简化的完整性评分
                "interconnectivity_score": len([edge for edge in self.get_knowledge_graph()["edges"] if edge["type"] == "applies_to"]),
                "last_updated": datetime.now().isoformat()
            }
        }


# 全局知识库实例
legal_knowledge_base = LegalKnowledgeBase()