#!/usr/bin/env python3
"""
用户服务数据库操作
PostgreSQL 数据库连接和操作
"""

import logging
import sys
import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import uuid
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from psycopg2 import extensions
import time
import locale

# 设置PostgreSQL客户端编码环境变量
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['PGOPTIONS'] = '--client-encoding=UTF8'
# Windows环境下设置locale，避免GBK编码的错误消息
if sys.platform == 'win32':
    try:
        locale.setlocale(locale.LC_ALL, 'C')
    except:
        pass

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from pydantic import BaseModel

from shared.config import get_config
from shared.exceptions import DatabaseError, UserServiceError

# 配置日志
logger = logging.getLogger(__name__)

class UserDatabase:
    """用户数据库操作类"""
    
    def __init__(self):
        self.config = get_config()
        self.pool: Optional[SimpleConnectionPool] = None
        self._connection_string = self._build_connection_string()
    
    def _build_connection_string(self) -> str:
        """构建数据库连接字符串"""
        host = self.config.database.postgres_host
        # 避免 Windows 下 IPv6/解析问题，优先使用 127.0.0.1
        if host == "localhost":
            host = "127.0.0.1"
        return (
            f"host={host} "
            f"port={self.config.database.postgres_port} "
            f"dbname={self.config.database.postgres_db} "
            f"user={self.config.database.postgres_user} "
            f"password={self.config.database.postgres_password} "
            f"sslmode=disable connect_timeout=10 client_encoding=UTF8"
        )
    
    def initialize(self):
        """初始化数据库连接池（带重试与阶段日志）"""
        last_error: Optional[Exception] = None
        
        for attempt in range(1, 6):
            try:
                logger.info(f"[init {attempt}/5] 开始数据库连接初始化")
                
                # 测试单个连接
                test_conn = psycopg2.connect(self._connection_string)
                try:
                    # 强制设置连接编码
                    test_conn.set_client_encoding('UTF8')
                    with test_conn.cursor() as cur:
                        cur.execute("SET client_encoding TO 'UTF8'")
                        # lc_ctype 不能在运行时更改，由数据库初始化时决定
                        cur.execute("SELECT 1")
                    test_conn.commit()
                    logger.info(f"[init {attempt}/5] 单连接探测成功（编码已设置为UTF-8）")
                finally:
                    test_conn.close()

                logger.info(f"[init {attempt}/5] 创建连接池")
                self.pool = SimpleConnectionPool(
                    minconn=1,
                    maxconn=3,
                    dsn=self._connection_string
                )
                
                # 测试连接池中的连接
                conn = self.pool.getconn()
                try:
                    conn.set_client_encoding('UTF8')
                    with conn.cursor() as cur:
                        cur.execute("SET client_encoding TO 'UTF8'")
                        cur.execute("SELECT version()")
                        version = cur.fetchone()
                        logger.info(f"PostgreSQL版本: {version[0] if version else 'unknown'}")
                    conn.commit()
                finally:
                    self.pool.putconn(conn)
                    
                logger.info("数据库连接池初始化成功，编码配置完成")
                return
                
            except psycopg2.OperationalError as oe:
                # 捕获认证错误等操作错误
                last_error = oe
                error_msg = str(oe) if isinstance(oe, str) else "连接失败"
                
                # 尝试从错误对象中提取GBK编码的消息
                try:
                    if hasattr(oe, 'args') and oe.args:
                        error_bytes = oe.args[0] if isinstance(oe.args[0], bytes) else str(oe.args[0]).encode('latin-1')
                        try:
                            error_msg = error_bytes.decode('gbk')
                        except:
                            error_msg = error_bytes.decode('utf-8', errors='replace')
                except:
                    error_msg = "PostgreSQL连接/认证错误"
                
                logger.warning(f"[init {attempt}/5] 数据库操作错误: {error_msg}")
                
                # 认证错误不需要重试
                if 'Password' in error_msg or '认证' in error_msg or 'authentication' in error_msg.lower():
                    logger.error("PostgreSQL认证失败！请检查：")
                    logger.error("  1. PostgreSQL服务是否运行")
                    logger.error("  2. .env文件中的数据库用户名和密码是否正确")
                    logger.error("  3. pg_hba.conf是否允许本地连接")
                    break  # 不再重试认证错误
                
                time.sleep(min(0.5 * attempt, 3.0))
                
            except UnicodeDecodeError as ue:
                last_error = ue
                # 这通常是PostgreSQL返回的GBK编码错误消息导致的
                logger.warning(f"[init {attempt}/5] 编码错误（可能是PostgreSQL返回GBK编码的错误消息）")
                logger.warning("提示：建议使用Docker版PostgreSQL以避免编码问题")
                time.sleep(min(0.5 * attempt, 3.0))
                
            except Exception as e:
                last_error = e
                logger.warning(f"[init {attempt}/5] 数据库初始化失败: {type(e).__name__}")
                time.sleep(min(0.5 * attempt, 3.0))

        # 重试仍失败
        logger.error(f"数据库初始化彻底失败（{5}次重试后）: {type(last_error).__name__}")
        
        # 给出更友好的错误提示
        if isinstance(last_error, psycopg2.OperationalError):
            raise DatabaseError("PostgreSQL连接失败，请检查数据库配置和凭据", "user_service")
        elif isinstance(last_error, UnicodeDecodeError):
            raise DatabaseError("数据库编码错误，建议使用Docker版PostgreSQL", "user_service")
        else:
            raise DatabaseError(f"数据库初始化失败: {type(last_error).__name__}", "user_service")
    
    def _setup_connection(self, conn):
        """设置连接参数"""
        try:
            with conn.cursor() as cur:
                # 设置连接超时
                cur.execute("SET statement_timeout = '5s'")
                # 设置空闲超时
                cur.execute("SET idle_in_transaction_session_timeout = '30s'")
                # 设置连接编码
                cur.execute("SET client_encoding = 'utf8'")
            conn.commit()
        except Exception as e:
            logger.warning(f"连接设置失败: {str(e)}")
    
    def close(self):
        """关闭数据库连接池"""
        if self.pool:
            self.pool.closeall()
            logger.info("数据库连接池已关闭")
    
    def execute_schema(self, schema_file: str):
        """执行SQL架构文件"""
        try:
            schema_path = Path(__file__).parent / schema_file
            logger.info(f"正在读取SQL文件: {schema_path}")
            
            # 明确使用UTF-8编码读取SQL文件
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            logger.info(f"SQL文件读取成功，长度: {len(schema_sql)} 字符")
            
            conn = self.pool.getconn()
            try:
                # 确保连接使用UTF-8编码
                conn.set_client_encoding('UTF8')
                with conn.cursor() as cur:
                    cur.execute("SET client_encoding TO 'UTF8'")
                    # 分割并执行SQL语句
                    statements = self._split_sql_statements(schema_sql)
                    for i, stmt in enumerate(statements):
                        if stmt.strip():
                            logger.debug(f"执行SQL语句 {i+1}/{len(statements)}")
                            cur.execute(stmt)
                conn.commit()
                logger.info(f"成功执行SQL架构: {schema_file} ({len(statements)} 条语句)")
            finally:
                self.pool.putconn(conn)
                
        except UnicodeDecodeError as ue:
            logger.error(f"SQL文件编码错误 {schema_file}: {repr(ue)} - 请确保文件是UTF-8编码")
            raise DatabaseError(f"SQL文件编码错误: {repr(ue)}", "user_service")
        except Exception as e:
            logger.error(f"执行SQL架构失败 {schema_file}: {type(e).__name__}: {repr(e)}")
            raise DatabaseError(f"执行SQL架构失败: {repr(e)}", "user_service")

    def _split_sql_statements(self, sql_text: str) -> list[str]:
        """将 SQL 脚本拆分为语句列表，避免在 $$ 函数体内误分割。"""
        statements = []
        current = []
        in_dollar_block = False
        i = 0
        length = len(sql_text)
        while i < length:
            ch = sql_text[i]
            # 处理 $$ 块边界
            if ch == '$' and i + 1 < length and sql_text[i:i+2] == '$$':
                in_dollar_block = not in_dollar_block
                current.append('$$')
                i += 2
                continue
            if ch == ';' and not in_dollar_block:
                statements.append(''.join(current).strip())
                current = []
                i += 1
                continue
            current.append(ch)
            i += 1
        tail = ''.join(current).strip()
        if tail:
            statements.append(tail)
        return statements
    
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """创建用户"""
        try:
            conn = self.pool.getconn()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        INSERT INTO users (username, email, full_name, phone, role, status, hashed_password)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        user_data['username'],
                        user_data['email'],
                        user_data.get('full_name'),
                        user_data.get('phone'),
                        user_data['role'],
                        user_data['status'],
                        user_data['hashed_password']
                    ))
                    user_id = cur.fetchone()['id']
                conn.commit()
                return str(user_id)
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            raise DatabaseError(f"创建用户失败: {str(e)}", "user_service")
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        try:
            conn = self.pool.getconn()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, username, email, full_name, phone, role, status, 
                               hashed_password, created_at, updated_at, last_login
                        FROM users 
                        WHERE username = %s
                    """, (username,))
                    
                    row = cur.fetchone()
                    if row:
                        return dict(row)
                    return None
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"获取用户失败: {str(e)}")
            raise DatabaseError(f"获取用户失败: {str(e)}", "user_service")
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        try:
            conn = self.pool.getconn()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, username, email, full_name, phone, role, status, 
                               hashed_password, created_at, updated_at, last_login
                        FROM users 
                        WHERE email = %s
                    """, (email,))
                    
                    row = cur.fetchone()
                    if row:
                        return dict(row)
                    return None
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"获取用户失败: {str(e)}")
            raise DatabaseError(f"获取用户失败: {str(e)}", "user_service")
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根据用户ID获取用户"""
        try:
            conn = self.pool.getconn()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, username, email, full_name, phone, role, status, 
                               hashed_password, created_at, updated_at, last_login
                        FROM users 
                        WHERE id = %s
                    """, (user_id,))
                    
                    row = cur.fetchone()
                    if row:
                        return dict(row)
                    return None
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"获取用户失败: {str(e)}")
            raise DatabaseError(f"获取用户失败: {str(e)}", "user_service")
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
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
            
            conn = self.pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        UPDATE users 
                        SET {', '.join(set_clauses)}
                        WHERE id = ${param_count}
                    """, values)
                    
                    return True
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"更新用户失败: {str(e)}")
            raise DatabaseError(f"更新用户失败: {str(e)}", "user_service")
    
    def update_last_login(self, user_id: str) -> bool:
        """更新最后登录时间"""
        try:
            conn = self.pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE users 
                        SET last_login = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (user_id,))
                    return True
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"更新最后登录时间失败: {str(e)}")
            raise DatabaseError(f"更新最后登录时间失败: {str(e)}", "user_service")
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        try:
            conn = self.pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
                    return True
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"删除用户失败: {str(e)}")
            raise DatabaseError(f"删除用户失败: {str(e)}", "user_service")
    
    def create_session(self, user_id: str, access_token: str, refresh_token: str, expires_at: datetime) -> str:
        """创建用户会话"""
        try:
            access_token_hash = hashlib.sha256(access_token.encode()).hexdigest()
            refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            
            conn = self.pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO user_sessions (user_id, access_token_hash, refresh_token_hash, expires_at)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                    """, (user_id, access_token_hash, refresh_token_hash, expires_at))
                    
                    session_id = cur.fetchone()['id']
                    return str(session_id)
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"创建会话失败: {str(e)}")
            raise DatabaseError(f"创建会话失败: {str(e)}", "user_service")
    
    def get_session_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """根据令牌获取会话"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            conn = self.pool.getconn()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT s.id, s.user_id, s.access_token_hash, s.refresh_token_hash, 
                               s.expires_at, s.created_at, s.is_active,
                               u.username, u.email, u.role, u.status
                        FROM user_sessions s
                        JOIN users u ON s.user_id = u.id
                        WHERE (s.access_token_hash = %s OR s.refresh_token_hash = %s)
                        AND s.expires_at > CURRENT_TIMESTAMP
                        AND s.is_active = TRUE
                    """, (token_hash, token_hash))
                    
                    row = cur.fetchone()
                    if row:
                        return dict(row)
                    return None
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"获取会话失败: {str(e)}")
            raise DatabaseError(f"获取会话失败: {str(e)}", "user_service")
    
    def deactivate_session(self, user_id: str, token: str) -> bool:
        """停用会话"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            conn = self.pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE user_sessions 
                        SET is_active = FALSE
                        WHERE user_id = %s AND (access_token_hash = %s OR refresh_token_hash = %s)
                    """, (user_id, token_hash, token_hash))
                    
                    return True
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"停用会话失败: {str(e)}")
            raise DatabaseError(f"停用会话失败: {str(e)}", "user_service")
    
    def add_token_to_blacklist(self, token: str, expires_at: datetime) -> bool:
        """将令牌加入黑名单"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            conn = self.pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO token_blacklist (token_hash, expires_at)
                        VALUES (%s, %s)
                        ON CONFLICT (token_hash) DO NOTHING
                    """, (token_hash, expires_at))
                    
                    return True
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"添加令牌到黑名单失败: {str(e)}")
            raise DatabaseError(f"添加令牌到黑名单失败: {str(e)}", "user_service")
    
    def is_token_blacklisted(self, token: str) -> bool:
        """检查令牌是否在黑名单中"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            conn = self.pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 1 FROM token_blacklist 
                        WHERE token_hash = %s AND expires_at > CURRENT_TIMESTAMP
                    """, (token_hash,))
                    
                    return cur.fetchone() is not None
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"检查令牌黑名单失败: {str(e)}")
            raise DatabaseError(f"检查令牌黑名单失败: {str(e)}", "user_service")
    
    def log_user_login(self, user_id: Optional[str], username: str, ip_address: str, 
                           user_agent: str, login_status: str, failure_reason: Optional[str] = None) -> bool:
        """记录用户登录日志"""
        try:
            conn = self.pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO user_login_logs (user_id, username, ip_address, user_agent, login_status, failure_reason)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, username, ip_address, user_agent, login_status, failure_reason))
                    
                    return True
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"记录登录日志失败: {str(e)}")
            raise DatabaseError(f"记录登录日志失败: {str(e)}", "user_service")
    
    def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        try:
            conn = self.pool.getconn()
            try:
                with conn.cursor() as cur:
                    result = cur.fetchval("SELECT cleanup_expired_sessions()")
                    return result or 0
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"清理过期会话失败: {str(e)}")
            raise DatabaseError(f"清理过期会话失败: {str(e)}", "user_service")
    
    def cleanup_expired_tokens(self) -> int:
        """清理过期令牌"""
        try:
            conn = self.pool.getconn()
            try:
                with conn.cursor() as cur:
                    result = cur.fetchval("SELECT cleanup_expired_tokens()")
                    return result or 0
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"清理过期令牌失败: {str(e)}")
            raise DatabaseError(f"清理过期令牌失败: {str(e)}", "user_service")
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """获取用户权限"""
        try:
            conn = self.pool.getconn()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT permission FROM user_permissions WHERE user_id = %s
                    """, (user_id,))
                    
                    return [row['permission'] for row in cur.fetchall()]
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"获取用户权限失败: {str(e)}")
            raise DatabaseError(f"获取用户权限失败: {str(e)}", "user_service")
    
    def grant_permission(self, user_id: str, permission: str, granted_by: str) -> bool:
        """授予用户权限"""
        try:
            conn = self.pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO user_permissions (user_id, permission, granted_by)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (user_id, permission) DO NOTHING
                    """, (user_id, permission, granted_by))
                    
                    return True
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"授予权限失败: {str(e)}")
            raise DatabaseError(f"授予权限失败: {str(e)}", "user_service")
    
    def revoke_permission(self, user_id: str, permission: str) -> bool:
        """撤销用户权限"""
        try:
            conn = self.pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM user_permissions 
                        WHERE user_id = %s AND permission = %s
                    """, (user_id, permission))
                    
                    return True
            finally:
                self.pool.putconn(conn)
                
        except Exception as e:
            logger.error(f"撤销权限失败: {str(e)}")
            raise DatabaseError(f"撤销权限失败: {str(e)}", "user_service")

# 创建全局数据库实例
user_db = UserDatabase()
