#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法规解读服务
智慧城管系统 - 大语言模型法规解读功能
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from app.models.legal_regulations import (
    LegalKnowledgeBase, 
    ViolationType, 
    LegalAdvice, 
    LegalRegulation,
    legal_knowledge_base
)
from app.models.violation_types import ViolationCategory, get_violation_info
import httpx
from datetime import datetime


class LLMIntegrationService:
    """大语言模型集成服务"""
    
    def __init__(self):
        self.knowledge_base = legal_knowledge_base
        self.llm_config = {
            "enabled": os.getenv("LLM_ENABLED", "false").lower() == "true",
            "api_endpoint": os.getenv("LLM_API_ENDPOINT", ""),
            "api_key": os.getenv("LLM_API_KEY", ""),
            "model_name": os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo"),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "1000")),
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.3"))
        }
    
    async def analyze_violation_with_llm(self, violation_description: str, image_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """使用LLM分析违章情况并提供法律建议"""
        try:
            # 构建分析prompt
            prompt = self._build_analysis_prompt(violation_description, image_analysis)
            
            if self.llm_config["enabled"]:
                # 调用LLM API
                llm_response = await self._call_llm_api(prompt)
                
                # 解析LLM响应
                analysis_result = self._parse_llm_response(llm_response)
            else:
                # 使用本地规则引擎作为备选方案
                analysis_result = self._local_rule_analysis(violation_description, image_analysis)
            
            # 结合知识库增强结果
            enhanced_result = self._enhance_with_knowledge_base(analysis_result)
            
            return enhanced_result
            
        except Exception as e:
            print(f"LLM分析失败: {e}")
            # 降级到本地分析
            return self._local_rule_analysis(violation_description, image_analysis)
    
    def _build_analysis_prompt(self, violation_description: str, image_analysis: Dict[str, Any]) -> str:
        """构建分析prompt"""
        prompt = f"""
作为智慧城管系统的法律专家，请分析以下违章建筑情况并提供专业建议：

违章描述: {violation_description}

图像分析结果:
- 建筑特征: {image_analysis.get('building_features', {})}
- 环境上下文: {image_analysis.get('environmental_context', {})}
- 风险评估: {image_analysis.get('risk_assessment', {})}

请从以下几个维度进行分析：
1. 违章类型识别 - 确定具体的违章建筑类型
2. 严重程度评估 - 评估违章的严重程度（轻微/一般/严重/重大）
3. 法律适用性 - 分析适用的法律法规条文
4. 执法建议 - 提供具体的执法处置建议
5. 处罚依据 - 说明相应的法律处罚依据

请以JSON格式返回分析结果：
{{
    "violation_type": "具体违章类型",
    "severity_level": "严重程度",
    "legal_basis": ["适用的法律条文"],
    "enforcement_recommendations": ["执法建议"],
    "penalty_basis": "处罚依据",
    "priority_score": 1-5的优先级评分,
    "analysis_confidence": 0.0-1.0的置信度
}}
"""
        return prompt
    
    async def _call_llm_api(self, prompt: str) -> str:
        """调用LLM API"""
        if not self.llm_config["api_endpoint"] or not self.llm_config["api_key"]:
            raise Exception("LLM API配置不完整")
        
        headers = {
            "Authorization": f"Bearer {self.llm_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.llm_config["model_name"],
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的城市管理法律专家，精通违章建筑相关的法律法规。"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": self.llm_config["max_tokens"],
            "temperature": self.llm_config["temperature"]
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.llm_config["api_endpoint"],
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """解析LLM响应"""
        try:
            # 尝试提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # 如果没有找到JSON，使用文本解析
                return self._parse_text_response(response)
                
        except json.JSONDecodeError:
            return self._parse_text_response(response)
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """解析文本响应（备选方案）"""
        # 简化的文本解析逻辑
        lines = response.lower().split('\n')
        
        violation_type = "illegal_construction"  # 默认类型
        severity_level = "中"
        priority_score = 3
        
        # 简单的关键词匹配
        if any(word in response.lower() for word in ['严重', '重大', '危险']):
            severity_level = "严重"
            priority_score = 5
        elif any(word in response.lower() for word in ['轻微', '一般']):
            severity_level = "轻微"  
            priority_score = 2
        
        return {
            "violation_type": violation_type,
            "severity_level": severity_level,
            "legal_basis": ["相关城市管理法规"],
            "enforcement_recommendations": ["建议现场核查", "依法处置"],
            "penalty_basis": "根据相关法律法规进行处罚",
            "priority_score": priority_score,
            "analysis_confidence": 0.7
        }
    
    def _local_rule_analysis(self, violation_description: str, image_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """本地规则引擎分析（LLM不可用时的备选方案）"""
        # 基于风险评估确定违章类型和严重程度
        risk_assessment = image_analysis.get('risk_assessment', {})
        risk_score = risk_assessment.get('risk_score', 0)
        
        # 根据风险分数确定严重程度
        if risk_score >= 50:
            severity_level = "严重"
            priority_score = 5
        elif risk_score >= 30:
            severity_level = "中"
            priority_score = 3
        else:
            severity_level = "轻微"
            priority_score = 2
        
        # 基于建筑特征分析确定违章类型
        building_features = image_analysis.get('building_features', {})
        complexity_level = building_features.get('complexity_level', '低')
        
        if complexity_level == '高':
            violation_type = "illegal_construction"
        else:
            violation_type = "temporary_structure"
        
        return {
            "violation_type": violation_type,
            "severity_level": severity_level,
            "legal_basis": ["城乡规划法", "城市管理条例"],
            "enforcement_recommendations": [
                "立即组织现场调查",
                "收集相关证据材料",
                "按程序进行处理",
                "跟踪整改落实"
            ],
            "penalty_basis": "依据相关法律法规执行",
            "priority_score": priority_score,
            "analysis_confidence": 0.8
        }
    
    def _enhance_with_knowledge_base(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """使用知识库增强分析结果"""
        try:
            violation_type_str = analysis_result.get("violation_type", "illegal_construction")
            
            # 映射到ViolationType枚举
            violation_type_mapping = {
                "illegal_construction": ViolationType.ILLEGAL_CONSTRUCTION,
                "unauthorized_parking": ViolationType.UNAUTHORIZED_PARKING,
                "temporary_structure": ViolationType.TEMPORARY_STRUCTURE,
                "shed_structure": ViolationType.SHED_STRUCTURE,
                "illegal_market_stall": ViolationType.ILLEGAL_MARKET_STALL,
                "unauthorized_storefront": ViolationType.UNAUTHORIZED_STOREFRONT,
                "illegal_fence": ViolationType.ILLEGAL_FENCE,
                "illegal_signage": ViolationType.ILLEGAL_SIGNAGE
            }
            
            violation_type = violation_type_mapping.get(violation_type_str, ViolationType.ILLEGAL_CONSTRUCTION)
            severity = analysis_result.get("severity_level", "中")
            
            # 获取法律建议
            legal_advice = self.knowledge_base.get_legal_advice(violation_type, severity)
            
            # 获取相关法规
            regulations = self.knowledge_base.get_regulations_for_violation(violation_type)
            
            # 增强结果
            enhanced_result = analysis_result.copy()
            enhanced_result.update({
                "legal_advice": legal_advice.dict(),
                "applicable_regulations": [
                    {
                        "title": reg.title,
                        "content": reg.content,
                        "penalty_description": reg.penalty_description,
                        "enforcement_procedure": reg.enforcement_procedure
                    } for reg in regulations[:3]  # 最多返回3条最相关的法规
                ],
                "enhanced_by_knowledge_base": True,
                "knowledge_base_version": "1.0"
            })
            
            return enhanced_result
            
        except Exception as e:
            print(f"知识库增强失败: {e}")
            return analysis_result
    
    def get_violation_legal_summary(self, violation_type: str) -> Dict[str, Any]:
        """获取特定违章类型的法律摘要"""
        try:
            # 映射违章类型
            violation_mapping = {
                "illegal_construction": ViolationType.ILLEGAL_CONSTRUCTION,
                "unauthorized_parking": ViolationType.UNAUTHORIZED_PARKING,
                "temporary_structure": ViolationType.TEMPORARY_STRUCTURE,
                "shed_structure": ViolationType.SHED_STRUCTURE,
                "illegal_market_stall": ViolationType.ILLEGAL_MARKET_STALL,
                "unauthorized_storefront": ViolationType.UNAUTHORIZED_STOREFRONT,
                "illegal_fence": ViolationType.ILLEGAL_FENCE,
                "illegal_signage": ViolationType.ILLEGAL_SIGNAGE
            }
            
            violation_enum = violation_mapping.get(violation_type, ViolationType.ILLEGAL_CONSTRUCTION)
            
            # 获取相关法规
            regulations = self.knowledge_base.get_regulations_for_violation(violation_enum)
            legal_advice = self.knowledge_base.get_legal_advice(violation_enum)
            
            return {
                "violation_type": violation_type,
                "violation_name": violation_enum.value,
                "applicable_laws_count": len(regulations),
                "primary_regulations": [
                    {
                        "title": reg.title,
                        "level": reg.level.value,
                        "effective_date": reg.effective_date.isoformat(),
                        "keywords": reg.keywords
                    } for reg in regulations[:2]
                ],
                "legal_advice": legal_advice.dict(),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"获取法律摘要失败: {str(e)}"}
    
    def search_legal_cases(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """搜索相关法律案例"""
        try:
            regulations = self.knowledge_base.search_regulations(keywords)
            
            return [
                {
                    "regulation_id": reg.regulation_id,
                    "title": reg.title,
                    "level": reg.level.value,
                    "content_excerpt": reg.content[:200] + "..." if len(reg.content) > 200 else reg.content,
                    "applicable_violations": [vt.value for vt in reg.applicable_violations],
                    "keywords": reg.keywords
                } for reg in regulations
            ]
            
        except Exception as e:
            return [{"error": f"搜索失败: {str(e)}"}]


# 全局法规服务实例
legal_service = LLMIntegrationService()