# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

## 项目概述

这是一个智慧城市管理系统（智慧城管），使用多模态AI进行智能违规检测。这是第十一届中国研究生智慧城市技术与创意设计大赛的参赛作品。该系统使用基于YOLOv8的目标检测技术来识别建筑违规和城市管理问题。

## 常用开发命令

### 应用启动
```bash
# 开发模式（自动重载）
python run.py --reload

# 生产模式
python run.py --host 0.0.0.0 --port 8000

# 自定义配置
python run.py --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

### Docker部署
```bash
# 开发环境
docker-compose -f docker-compose.dev.yml up -d

# 生产环境
docker-compose up -d
```

### 测试
```bash
# 运行所有测试
pytest tests/

# 运行覆盖率测试
pytest --cov=app tests/

# 运行特定测试文件
pytest tests/test_detection.py
```

### 代码质量
```bash
# 使用black格式化代码
black app/

# 检查代码风格
flake8 app/

# 排序导入
isort app/

# 类型检查
mypy app/
```

### 依赖管理
```bash
# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -e ".[dev]"
```

## 高层架构

### 核心组件

1. **FastAPI应用** (`app/main.py`)
   - 主入口点，包含生命周期管理
   - CORS配置和静态文件服务
   - 健康检查和演示端点

2. **AI服务** (`app/services/ai_service.py`)
   - YOLOv8模型管理和加载
   - 违规检测和分类
   - 多模态图像分析（增强、结构分析）
   - 性能基准测试

3. **数据库层** (`app/core/database.py`)
   - 异步SQLAlchemy，支持PostgreSQL/SQLite
   - 连接池和生命周期管理
   - Alembic迁移支持

4. **API结构** (`app/api/`)
   - 按版本组织的RESTful API端点
   - `app/api/api.py`中的模块化路由系统
   - 检测、文件、法律法规和系统的独立模块

5. **模型** (`app/models/`)
   - 违规行为、法律法规、数据库实体的数据模型
   - 用于请求/响应验证的Pydantic模型
   - 违规类型分类系统

### 关键特性

- **多模态AI检测**: 结合YOLOv8目标检测与图像增强和结构分析
- **违规分类**: 6类建筑违规，包含严重性评估
- **性能目标**: mAP ≥ 0.85，响应时间 ≤ 3秒，50 FPS @ 1080p
- **多格式支持**: JPG、PNG、BMP、TIF/TIFF、WebP
- **实时处理**: GPU加速优化性能

### 文件结构
```
app/
├── api/           # API路由和端点
├── core/          # 核心配置和数据库
├── models/        # 数据模型和模式
├── services/      # 业务逻辑服务
└── utils/         # 工具函数

data/
├── uploads/       # 待处理的上传文件
└── results/       # 检测结果和输出

models/            # AI模型文件（YOLOv8权重）
static/            # 静态文件和演示界面
```

### 配置

- `.env`文件中的环境变量
- `app/core/config.py`中的Pydantic设置
- 可配置的模型路径和性能阈值
- 数据库连接字符串和Redis缓存设置

### 开发注意事项

- 系统支持检测和分类两种模型
- GPU加速在可用时自动启用
- 图像预处理包括对比度增强、降噪和边缘锐化
- 模型加载时自动运行性能基准测试
- 违规分类系统将YOLO类别映射到违规类型

### API端点

主要端点包括：
- `POST /api/v1/detect/image` - 基于图像的违规检测
- `POST /api/v1/files/upload` - 文件上传处理
- `GET /api/v1/legal/regulations` - 法律法规查询
- `GET /health` - 系统健康检查
- `/docs` - 交互式API文档