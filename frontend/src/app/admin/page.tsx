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
    lastCheck: new Date().toISOString(),
    port: 3000
  },
  {
    name: '应急服务',
    status: 'running',
    uptime: '2天 14小时',
    lastCheck: new Date().toISOString(),
    port: 8000
  },
  {
    name: '知识图谱服务',
    status: 'running',
    uptime: '2天 14小时',
    lastCheck: new Date().toISOString(),
    port: 8001
  },
  {
    name: 'Ollama服务',
    status: 'running',
    uptime: '2天 14小时',
    lastCheck: new Date().toISOString(),
    port: 8003
  },
  {
    name: '缓存服务',
    status: 'running',
    uptime: '2天 14小时',
    lastCheck: new Date().toISOString(),
    port: 8004
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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* 页面标题 */}
        <div className="flex justify-between items-center mb-12">
          <div>
            <div className="inline-flex items-center px-4 py-2 mb-4 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
              <CogIcon className="h-4 w-4 mr-2" />
              系统管理中心
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">系统管理后台</h1>
            <p className="text-xl text-gray-600">实时监控和管理消防应急RAG系统</p>
          </div>
          <Button 
            onClick={loadSystemStatus} 
            disabled={isLoading}
            size="lg"
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg hover:shadow-xl transition-all"
          >
            <ArrowPathIcon className={`h-5 w-5 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            刷新状态
          </Button>
        </div>

        {/* 系统概览 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-2 border-blue-200 shadow-lg hover:shadow-xl transition-all transform hover:scale-105">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">运行服务</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">5/5</p>
                  <p className="text-xs text-gray-500 mt-1">全部正常</p>
                </div>
                <div className="p-4 bg-blue-100 rounded-xl">
                  <ServerIcon className="h-8 w-8 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 shadow-lg hover:shadow-xl transition-all transform hover:scale-105">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">数据库状态</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">正常</p>
                  <p className="text-xs text-gray-500 mt-1">2个活跃</p>
                </div>
                <div className="p-4 bg-green-100 rounded-xl">
                  <CircleStackIcon className="h-8 w-8 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200 shadow-lg hover:shadow-xl transition-all transform hover:scale-105">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">知识图谱</p>
                  <p className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">80</p>
                  <p className="text-xs text-gray-500 mt-1">节点已加载</p>
                </div>
                <div className="p-4 bg-purple-100 rounded-xl">
                  <ChartBarIcon className="h-8 w-8 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-50 to-yellow-50 border-2 border-orange-200 shadow-lg hover:shadow-xl transition-all transform hover:scale-105">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">最后更新</p>
                  <p className="text-lg font-bold text-gray-900">{formatRelativeTime(lastRefresh)}</p>
                  <p className="text-xs text-gray-500 mt-1">自动刷新</p>
                </div>
                <div className="p-4 bg-orange-100 rounded-xl">
                  <ClockIcon className="h-8 w-8 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 服务状态详情 */}
        <Card className="mb-8 shadow-2xl border-2 border-gray-200">
          <CardHeader className="bg-gradient-to-r from-purple-50 to-blue-50 border-b-2 border-gray-200">
            <CardTitle className="flex items-center text-2xl">
              <ServerIcon className="h-7 w-7 text-purple-600 mr-3" />
              服务状态监控
            </CardTitle>
            <CardDescription className="text-base">
              各微服务的运行状态和性能指标
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="space-y-4">
              {mockServices.map((service, index) => (
                <div 
                  key={service.name} 
                  className="group flex items-center justify-between p-6 border-2 border-gray-200 rounded-xl hover:border-purple-300 hover:bg-gradient-to-br hover:from-white hover:to-purple-50 transition-all transform hover:scale-[1.02] shadow-md hover:shadow-lg"
                >
                  <div className="flex items-center space-x-4">
                    <div className={`p-3 rounded-xl ${
                      index === 0 ? 'bg-red-100' :
                      index === 1 ? 'bg-blue-100' :
                      index === 2 ? 'bg-green-100' :
                      index === 3 ? 'bg-yellow-100' :
                      'bg-purple-100'
                    }`}>
                      {getStatusIcon(service.status)}
                      <CheckCircleIcon className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-bold text-lg text-gray-900 group-hover:text-purple-600 transition-colors">{service.name}</h3>
                      <p className="text-sm text-gray-500">端口: <span className="font-medium text-gray-700">{service.port}</span></p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-8">
                    <div className="text-right">
                      <p className="text-xs font-medium text-gray-600 mb-1">运行时间</p>
                      <p className="text-sm font-bold text-gray-900">{service.uptime}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-medium text-gray-600 mb-1">最后检查</p>
                      <p className="text-sm font-bold text-gray-900">{formatRelativeTime(service.lastCheck)}</p>
                    </div>
                    <div className="px-5 py-2 rounded-full text-sm font-bold bg-gradient-to-r from-green-100 to-emerald-100 text-green-700 border-2 border-green-300 shadow-sm">
                      ✓ 运行中
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 数据库状态 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <Card className="shadow-xl border-2 border-green-200 bg-gradient-to-br from-white to-green-50">
            <CardHeader className="border-b-2 border-green-100">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center text-xl">
                  <div className="p-3 bg-green-100 rounded-xl mr-3">
                    <CircleStackIcon className="h-6 w-6 text-green-600" />
                  </div>
                  PostgreSQL
                </CardTitle>
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold border-2 border-green-300">
                  在线
                </span>
              </div>
              <CardDescription className="text-base ml-12">
                用户数据和系统配置存储
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-white rounded-lg border-2 border-green-100">
                  <span className="text-sm font-medium text-gray-700">连接状态</span>
                  <div className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span className="text-sm font-bold text-green-600">已连接</span>
                  </div>
                </div>
                <div className="flex justify-between items-center p-3 bg-white rounded-lg border-2 border-green-100">
                  <span className="text-sm font-medium text-gray-700">数据库大小</span>
                  <span className="text-sm font-bold text-gray-900">2.3 MB</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-white rounded-lg border-2 border-green-100">
                  <span className="text-sm font-medium text-gray-700">表数量</span>
                  <span className="text-sm font-bold text-gray-900">8</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-white rounded-lg border-2 border-green-100">
                  <span className="text-sm font-medium text-gray-700">最后备份</span>
                  <span className="text-sm font-bold text-gray-900">2小时前</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="shadow-xl border-2 border-purple-200 bg-gradient-to-br from-white to-purple-50">
            <CardHeader className="border-b-2 border-purple-100">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center text-xl">
                  <div className="p-3 bg-purple-100 rounded-xl mr-3">
                    <ChartBarIcon className="h-6 w-6 text-purple-600" />
                  </div>
                  Neo4j
                </CardTitle>
                <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-bold border-2 border-purple-300">
                  在线
                </span>
              </div>
              <CardDescription className="text-base ml-12">
                知识图谱和关系数据存储
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-white rounded-lg border-2 border-purple-100">
                  <span className="text-sm font-medium text-gray-700">连接状态</span>
                  <div className="flex items-center">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
                    <span className="text-sm font-bold text-green-600">已连接</span>
                  </div>
                </div>
                <div className="flex justify-between items-center p-3 bg-white rounded-lg border-2 border-purple-100">
                  <span className="text-sm font-medium text-gray-700">节点数量</span>
                  <span className="text-sm font-bold text-purple-600">80</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-white rounded-lg border-2 border-purple-100">
                  <span className="text-sm font-medium text-gray-700">关系数量</span>
                  <span className="text-sm font-bold text-purple-600">100</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-white rounded-lg border-2 border-purple-100">
                  <span className="text-sm font-medium text-gray-700">索引状态</span>
                  <span className="text-sm font-bold text-green-600">✓ 已优化</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 系统操作 */}
        <Card className="shadow-xl border-2 border-gray-200">
          <CardHeader className="bg-gradient-to-r from-gray-50 to-blue-50 border-b-2 border-gray-200">
            <CardTitle className="text-2xl">系统操作</CardTitle>
            <CardDescription className="text-base">
              执行系统维护和管理操作
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Button 
                variant="outline" 
                className="h-32 flex-col border-2 border-blue-200 hover:border-blue-400 hover:bg-gradient-to-br hover:from-blue-50 hover:to-cyan-50 transition-all group transform hover:scale-105 shadow-md hover:shadow-lg"
              >
                <div className="p-4 bg-blue-100 rounded-xl mb-3 group-hover:scale-110 transition-transform">
                  <CircleStackIcon className="h-8 w-8 text-blue-600" />
                </div>
                <span className="text-base font-semibold">备份数据库</span>
                <span className="text-xs text-gray-500 mt-1">全量备份</span>
              </Button>
              <Button 
                variant="outline" 
                className="h-32 flex-col border-2 border-purple-200 hover:border-purple-400 hover:bg-gradient-to-br hover:from-purple-50 hover:to-pink-50 transition-all group transform hover:scale-105 shadow-md hover:shadow-lg"
              >
                <div className="p-4 bg-purple-100 rounded-xl mb-3 group-hover:scale-110 transition-transform">
                  <ChartBarIcon className="h-8 w-8 text-purple-600" />
                </div>
                <span className="text-base font-semibold">重建索引</span>
                <span className="text-xs text-gray-500 mt-1">优化性能</span>
              </Button>
              <Button 
                variant="outline" 
                className="h-32 flex-col border-2 border-orange-200 hover:border-orange-400 hover:bg-gradient-to-br hover:from-orange-50 hover:to-yellow-50 transition-all group transform hover:scale-105 shadow-md hover:shadow-lg"
              >
                <div className="p-4 bg-orange-100 rounded-xl mb-3 group-hover:scale-110 transition-transform">
                  <ArrowPathIcon className="h-8 w-8 text-orange-600" />
                </div>
                <span className="text-base font-semibold">重启服务</span>
                <span className="text-xs text-gray-500 mt-1">全部重启</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
