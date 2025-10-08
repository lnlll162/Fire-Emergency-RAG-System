"""
火灾应急救援RAG系统 - 统一HTTP客户端
提供服务间通信的统一接口
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
from shared.service_registry import ServiceRegistry
from shared.models import APIResponse, ErrorResponse

logger = logging.getLogger(__name__)


class ServiceCommunicationError(Exception):
    """服务通信异常"""
    pass


class ServiceTimeoutError(ServiceCommunicationError):
    """服务超时异常"""
    pass


class ServiceUnavailableError(ServiceCommunicationError):
    """服务不可用异常"""
    pass


class ServiceClient:
    """服务间通信客户端"""
    
    def __init__(
        self,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0
    ):
        """
        初始化HTTP客户端
        
        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间（秒）
            circuit_breaker_threshold: 熔断器阈值
            circuit_breaker_timeout: 熔断器超时时间（秒）
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        
        # 熔断器状态
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # 创建HTTP客户端
        self.client = httpx.AsyncClient(
            timeout=timeout,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
    
    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        调用其他服务
        
        Args:
            service_name: 服务名称
            endpoint: 端点路径
            method: HTTP方法
            data: 请求数据
            params: 查询参数
            headers: 请求头
            timeout: 超时时间
            
        Returns:
            Dict[str, Any]: 响应数据
            
        Raises:
            ServiceCommunicationError: 服务通信异常
            ServiceTimeoutError: 服务超时异常
            ServiceUnavailableError: 服务不可用异常
        """
        # 检查熔断器状态
        if self._is_circuit_breaker_open(service_name):
            raise ServiceUnavailableError(f"服务 {service_name} 熔断器开启")
        
        # 获取服务URL
        try:
            service_url = ServiceRegistry.get_service_url(service_name)
        except ValueError as e:
            raise ServiceCommunicationError(f"服务配置错误: {str(e)}")
        
        url = f"{service_url}{endpoint}"
        
        # 设置默认请求头
        default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "Fire-Emergency-RAG-System/1.0.0"
        }
        if headers:
            default_headers.update(headers)
        
        # 执行请求
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"调用服务 {service_name}: {method} {url} (尝试 {attempt + 1}/{self.max_retries + 1})")
                
                response = await self.client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=default_headers,
                    timeout=timeout or self.timeout
                )
                
                # 记录成功请求
                self._record_success(service_name)
                
                # 检查响应状态
                if response.status_code >= 400:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"message": response.text}
                    raise ServiceCommunicationError(f"服务 {service_name} 返回错误 {response.status_code}: {error_data}")
                
                # 解析响应
                if response.headers.get("content-type", "").startswith("application/json"):
                    return response.json()
                else:
                    return {"data": response.text}
                    
            except httpx.TimeoutException as e:
                last_exception = ServiceTimeoutError(f"服务 {service_name} 请求超时: {str(e)}")
                logger.warning(f"服务 {service_name} 请求超时 (尝试 {attempt + 1}/{self.max_retries + 1})")
                
            except httpx.ConnectError as e:
                last_exception = ServiceUnavailableError(f"服务 {service_name} 连接失败: {str(e)}")
                logger.warning(f"服务 {service_name} 连接失败 (尝试 {attempt + 1}/{self.max_retries + 1})")
                
            except httpx.HTTPError as e:
                last_exception = ServiceCommunicationError(f"服务 {service_name} HTTP错误: {str(e)}")
                logger.warning(f"服务 {service_name} HTTP错误 (尝试 {attempt + 1}/{self.max_retries + 1})")
                
            except Exception as e:
                last_exception = ServiceCommunicationError(f"服务 {service_name} 未知错误: {str(e)}")
                logger.error(f"服务 {service_name} 未知错误 (尝试 {attempt + 1}/{self.max_retries + 1}): {str(e)}")
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.max_retries:
                await asyncio.sleep(self.retry_delay * (2 ** attempt))  # 指数退避
        
        # 记录失败请求
        self._record_failure(service_name)
        
        # 抛出最后一个异常
        if last_exception:
            raise last_exception
        else:
            raise ServiceCommunicationError(f"服务 {service_name} 调用失败")
    
    async def health_check(self, service_name: str) -> bool:
        """
        检查服务健康状态
        
        Args:
            service_name: 服务名称
            
        Returns:
            bool: 服务是否健康
        """
        try:
            health_url = ServiceRegistry.get_health_check_url(service_name)
            response = await self.client.get(health_url, timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"服务 {service_name} 健康检查失败: {str(e)}")
            return False
    
    async def health_check_all(self) -> Dict[str, bool]:
        """
        检查所有服务健康状态
        
        Returns:
            Dict[str, bool]: 各服务健康状态
        """
        services = ServiceRegistry.list_services()
        health_status = {}
        
        tasks = [self.health_check(service) for service in services]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for service, result in zip(services, results):
            if isinstance(result, Exception):
                health_status[service] = False
                logger.error(f"服务 {service} 健康检查异常: {str(result)}")
            else:
                health_status[service] = result
        
        return health_status
    
    def _is_circuit_breaker_open(self, service_name: str) -> bool:
        """检查熔断器是否开启"""
        if service_name not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[service_name]
        if breaker["state"] == "open":
            # 检查是否可以尝试关闭熔断器
            if datetime.utcnow() - breaker["last_failure_time"] > timedelta(seconds=self.circuit_breaker_timeout):
                breaker["state"] = "half-open"
                breaker["failure_count"] = 0
                return False
            return True
        
        return False
    
    def _record_success(self, service_name: str):
        """记录成功请求"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure_time": None
            }
        
        breaker = self.circuit_breakers[service_name]
        if breaker["state"] == "half-open":
            breaker["state"] = "closed"
        breaker["failure_count"] = 0
    
    def _record_failure(self, service_name: str):
        """记录失败请求"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure_time": None
            }
        
        breaker = self.circuit_breakers[service_name]
        breaker["failure_count"] += 1
        breaker["last_failure_time"] = datetime.utcnow()
        
        if breaker["failure_count"] >= self.circuit_breaker_threshold:
            breaker["state"] = "open"
            logger.warning(f"服务 {service_name} 熔断器开启")
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# 全局客户端实例
_global_client: Optional[ServiceClient] = None


def get_service_client() -> ServiceClient:
    """获取全局服务客户端实例"""
    global _global_client
    if _global_client is None:
        _global_client = ServiceClient()
    return _global_client


async def close_service_client():
    """关闭全局服务客户端"""
    global _global_client
    if _global_client:
        await _global_client.close()
        _global_client = None
