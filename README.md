# 智慧城市管理系统 (Wise City Management System)

## 项目简介

智慧城市管理系统是一个基于AI的智能城市管理平台，集成了YOLOv8目标检测技术，能够实时监控和分析城市中的各种违规行为和异常情况。

## 功能特性

- 🤖 **AI智能检测**: 基于YOLOv8的实时目标检测
- 📊 **数据管理**: 完整的检测结果数据存储和管理
- 🌐 **RESTful API**: 标准化的API接口
- 🐳 **Docker支持**: 容器化部署，简化运维
- 📁 **文件管理**: 支持图片和视频文件的上传处理
- 🔍 **多种检测模式**: 支持图片、视频和实时流检测

## 技术栈

- **后端框架**: FastAPI
- **AI模型**: YOLOv8
- **数据库**: SQLite/PostgreSQL
- **部署**: Docker + Docker Compose
- **Web服务器**: Nginx
- **Python版本**: 3.8+

## 项目结构

```
wise_city/
├── app/                    # 应用程序主目录
│   ├── api/               # API路由
│   ├── core/              # 核心配置
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑服务
│   └── utils/             # 工具函数
├── data/                  # 数据目录
│   ├── uploads/           # 上传文件
│   └── results/           # 检测结果
├── docker/                # Docker配置
├── models/                # AI模型文件
├── static/                # 静态文件
├── tests/                 # 测试文件
└── docs/                  # 文档
```

## 快速开始

### 使用Docker部署（推荐）

1. **克隆项目**
   ```bash
   git clone https://github.com/insistgang/wise_city.git
   cd wise_city
   ```

2. **启动服务**
   ```bash
   # 开发环境
   docker-compose -f docker-compose.dev.yml up -d
   
   # 生产环境
   docker-compose up -d
   ```

3. **访问应用**
   - API文档: http://localhost:8000/docs
   - 演示页面: http://localhost:8000/demo.html

### 本地开发

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件配置数据库等信息
   ```

3. **启动应用**
   ```bash
   python run.py
   ```

## API接口

### 主要端点

- `GET /` - 健康检查
- `POST /api/v1/detect/image` - 图片检测
- `POST /api/v1/detect/video` - 视频检测
- `GET /api/v1/detect/results` - 获取检测结果
- `POST /api/v1/files/upload` - 文件上传

详细的API文档请访问: http://localhost:8000/docs

## 配置说明

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接URL | `sqlite:///./wise_city.db` |
| `UPLOAD_DIR` | 文件上传目录 | `./data/uploads` |
| `RESULTS_DIR` | 检测结果目录 | `./data/results` |
| `MODEL_PATH` | AI模型路径 | `./yolov8n.pt` |

### 违规类型配置

系统支持多种违规检测类型，可在 `app/models/violation_types.py` 中配置：
- 违规停车
- 乱丢垃圾
- 违规建筑
- 交通违规
- 其他自定义类型

## 开发指南

### 代码规范

- 使用 Black 进行代码格式化
- 使用 flake8 进行代码检查
- 使用 pre-commit 钩子确保代码质量

### 测试

```bash
# 运行测试
pytest tests/

# 生成覆盖率报告
pytest --cov=app tests/
```

### 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 部署指南

### 生产环境部署

1. **服务器要求**
   - 2GB+ RAM
   - 10GB+ 磁盘空间
   - Docker & Docker Compose

2. **部署步骤**
   ```bash
   git clone https://github.com/insistgang/wise_city.git
   cd wise_city
   cp .env.example .env
   # 配置生产环境变量
   docker-compose up -d
   ```

3. **反向代理配置**
   - 使用 Nginx 作为反向代理
   - 配置 SSL 证书
   - 配置域名解析

## 监控和日志

- 应用日志存储在 `logs/` 目录
- 支持结构化日志记录
- 可集成 ELK Stack 进行日志分析

## 故障排除

### 常见问题

1. **模型加载失败**
   - 检查 `yolov8n.pt` 文件是否存在
   - 确保有足够的内存

2. **数据库连接错误**
   - 检查数据库配置
   - 确保数据库服务正常运行

3. **文件上传失败**
   - 检查上传目录权限
   - 确保磁盘空间充足

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目维护者: insistgang
- 邮箱: insistgang@163.com
- GitHub: https://github.com/insistgang/wise_city

## 致谢

- YOLOv8 目标检测框架
- FastAPI Web框架
- Docker 容器化技术
- 所有贡献者和用户

---

## 更新日志

### v1.0.0 (2024-09-04)
- 初始版本发布
- 集成YOLOv8检测功能
- 完整的API接口
- Docker部署支持