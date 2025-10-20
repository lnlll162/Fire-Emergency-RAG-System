'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { emergencyAPI, type EmergencyResponse } from '@/lib/api'
import { formatRelativeTime } from '@/lib/utils'
import { 
  ExclamationTriangleIcon, 
  ClockIcon, 
  CheckCircleIcon,
  DocumentTextIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'

interface QueryHistory {
  id: string
  query: string
  response: EmergencyResponse
  timestamp: string
}

export default function EmergencyPage() {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentResponse, setCurrentResponse] = useState<EmergencyResponse | null>(null)
  const [history, setHistory] = useState<QueryHistory[]>([])
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await emergencyAPI.query({ query })
      setCurrentResponse(response)
      
      // 添加到历史记录
      const newHistoryItem: QueryHistory = {
        id: Date.now().toString(),
        query,
        response,
        timestamp: new Date().toISOString()
      }
      setHistory(prev => [newHistoryItem, ...prev])
      setQuery('')
    } catch (err) {
      setError('查询失败，请稍后重试')
      console.error('Emergency query error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const quickQueries = [
    '火灾逃生路线',
    '消防器材使用方法',
    '紧急疏散程序',
    '火灾报警流程',
    '消防栓操作指南'
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">应急查询系统</h1>
          <p className="text-lg text-gray-600">基于RAG技术的智能消防应急响应</p>
        </div>

        {/* 查询表单 */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <ExclamationTriangleIcon className="h-6 w-6 text-red-600 mr-2" />
              应急查询
            </CardTitle>
            <CardDescription>
              输入您的问题，系统将基于消防知识库为您提供准确的应急指导
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Textarea
                placeholder="请输入您的应急问题，例如：火灾发生时如何正确逃生？"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="min-h-[120px]"
                disabled={isLoading}
              />
              <div className="flex justify-between items-center">
                <div className="flex flex-wrap gap-2">
                  {quickQueries.map((quickQuery) => (
                    <Button
                      key={quickQuery}
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setQuery(quickQuery)}
                      disabled={isLoading}
                    >
                      {quickQuery}
                    </Button>
                  ))}
                </div>
                <Button type="submit" disabled={isLoading || !query.trim()}>
                  {isLoading ? (
                    <>
                      <ClockIcon className="h-4 w-4 mr-2 animate-spin" />
                      查询中...
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="h-4 w-4 mr-2" />
                      查询
                    </>
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* 错误提示 */}
        {error && (
          <Card className="mb-8 border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center text-red-800">
                <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
                {error}
              </div>
            </CardContent>
          </Card>
        )}

        {/* 当前查询结果 */}
        {currentResponse && (
          <Card className="mb-8 border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="flex items-center text-green-800">
                <CheckCircleIcon className="h-6 w-6 mr-2" />
                查询结果
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="bg-white p-4 rounded-lg border">
                  <h3 className="font-semibold text-gray-900 mb-2">回答：</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{currentResponse.response}</p>
                </div>
                
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <div className="flex items-center">
                    <span>置信度: </span>
                    <div className="ml-2 w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full" 
                        style={{ width: `${currentResponse.confidence * 100}%` }}
                      ></div>
                    </div>
                    <span className="ml-2">{Math.round(currentResponse.confidence * 100)}%</span>
                  </div>
                  <span>{formatRelativeTime(currentResponse.timestamp)}</span>
                </div>

                {currentResponse.sources.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                      <DocumentTextIcon className="h-4 w-4 mr-1" />
                      参考来源：
                    </h4>
                    <ul className="space-y-1">
                      {currentResponse.sources.map((source, index) => (
                        <li key={index} className="text-sm text-gray-600 bg-white p-2 rounded border">
                          {source}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* 查询历史 */}
        {history.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>查询历史</CardTitle>
              <CardDescription>最近的查询记录</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {history.slice(0, 5).map((item) => (
                  <div key={item.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-gray-900">{item.query}</h4>
                      <span className="text-sm text-gray-500">{formatRelativeTime(item.timestamp)}</span>
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2">{item.response.response}</p>
                    <div className="flex items-center mt-2 text-xs text-gray-500">
                      <span>置信度: {Math.round(item.response.confidence * 100)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
