#!/usr/bin/env python3
"""
违章建筑智能检测系统启动脚本
"""

import uvicorn
import argparse
import os
import sys

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
    
    print("=" * 60)
    print("违章建筑智能检测与管理系统")
    print("=" * 60)
    print(f"启动地址: http://{args.host}:{args.port}")
    print(f"API文档: http://{args.host}:{args.port}/docs")
    print(f"健康检查: http://{args.host}:{args.port}/health")
    print("=" * 60)
    
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