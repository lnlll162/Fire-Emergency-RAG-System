-- 用户表


CREATE TABLE IF NOT EXISTS users (


    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),


    username VARCHAR(50) UNIQUE NOT NULL,


    email VARCHAR(255) UNIQUE NOT NULL,


    full_name VARCHAR(100),


    phone VARCHAR(20),


    role VARCHAR(20) NOT NULL DEFAULT 'user',


    status VARCHAR(20) NOT NULL DEFAULT 'active',


    hashed_password VARCHAR(255) NOT NULL,


    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,


    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,


    last_login TIMESTAMP WITH TIME ZONE


);





-- 更新时间触发器


CREATE OR REPLACE FUNCTION update_updated_at()


RETURNS TRIGGER AS $$


BEGIN


   NEW.updated_at = now();


   RETURN NEW;


END;


$$ language 'plpgsql';





DROP TRIGGER IF EXISTS users_updated_at ON users;
CREATE TRIGGER users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE PROCEDURE update_updated_at();





-- 索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);


