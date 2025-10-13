#!/usr/bin/env python3
"""
用户服务数据库操作
PostgreSQL 数据库连接和操作
"""

import asyncio
import logging
import sys
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import uuid

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import asyncpg
from asyncpg import Pool, Connection
from pydantic import BaseModel

from shared.config import get_config
from shared.exceptions import DatabaseError, UserServiceError

# 配置日志
logger = logging.getLogger(__name__)

class UserDatabase:
    """用户数据库操作类"""
    
    def __init__(self):
        self.config = get_config()
        self.pool: Optional[Pool] = None
        self._connection_string = self._build_connection_string()
    
    def _build_connection_string(self) -> str:
        """构建数据库连接字符串"""
        return (
            f"postgresql://{self.config.database.postgres_user}:"
            f"{self.config.database.postgres_password}@"
            f"{self.config.database.postgres_host}:"
            f"{self.config.database.postgres_port}/"
            f"{self.config.database.postgres_db}"
        )
    
    async def initialize(self):
        """初始化数据库连接池"""
        try:
            self.pool = await asyncpg.create_pool(
                self._connection_string,
                min_size=1,
                max_size=3,  # 进一步减少连接数
                command_timeout=5,  # 减少超时时间
                server_settings={
                    'application_name': 'fire_emergency_user_service',
                    'client_encoding': 'utf8',  # 明确指定编码
                },
                # 添加连接池配置
                max_queries=50000,
                max_inactive_connection_lifetime=300.0,  # 5分钟
                setup=self._setup_connection  # 添加连接设置
            )
            logger.info("数据库连接池初始化成功")
            
            # 测试连接
            async with self.pool.acquire() as conn:
                await conn.execute("SELECT 1")
            logger.info("数据库连接测试成功")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            raise DatabaseError(f"数据库初始化失败: {str(e)}", "user_service")
    
    async def _setup_connection(self, conn):
        """设置连接参数"""
        try:
            # 设置连接超时
            await conn.execute("SET statement_timeout = '5s'")
            # 设置空闲超时
            await conn.execute("SET idle_in_transaction_session_timeout = '30s'")
            # 设置连接编码
            await conn.execute("SET client_encoding = 'utf8'")
        except Exception as e:
            logger.warning(f"连接设置失败: {str(e)}")
    
    async def close(self):
        """关闭数据库连接池"""
        if self.pool:
            await self.pool.close()
            logger.info("数据库连接池已关闭")
    
    async def execute_schema(self, schema_file: str):
        """执行数据库模式文件"""
        try:
            schema_path = Path(__file__).parent / schema_file
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            async with self.pool.acquire() as conn:
                await conn.execute(schema_sql)
            logger.info(f"数据库模式文件 {schema_file} 执行成功")
            
        except Exception as e:
            logger.error(f"执行数据库模式失败: {str(e)}")
            raise DatabaseError(f"执行数据库模式失败: {str(e)}", "user_service")
    
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """创建用户"""
        try:
            async with self.pool.acquire() as conn:
                user_id = await conn.fetchval("""
                    INSERT INTO users (username, email, full_name, phone, role, status, hashed_password)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING id
                """, 
                user_data['username'],
                user_data['email'],
                user_data.get('full_name'),
                user_data.get('phone'),
                user_data['role'],
                user_data['status'],
                user_data['hashed_password']
                )
                return str(user_id)
                
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            raise DatabaseError(f"创建用户失败: {str(e)}", "user_service")
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT id, username, email, full_name, phone, role, status, 
                           hashed_password, created_at, updated_at, last_login
                    FROM users 
                    WHERE username = $1
                """, username)
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"获取用户失败: {str(e)}")
            raise DatabaseError(f"获取用户失败: {str(e)}", "user_service")
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT id, username, email, full_name, phone, role, status, 
                           hashed_password, created_at, updated_at, last_login
                    FROM users 
                    WHERE email = $1
                """, email)
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"获取用户失败: {str(e)}")
            raise DatabaseError(f"获取用户失败: {str(e)}", "user_service")
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根据用户ID获取用户"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT id, username, email, full_name, phone, role, status, 
                           hashed_password, created_at, updated_at, last_login
                    FROM users 
                    WHERE id = $1
                """, user_id)
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"获取用户失败: {str(e)}")
            raise DatabaseError(f"获取用户失败: {str(e)}", "user_service")
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """更新用户信息"""
        try:
            # 构建动态更新SQL
            set_clauses = []
            values = []
            param_count = 1
            
            for key, value in update_data.items():
                if key in ['full_name', 'phone', 'role', 'status']:
                    set_clauses.append(f"{key} = ${param_count}")
                    values.append(value)
                    param_count += 1
            
            if not set_clauses:
                return True
            
            values.append(user_id)
            
            async with self.pool.acquire() as conn:
                await conn.execute(f"""
                    UPDATE users 
                    SET {', '.join(set_clauses)}
                    WHERE id = ${param_count}
                """, *values)
                
                return True
                
        except Exception as e:
            logger.error(f"更新用户失败: {str(e)}")
            raise DatabaseError(f"更新用户失败: {str(e)}", "user_service")
    
    async def update_last_login(self, user_id: str) -> bool:
        """更新最后登录时间"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE users 
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE id = $1
                """, user_id)
                return True
                
        except Exception as e:
            logger.error(f"更新最后登录时间失败: {str(e)}")
            raise DatabaseError(f"更新最后登录时间失败: {str(e)}", "user_service")
    
    async def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("DELETE FROM users WHERE id = $1", user_id)
                return True
                
        except Exception as e:
            logger.error(f"删除用户失败: {str(e)}")
            raise DatabaseError(f"删除用户失败: {str(e)}", "user_service")
    
    async def create_session(self, user_id: str, access_token: str, refresh_token: str, expires_at: datetime) -> str:
        """创建用户会话"""
        try:
            access_token_hash = hashlib.sha256(access_token.encode()).hexdigest()
            refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            
            async with self.pool.acquire() as conn:
                session_id = await conn.fetchval("""
                    INSERT INTO user_sessions (user_id, access_token_hash, refresh_token_hash, expires_at)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                """, user_id, access_token_hash, refresh_token_hash, expires_at)
                
                return str(session_id)
                
        except Exception as e:
            logger.error(f"创建会话失败: {str(e)}")
            raise DatabaseError(f"创建会话失败: {str(e)}", "user_service")
    
    async def get_session_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """根据令牌获取会话"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT s.id, s.user_id, s.access_token_hash, s.refresh_token_hash, 
                           s.expires_at, s.created_at, s.is_active,
                           u.username, u.email, u.role, u.status
                    FROM user_sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE (s.access_token_hash = $1 OR s.refresh_token_hash = $1)
                    AND s.expires_at > CURRENT_TIMESTAMP
                    AND s.is_active = TRUE
                """, token_hash)
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"获取会话失败: {str(e)}")
            raise DatabaseError(f"获取会话失败: {str(e)}", "user_service")
    
    async def deactivate_session(self, user_id: str, token: str) -> bool:
        """停用会话"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE user_sessions 
                    SET is_active = FALSE
                    WHERE user_id = $1 AND (access_token_hash = $2 OR refresh_token_hash = $2)
                """, user_id, token_hash)
                
                return True
                
        except Exception as e:
            logger.error(f"停用会话失败: {str(e)}")
            raise DatabaseError(f"停用会话失败: {str(e)}", "user_service")
    
    async def add_token_to_blacklist(self, token: str, expires_at: datetime) -> bool:
        """将令牌加入黑名单"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO token_blacklist (token_hash, expires_at)
                    VALUES ($1, $2)
                    ON CONFLICT (token_hash) DO NOTHING
                """, token_hash, expires_at)
                
                return True
                
        except Exception as e:
            logger.error(f"添加令牌到黑名单失败: {str(e)}")
            raise DatabaseError(f"添加令牌到黑名单失败: {str(e)}", "user_service")
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """检查令牌是否在黑名单中"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT 1 FROM token_blacklist 
                    WHERE token_hash = $1 AND expires_at > CURRENT_TIMESTAMP
                """, token_hash)
                
                return row is not None
                
        except Exception as e:
            logger.error(f"检查令牌黑名单失败: {str(e)}")
            raise DatabaseError(f"检查令牌黑名单失败: {str(e)}", "user_service")
    
    async def log_user_login(self, user_id: Optional[str], username: str, ip_address: str, 
                           user_agent: str, login_status: str, failure_reason: Optional[str] = None) -> bool:
        """记录用户登录日志"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO user_login_logs (user_id, username, ip_address, user_agent, login_status, failure_reason)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, user_id, username, ip_address, user_agent, login_status, failure_reason)
                
                return True
                
        except Exception as e:
            logger.error(f"记录登录日志失败: {str(e)}")
            raise DatabaseError(f"记录登录日志失败: {str(e)}", "user_service")
    
    async def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT cleanup_expired_sessions()")
                return result or 0
                
        except Exception as e:
            logger.error(f"清理过期会话失败: {str(e)}")
            raise DatabaseError(f"清理过期会话失败: {str(e)}", "user_service")
    
    async def cleanup_expired_tokens(self) -> int:
        """清理过期令牌"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval("SELECT cleanup_expired_tokens()")
                return result or 0
                
        except Exception as e:
            logger.error(f"清理过期令牌失败: {str(e)}")
            raise DatabaseError(f"清理过期令牌失败: {str(e)}", "user_service")
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """获取用户权限"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT permission FROM user_permissions WHERE user_id = $1
                """, user_id)
                
                return [row['permission'] for row in rows]
                
        except Exception as e:
            logger.error(f"获取用户权限失败: {str(e)}")
            raise DatabaseError(f"获取用户权限失败: {str(e)}", "user_service")
    
    async def grant_permission(self, user_id: str, permission: str, granted_by: str) -> bool:
        """授予用户权限"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO user_permissions (user_id, permission, granted_by)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id, permission) DO NOTHING
                """, user_id, permission, granted_by)
                
                return True
                
        except Exception as e:
            logger.error(f"授予权限失败: {str(e)}")
            raise DatabaseError(f"授予权限失败: {str(e)}", "user_service")
    
    async def revoke_permission(self, user_id: str, permission: str) -> bool:
        """撤销用户权限"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    DELETE FROM user_permissions 
                    WHERE user_id = $1 AND permission = $2
                """, user_id, permission)
                
                return True
                
        except Exception as e:
            logger.error(f"撤销权限失败: {str(e)}")
            raise DatabaseError(f"撤销权限失败: {str(e)}", "user_service")

# 创建全局数据库实例
user_db = UserDatabase()
