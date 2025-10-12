#!/usr/bin/env python3
"""
用户服务
提供用户认证、授权和权限管理功能
"""

import asyncio
import logging
import sys
import hashlib
import secrets
import uuid
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr, field_validator
from enum import Enum
import bcrypt
import jwt
import redis
from redis.exceptions import RedisError

from shared.config import get_config
from shared.exceptions import AuthenticationError, AuthorizationError, ValidationError, UserServiceError
from shared.models import User, APIResponse
from backend.database.user_database import user_db

# 配置日志
logger = logging.getLogger(__name__)

# 安全配置
security = HTTPBearer()

# 数据模型
class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    OPERATOR = "operator"
    USER = "user"
    GUEST = "guest"

class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class UserCreate(BaseModel):
    """用户创建模型"""
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码", min_length=8, max_length=100)
    confirm_password: str = Field(..., description="确认密码")
    full_name: Optional[str] = Field(None, description="全名", max_length=100)
    phone: Optional[str] = Field(None, description="手机号", max_length=20)
    role: UserRole = Field(default=UserRole.USER, description="用户角色")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含数字')
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def validate_confirm_password(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('密码和确认密码不匹配')
        return v

class UserUpdate(BaseModel):
    """用户更新模型"""
    full_name: Optional[str] = Field(None, description="全名", max_length=100)
    phone: Optional[str] = Field(None, description="手机号", max_length=20)
    role: Optional[UserRole] = Field(None, description="用户角色")
    status: Optional[UserStatus] = Field(None, description="用户状态")

class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")

class UserResponse(BaseModel):
    """用户响应模型"""
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, description="全名")
    phone: Optional[str] = Field(None, description="手机号")
    role: UserRole = Field(..., description="用户角色")
    status: UserStatus = Field(..., description="用户状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")

class TokenData(BaseModel):
    """令牌数据模型"""
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    role: UserRole = Field(..., description="用户角色")
    exp: datetime = Field(..., description="过期时间")

