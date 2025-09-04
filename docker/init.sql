-- 初始化数据库脚本

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建用户表（如果需要的话）
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建检测结果表
CREATE TABLE IF NOT EXISTS detection_results (
    id SERIAL PRIMARY KEY,
    image_path VARCHAR(255) NOT NULL,
    total_violations INTEGER DEFAULT 0,
    confidence_threshold FLOAT DEFAULT 0.5,
    iou_threshold FLOAT DEFAULT 0.45,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- 创建检测详情表
CREATE TABLE IF NOT EXISTS detections (
    id SERIAL PRIMARY KEY,
    result_id INTEGER REFERENCES detection_results(id) ON DELETE CASCADE,
    class_id INTEGER NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL,
    bbox_x FLOAT NOT NULL,
    bbox_y FLOAT NOT NULL,
    bbox_width FLOAT NOT NULL,
    bbox_height FLOAT NOT NULL,
    area FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_detection_results_created_at ON detection_results(created_at);
CREATE INDEX IF NOT EXISTS idx_detections_result_id ON detections(result_id);
CREATE INDEX IF NOT EXISTS idx_detections_class_name ON detections(class_name);

-- 插入测试数据（可选）
-- INSERT INTO users (username, email, password_hash) VALUES
-- ('admin', 'admin@example.com', '$2b$12$example_hash_here');

COMMIT;