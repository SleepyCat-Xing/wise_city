#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
违章建筑智能检测系统启动脚本
智慧城管：基于多模态AI的违章建筑智能检测与管理系统
"""

import uvicorn
import argparse
import os
import sys
import locale

# 设置控制台编码
if sys.platform.startswith('win'):
    # Windows系统设置
    os.system('chcp 65001 > nul')  # 设置为UTF-8编码
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # 设置locale
    try:
        locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'Chinese')
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description='启动违章建筑智能检测系统')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, default=8000, help='监听端口')
    parser.add_argument('--reload', action='store_true', help='启用自动重载（开发模式）')
    parser.add_argument('--workers', type=int, default=1, help='工作进程数量')
    parser.add_argument('--log-level', default='info', choices=['debug', 'info', 'warning', 'error'])
    
    args = parser.parse_args()
    
    # 确保必要的目录存在
    os.makedirs('data/uploads', exist_ok=True)
    os.makedirs('data/results', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    print("=" * 80)
    print("智慧城管：基于多模态AI的违章建筑智能检测与管理系统")
    print("第十一届中国研究生智慧城市技术与创意设计大赛作品")
    print("=" * 80)
    print(f"服务地址: http://{args.host}:{args.port}")
    print(f"API文档: http://{args.host}:{args.port}/docs") 
    print(f"健康检查: http://{args.host}:{args.port}/health")
    print(f"演示页面: http://{args.host}:{args.port}/static/demo.html")
    print("=" * 80)
    print("系统特性:")
    print("   * 多模态AI融合检测 (YOLOv8增强版)")
    print("   * 违章建筑智能分类 (支持TIF格式)")
    print("   * 图像增强与结构分析")
    print("   * 性能目标: mAP>=0.85, 响应<=3秒")
    print("=" * 80)
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        log_level=args.log_level,
        access_log=True
    )

if __name__ == "__main__":
    main()