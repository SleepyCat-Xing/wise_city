# Makefile for 违章建筑智能检测系统

.PHONY: help install dev test lint format clean docker-build docker-up docker-down

help:		## 显示帮助信息
	@echo "违章建筑智能检测系统 - 可用命令:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:	## 安装依赖
	pip install -r requirements.txt

dev:		## 安装开发依赖
	pip install -e .[dev]

test:		## 运行测试
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term

lint:		## 代码质量检查
	flake8 app tests
	mypy app

format:		## 格式化代码
	black app tests
	isort app tests

pre-commit:	## 运行pre-commit检查
	pre-commit run --all-files

clean:		## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

run:		## 启动服务（开发模式）
	python run.py --reload --log-level debug

run-prod:	## 启动服务（生产模式）
	python run.py --workers 4

docker-build:	## 构建Docker镜像
	docker-compose build

docker-up:	## 启动Docker服务
	docker-compose up -d

docker-down:	## 停止Docker服务
	docker-compose down

docker-dev:	## 启动开发环境Docker服务
	docker-compose -f docker-compose.dev.yml up -d

docker-logs:	## 查看Docker日志
	docker-compose logs -f

docker-clean:	## 清理Docker资源
	docker-compose down -v
	docker system prune -f

init-db:	## 初始化数据库（如果需要）
	python -c "from app.database import init_db; init_db()"

backup-data:	## 备份数据
	@echo "备份数据功能待实现"

restore-data:	## 恢复数据
	@echo "恢复数据功能待实现"

setup:		## 项目初始化设置
	cp .env.example .env
	mkdir -p data/uploads data/results logs models
	@echo "请编辑 .env 文件配置必要参数"