-- 火灾应急救援RAG系统 - PostgreSQL初始化脚本

-- 创建数据库（如果不存在）
-- 数据库已由Docker环境变量创建，无需重复创建

-- 使用数据库
\c fire_emergency;

-- 启用必要扩展（优先 pgcrypto，失败则尝试 uuid-ossp）
CREATE EXTENSION IF NOT EXISTS pgcrypto;
DO $$ BEGIN
    BEGIN
        PERFORM 1 FROM pg_extension WHERE extname = 'pgcrypto';
        IF NOT FOUND THEN
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        END IF;
    EXCEPTION WHEN others THEN
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    END;
END $$;

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建救援方案表
CREATE TABLE IF NOT EXISTS rescue_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('低', '中', '高', '紧急')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    steps JSONB NOT NULL,
    equipment_list JSONB NOT NULL,
    warnings JSONB NOT NULL,
    estimated_duration INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建用户输入记录表
CREATE TABLE IF NOT EXISTS user_inputs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rescue_plan_id UUID REFERENCES rescue_plans(id) ON DELETE CASCADE,
    items JSONB NOT NULL,
    environment JSONB NOT NULL,
    additional_info TEXT,
    urgency_level VARCHAR(20) DEFAULT '中',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建系统日志表
CREATE TABLE IF NOT EXISTS system_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name VARCHAR(50) NOT NULL,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_rescue_plans_user_id ON rescue_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_rescue_plans_created_at ON rescue_plans(created_at);
CREATE INDEX IF NOT EXISTS idx_user_inputs_user_id ON user_inputs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_inputs_rescue_plan_id ON user_inputs(rescue_plan_id);
CREATE INDEX IF NOT EXISTS idx_system_logs_service_name ON system_logs(service_name);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON system_logs(created_at);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要更新时间的表创建触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rescue_plans_updated_at BEFORE UPDATE ON rescue_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 插入默认管理员用户
INSERT INTO users (username, email, password_hash, full_name, role) 
VALUES (
    'admin', 
    'admin@fire-emergency.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HSyK8m2', -- password: admin123
    '系统管理员', 
    'admin'
) ON CONFLICT (username) DO NOTHING;

-- 插入测试用户
INSERT INTO users (username, email, password_hash, full_name, role) 
VALUES (
    'testuser', 
    'test@fire-emergency.com', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HSyK8m2', -- password: admin123
    '测试用户', 
    'user'
) ON CONFLICT (username) DO NOTHING;