class TokenResponse(BaseModel):
    """令牌响应模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")

class UserInDB(BaseModel):
    """数据库中的用户模型"""
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, description="全名")
    phone: Optional[str] = Field(None, description="手机号")
    role: UserRole = Field(..., description="用户角色")
    status: UserStatus = Field(..., description="用户状态")
    hashed_password: str = Field(..., description="加密密码")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")

class Permission(str, Enum):
    """权限枚举"""
    # 用户权限
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # 救援方案权限
    CREATE_RESCUE_PLAN = "create_rescue_plan"
    READ_RESCUE_PLAN = "read_rescue_plan"
    UPDATE_RESCUE_PLAN = "update_rescue_plan"
    DELETE_RESCUE_PLAN = "delete_rescue_plan"
    
    # 知识库权限
    MANAGE_KNOWLEDGE = "manage_knowledge"
    VIEW_KNOWLEDGE = "view_knowledge"
    
    # 系统管理权限
    MANAGE_SYSTEM = "manage_system"
    VIEW_LOGS = "view_logs"
    MANAGE_CONFIG = "manage_config"

class UserService:
    """用户服务类"""
    
    def __init__(self):
        self.config = get_config()
        self.redis_client = None
        self._initialize_redis()
        self.role_permissions = self._load_role_permissions()
        self.db_initialized = False
    
    def _initialize_redis(self):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.Redis(
                host=self.config.database.redis_host,
                port=self.config.database.redis_port,
                password=self.config.database.redis_password,
                db=self.config.database.redis_db,
                decode_responses=True
            )
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis连接初始化成功")
        except Exception as e:
            logger.warning(f"Redis连接初始化失败: {str(e)}")
            self.redis_client = None
    
    def _load_role_permissions(self) -> Dict[UserRole, List[Permission]]:
        """加载角色权限配置"""
        return {
            UserRole.ADMIN: list(Permission),  # 管理员拥有所有权限
            UserRole.OPERATOR: [
                Permission.CREATE_RESCUE_PLAN,
                Permission.READ_RESCUE_PLAN,
                Permission.UPDATE_RESCUE_PLAN,
                Permission.DELETE_RESCUE_PLAN,
                Permission.VIEW_KNOWLEDGE,
                Permission.VIEW_LOGS
            ],
            UserRole.USER: [
                Permission.CREATE_RESCUE_PLAN,
                Permission.READ_RESCUE_PLAN,
                Permission.VIEW_KNOWLEDGE
            ],
            UserRole.GUEST: [
                Permission.READ_RESCUE_PLAN,
                Permission.VIEW_KNOWLEDGE
            ]
        }
    
    async def initialize_database(self):
        """初始化数据库"""
        try:
            await user_db.initialize()
            await user_db.execute_schema("user_schema.sql")
            self.db_initialized = True
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            self.db_initialized = False
    
    async def test_connection(self) -> bool:
        """测试服务连接"""
        try:
            redis_ok = False
            db_ok = False
            
            # 测试Redis连接
            if self.redis_client:
                self.redis_client.ping()
                redis_ok = True
            
            # 测试数据库连接
            if self.db_initialized:
                async with user_db.pool.acquire() as conn:
                    await conn.execute("SELECT 1")
                db_ok = True
            
            return redis_ok and db_ok
        except Exception as e:
            logger.error(f"服务连接测试失败: {str(e)}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """加密密码"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    def _create_access_token(self, user: UserInDB) -> str:
        """创建访问令牌"""
        expire = datetime.utcnow() + timedelta(
            minutes=self.config.security.jwt_access_token_expire_minutes
        )
        to_encode = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "exp": expire
        }
        encoded_jwt = jwt.encode(
            to_encode, 
            self.config.security.jwt_secret_key, 
            algorithm=self.config.security.jwt_algorithm
        )
        return encoded_jwt
    
    def _create_refresh_token(self, user: UserInDB) -> str:
        """创建刷新令牌"""
        expire = datetime.utcnow() + timedelta(
            days=self.config.security.jwt_refresh_token_expire_days
        )
        to_encode = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "exp": expire,
            "type": "refresh"
        }
        encoded_jwt = jwt.encode(
            to_encode, 
            self.config.security.jwt_secret_key, 
            algorithm=self.config.security.jwt_algorithm
        )
        return encoded_jwt
    
    def _verify_token(self, token: str) -> Optional[TokenData]:
        """验证令牌"""
        try:
            payload = jwt.decode(
                token, 
                self.config.security.jwt_secret_key, 
                algorithms=[self.config.security.jwt_algorithm]
            )
            user_id: str = payload.get("user_id")
            username: str = payload.get("username")
            role: str = payload.get("role")
            exp: int = payload.get("exp")
            
            if user_id is None or username is None or role is None or exp is None:
                return None
            
            # 检查令牌是否过期
            if datetime.utcnow() > datetime.fromtimestamp(exp):
                return None
            
            return TokenData(
                user_id=user_id,
                username=username,
                role=UserRole(role),
                exp=datetime.fromtimestamp(exp)
            )
        except jwt.PyJWTError:
            return None
    
    async def _get_user_by_username_or_email(self, username: str, email: str) -> Optional[UserInDB]:
        """根据用户名或邮箱获取用户"""
        if not self.db_initialized:
            return None
        
        try:
            # 先尝试用户名查询
            user_data = await user_db.get_user_by_username(username)
            if user_data:
                return self._dict_to_user_in_db(user_data)
            
            # 再尝试邮箱查询
            user_data = await user_db.get_user_by_email(email)
            if user_data:
                return self._dict_to_user_in_db(user_data)
            
            return None
        except Exception as e:
            logger.error(f"查询用户失败: {str(e)}")
            return None
    
    async def _get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """根据用户ID获取用户"""
        if not self.db_initialized:
            return None
        
        try:
            user_data = await user_db.get_user_by_id(user_id)
            if user_data:
                return self._dict_to_user_in_db(user_data)
            return None
        except Exception as e:
            logger.error(f"查询用户失败: {str(e)}")
            return None
    
    def _dict_to_user_in_db(self, user_data: Dict[str, Any]) -> UserInDB:
        """将数据库查询结果转换为UserInDB对象"""
        return UserInDB(
            id=str(user_data['id']),
            username=user_data['username'],
            email=user_data['email'],
            full_name=user_data.get('full_name'),
            phone=user_data.get('phone'),
            role=UserRole(user_data['role']),
            status=UserStatus(user_data['status']),
            hashed_password=user_data['hashed_password'],
            created_at=user_data['created_at'],
            updated_at=user_data['updated_at'],
            last_login=user_data.get('last_login')
        )
    
    async def _save_user(self, user: UserInDB) -> bool:
        """保存用户到数据库"""
        if not self.db_initialized:
            logger.warning("数据库未初始化，无法保存用户")
            return False
        
        try:
            user_data = {
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'role': user.role.value,
                'status': user.status.value,
                'hashed_password': user.hashed_password
            }
            
            user_id = await user_db.create_user(user_data)
            user.id = user_id
            logger.info(f"用户保存成功: {user.username} (ID: {user_id})")
            return True
        except Exception as e:
            logger.error(f"保存用户失败: {str(e)}")
            return False
    
    async def _update_last_login(self, user_id: str):
        """更新最后登录时间"""
        if not self.db_initialized:
            return
        
        try:
            await user_db.update_last_login(user_id)
            logger.info(f"更新用户 {user_id} 的最后登录时间")
        except Exception as e:
            logger.error(f"更新最后登录时间失败: {str(e)}")
    
    async def _save_refresh_token(self, user_id: str, refresh_token: str):
        """保存刷新令牌到Redis"""
        if self.redis_client:
            key = f"refresh_token:{user_id}"
            expire_time = self.config.security.jwt_refresh_token_expire_days * 24 * 3600
            self.redis_client.setex(key, expire_time, refresh_token)
    
    async def _blacklist_token(self, token: str):
        """将令牌加入黑名单"""
        if self.redis_client:
            # 计算令牌过期时间
            try:
                payload = jwt.decode(
                    token, 
                    self.config.security.jwt_secret_key, 
                    algorithms=[self.config.security.jwt_algorithm],
                    options={"verify_exp": False}
                )
                exp = payload.get("exp", 0)
                if exp > 0:
                    expire_time = exp - int(datetime.utcnow().timestamp())
                    if expire_time > 0:
                        self.redis_client.setex(f"blacklist:{token}", expire_time, "1")
            except jwt.PyJWTError:
                pass
    
    async def _is_token_blacklisted(self, token: str) -> bool:
        """检查令牌是否在黑名单中"""
        if self.redis_client:
            return self.redis_client.exists(f"blacklist:{token}") > 0
        return False
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """创建用户"""
        try:
            # 验证密码
            if user_data.password != user_data.confirm_password:
                raise ValidationError("密码和确认密码不匹配")
            
            # 检查用户名和邮箱是否已存在
            existing_user = await self._get_user_by_username_or_email(
                user_data.username, user_data.email
            )
            if existing_user:
                raise ValidationError("用户名或邮箱已存在")
            
            # 加密密码
            hashed_password = self._hash_password(user_data.password)
            
            # 创建用户
            user_id = str(uuid.uuid4())
            user = UserInDB(
                id=user_id,
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                phone=user_data.phone,
                role=user_data.role,
                status=UserStatus.ACTIVE,
                hashed_password=hashed_password,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # 保存到数据库
            await self._save_user(user)
            
            return UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                phone=user.phone,
                role=user.role,
                status=user.status,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            raise UserServiceError(f"创建用户失败: {str(e)}")
    
    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """验证用户"""
        try:
            # 获取用户
            user = await self._get_user_by_username_or_email(username, username)
            if not user:
                return None
            
            # 验证密码
            if not self._verify_password(password, user.hashed_password):
                return None
            
            # 检查用户状态
            if user.status != UserStatus.ACTIVE:
                return None
            
            # 更新最后登录时间
            await self._update_last_login(user.id)
            
            return user
            
        except Exception as e:
            logger.error(f"验证用户失败: {str(e)}")
            raise UserServiceError(f"验证用户失败: {str(e)}")
    
    async def create_tokens(self, user: UserInDB) -> TokenResponse:
        """创建访问令牌和刷新令牌"""
        try:
            # 创建访问令牌
            access_token = self._create_access_token(user)
            
            # 创建刷新令牌
            refresh_token = self._create_refresh_token(user)
            
            # 保存刷新令牌到Redis
            await self._save_refresh_token(user.id, refresh_token)
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=self.config.security.jwt_access_token_expire_minutes * 60
            )
            
        except Exception as e:
            logger.error(f"创建令牌失败: {str(e)}")
            raise UserServiceError(f"创建令牌失败: {str(e)}")
    
    async def verify_token(self, token: str) -> Optional[TokenData]:
        """验证令牌"""
        try:
            # 检查令牌是否在黑名单中
            if await self._is_token_blacklisted(token):
                return None
            
            return self._verify_token(token)
        except Exception as e:
            logger.error(f"验证令牌失败: {str(e)}")
            return None
    
    async def check_permission(
        self, 
        user_id: str, 
        permission: Permission,
        resource_id: Optional[str] = None
    ) -> bool:
        """检查用户权限"""
        try:
            # 获取用户信息
            user = await self._get_user_by_id(user_id)
            if not user or user.status != UserStatus.ACTIVE:
                return False
            
            # 获取用户角色权限
            user_permissions = self.role_permissions.get(user.role, [])
            
            # 检查权限
            if permission in user_permissions:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"检查权限失败: {str(e)}")
            return False
    
    async def logout_user(self, user_id: str, token: str):
        """用户登出"""
        try:
            # 将令牌加入黑名单
            await self._blacklist_token(token)
            
            # 删除刷新令牌
            if self.redis_client:
                self.redis_client.delete(f"refresh_token:{user_id}")
            
        except Exception as e:
            logger.error(f"用户登出失败: {str(e)}")
            raise UserServiceError(f"用户登出失败: {str(e)}")

