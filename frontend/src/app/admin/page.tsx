'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { systemAPI, type SystemStatus } from '@/lib/api'
import { formatRelativeTime } from '@/lib/utils'
import { 
  CogIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  ServerIcon,
  CircleStackIcon,
  ChartBarIcon,
  ClockIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline'

interface ServiceStatus {
  name: string
  status: 'running' | 'stopped' | 'error'
  uptime: string
  lastCheck: string
  port: number
}

const mockServices: ServiceStatus[] = [
  {
    name: 'RAG服务',
    status: 'running',
    uptime: '2天 14小时',
    lastCheck: '2024-01-09T10:30:00Z',
    port: 8001
  },
  {
    name: '应急服务',
    status: 'running',
    uptime: '2天 14小时',
    lastCheck: '2024-01-09T10:30:00Z',
    port: 8002
  },
  {
    name: '知识图谱服务',
    status: 'running',
    uptime: '2天 14小时',
    lastCheck: '2024-01-09T10:30:00Z',
    port: 8003
  },
  {
    name: 'Ollama服务',
    status: 'running',
    uptime: '2天 14小时',
    lastCheck: '2024-01-09T10:30:00Z',
    port: 8004
  },
  {
    name: '缓存服务',
    status: 'running',
    uptime: '2天 14小时',
    lastCheck: '2024-01-09T10:30:00Z',
    port: 8005
  }
]

export default function AdminPage() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  useEffect(() => {
    loadSystemStatus()
  }, [])

  const loadSystemStatus = async () => {
    setIsLoading(true)
    try {
      const status = await systemAPI.getStatus()
      setSystemStatus(status)
    } catch (error) {
      console.error('Failed to load system status:', error)
      // 使用模拟数据
      setSystemStatus({
        services: {},
        databases: { postgres: true, neo4j: true },
        overall_status: 'healthy'
      })
    } finally {
      setIsLoading(false)
      setLastRefresh(new Date())
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'stopped':
        return <XCircleIcon className="h-5 w-5 text-red-500" />
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'stopped':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'error':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* 页面标题 */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">系统管理后台</h1>
            <p className="text-lg text-gray-600">监控和管理消防应急RAG系统</p>
          </div>
          <Button onClick={loadSystemStatus} disabled={isLoading}>
            <ArrowPathIcon className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            刷新状态
          </Button>
        </div>

        {/* 系统概览 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <ServerIcon className="h-8 w-8 text-blue-500" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">运行服务</p>
                  <p className="text-2xl font-bold text-gray-900">5/5</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <CircleStackIcon className="h-8 w-8 text-green-500" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">数据库状态</p>
                  <p className="text-2xl font-bold text-green-600">正常</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <ChartBarIcon className="h-8 w-8 text-purple-500" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">知识图谱</p>
                  <p className="text-2xl font-bold text-purple-600">已加载</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <ClockIcon className="h-8 w-8 text-orange-500" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">最后更新</p>
                  <p className="text-sm font-bold text-gray-900">{formatRelativeTime(lastRefresh)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 服务状态详情 */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <CogIcon className="h-6 w-6 text-gray-600 mr-2" />
              服务状态监控
            </CardTitle>
            <CardDescription>
              各微服务的运行状态和性能指标
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockServices.map((service) => (
                <div key={service.name} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(service.status)}
                    <div>
                      <h3 className="font-medium text-gray-900">{service.name}</h3>
                      <p className="text-sm text-gray-500">端口: {service.port}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-6">
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">运行时间</p>
                      <p className="text-sm text-gray-500">{service.uptime}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">最后检查</p>
                      <p className="text-sm text-gray-500">{formatRelativeTime(service.lastCheck)}</p>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(service.status)}`}>
                      {service.status === 'running' ? '运行中' : 
                       service.status === 'stopped' ? '已停止' : '错误'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 数据库状态 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <CircleStackIcon className="h-6 w-6 text-green-600 mr-2" />
                PostgreSQL 数据库
              </CardTitle>
              <CardDescription>
                用户数据和系统配置存储
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">连接状态</span>
                  <div className="flex items-center">
                    <CheckCircleIcon className="h-4 w-4 text-green-500 mr-1" />
                    <span className="text-sm font-medium text-green-600">已连接</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">数据库大小</span>
                  <span className="text-sm font-medium">2.3 MB</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">表数量</span>
                  <span className="text-sm font-medium">8</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">最后备份</span>
                  <span className="text-sm font-medium">2小时前</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <ChartBarIcon className="h-6 w-6 text-purple-600 mr-2" />
                Neo4j 图数据库
              </CardTitle>
              <CardDescription>
                知识图谱和关系数据存储
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">连接状态</span>
                  <div className="flex items-center">
                    <CheckCircleIcon className="h-4 w-4 text-green-500 mr-1" />
                    <span className="text-sm font-medium text-green-600">已连接</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">节点数量</span>
                  <span className="text-sm font-medium">1,247</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">关系数量</span>
                  <span className="text-sm font-medium">2,891</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">索引状态</span>
                  <span className="text-sm font-medium text-green-600">已优化</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 系统操作 */}
        <Card>
          <CardHeader>
            <CardTitle>系统操作</CardTitle>
            <CardDescription>
              执行系统维护和管理操作
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button variant="outline" className="h-20 flex-col">
                <CircleStackIcon className="h-6 w-6 mb-2" />
                备份数据库
              </Button>
              <Button variant="outline" className="h-20 flex-col">
                <ChartBarIcon className="h-6 w-6 mb-2" />
                重建索引
              </Button>
              <Button variant="outline" className="h-20 flex-col">
                <ArrowPathIcon className="h-6 w-6 mb-2" />
                重启服务
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
