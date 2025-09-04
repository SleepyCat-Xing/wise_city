import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """测试健康检查接口"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    """测试根接口"""
    response = client.get("/")
    assert response.status_code == 200
    assert "违章建筑智能检测系统API" in response.json()["message"]

def test_system_health():
    """测试系统健康检查"""
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_model_info():
    """测试获取模型信息"""
    response = client.get("/api/v1/detection/model/info")
    assert response.status_code == 200
    assert response.json()["success"] == True

# 注意：实际的图像检测测试需要真实的图像文件
# 这里仅提供基本的API测试框架