# 创建服务实例
user_service = UserService()

# FastAPI应用
app = FastAPI(
    title="用户服务",
    description="用户认证、授权和权限管理服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 依赖注入
def get_user_service() -> UserService:
    return user_service

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """获取当前用户"""
    token = credentials.credentials
    token_data = asyncio.run(user_service.verify_token(token))
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

def require_permission(permission: Permission):
    """权限检查装饰器"""
    def permission_checker(current_user: TokenData = Depends(get_current_user)):
        # 这里应该检查用户权限
        # 简化实现，实际应该调用user_service.check_permission
        return current_user
    return permission_checker

# API路由
@app.get("/", response_model=APIResponse)
async def root():
    """根路径 - 服务信息"""
    return APIResponse(
        success=True,
        message="用户服务运行正常",
        data={
            "service": "用户服务",
            "version": "1.0.0",
            "description": "用户认证、授权和权限管理服务",
            "endpoints": {
                "health": "/health",
                "register": "/register",
                "login": "/login",
                "logout": "/logout",
                "profile": "/profile",
                "users": "/users",
                "docs": "/docs"
            }
        }
    )

@app.get("/health", response_model=APIResponse)
async def health_check(service: UserService = Depends(get_user_service)):
    """健康检查"""
    try:
        is_healthy = await service.test_connection()
        return APIResponse(
            success=is_healthy,
            message="健康检查完成",
            data={"status": "healthy" if is_healthy else "unhealthy"}
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"健康检查失败: {str(e)}",
            data={"status": "unhealthy"}
        )

@app.post("/register", response_model=APIResponse)
async def register_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """用户注册"""
    try:
        user = await service.create_user(user_data)
        return APIResponse(
            success=True,
            message="用户注册成功",
            data=user.model_dump()
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", response_model=APIResponse)
async def login_user(
    login_data: UserLogin,
    service: UserService = Depends(get_user_service)
):
    """用户登录"""
    try:
        user = await service.authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        tokens = await service.create_tokens(user)
        return APIResponse(
            success=True,
            message="登录成功",
            data=tokens.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

@app.post("/logout", response_model=APIResponse)
async def logout_user(
    current_user: TokenData = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """用户登出"""
    try:
        await service.logout_user(current_user.user_id, "")
        return APIResponse(
            success=True,
            message="登出成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登出失败: {str(e)}")

@app.get("/profile", response_model=APIResponse)
async def get_user_profile(
    current_user: TokenData = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """获取用户信息"""
    try:
        user = await service._get_user_by_id(current_user.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
        
        return APIResponse(
            success=True,
            message="获取用户信息成功",
            data=user_response.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

# 启动和关闭事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("用户服务启动中...")
    try:
        # 初始化数据库
        await user_service.initialize_database()
        
        # 测试连接
        is_healthy = await user_service.test_connection()
        if is_healthy:
            logger.info("用户服务启动成功")
        else:
            logger.warning("用户服务启动，但部分连接异常")
    except Exception as e:
        logger.error(f"用户服务启动失败: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("用户服务关闭中...")
    try:
        # 关闭数据库连接
        await user_db.close()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {str(e)}")
    logger.info("用户服务已关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
