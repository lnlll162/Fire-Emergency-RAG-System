'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
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
    { text: '火灾逃生路线', icon: '🚪' },
    { text: '消防器材使用方法', icon: '🧯' },
    { text: '紧急疏散程序', icon: '🏃' },
    { text: '火灾报警流程', icon: '🚨' },
    { text: '消防栓操作指南', icon: '💧' },
    { text: '电器火灾处理', icon: '⚡' },
    { text: '高层建筑逃生', icon: '🏢' },
    { text: '化学品火灾应对', icon: '⚗️' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-red-50 to-orange-50">
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* 页面标题 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center px-4 py-2 mb-4 bg-red-100 text-red-800 rounded-full text-sm font-medium">
            <ExclamationTriangleIcon className="h-4 w-4 mr-2" />
            紧急响应系统
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            智能应急查询
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            基于RAG技术的智能消防应急响应系统，快速准确地为您提供专业指导
          </p>
        </div>

        {/* 快速查询标签 */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <SparklesIcon className="h-5 w-5 mr-2 text-red-600" />
            快速查询
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {quickQueries.map((item, index) => (
              <button
                key={index}
                onClick={() => setQuery(item.text)}
                className="group relative p-4 bg-white hover:bg-gradient-to-br hover:from-red-50 hover:to-orange-50 border-2 border-gray-200 hover:border-red-300 rounded-xl transition-all transform hover:scale-105 hover:shadow-lg text-left"
              >
                <div className="text-2xl mb-2">{item.icon}</div>
                <div className="text-sm font-medium text-gray-900 group-hover:text-red-600 transition-colors">
                  {item.text}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* 查询表单 */}
        <Card className="mb-8 shadow-xl border-2 hover:border-red-200 transition-colors">
          <CardHeader className="bg-gradient-to-r from-red-50 to-orange-50">
            <CardTitle className="flex items-center text-2xl">
              <ExclamationTriangleIcon className="h-7 w-7 text-red-600 mr-3" />
              应急查询
            </CardTitle>
            <CardDescription className="text-base">
              输入您的问题，系统将基于消防知识库为您提供准确的应急指导
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="relative">
                <Textarea
                  placeholder="请输入您的应急问题，例如：火灾发生时如何正确逃生？"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="min-h-[140px] text-lg border-2 focus:border-red-400 rounded-xl resize-none"
                  disabled={isLoading}
                />
                <div className="absolute bottom-3 right-3 text-sm text-gray-400">
                  {query.length} 字符
                </div>
              </div>
              <div className="flex justify-end">
                <Button 
                  type="submit" 
                  disabled={isLoading || !query.trim()}
                  size="lg"
                  className="bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white shadow-lg hover:shadow-xl transition-all min-w-[160px]"
                >
                  {isLoading ? (
                    <>
                      <ClockIcon className="h-5 w-5 mr-2 animate-spin" />
                      查询中...
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="h-5 w-5 mr-2" />
                      立即查询
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
          <Card className="mb-8 border-2 border-green-300 bg-gradient-to-br from-green-50 to-emerald-50 shadow-2xl animate-in fade-in duration-500">
            <CardHeader className="border-b border-green-200">
              <CardTitle className="flex items-center text-green-800 text-2xl">
                <CheckCircleIcon className="h-7 w-7 mr-3" />
                查询结果
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-6">
                <div className="bg-white p-6 rounded-xl border-2 border-green-200 shadow-md">
                  <div className="flex items-center mb-4">
                    <div className="h-1 w-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full mr-3"></div>
                    <h3 className="font-semibold text-lg text-gray-900">专业回答</h3>
                  </div>
                  <div className="markdown-content text-base">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {currentResponse.response}
                    </ReactMarkdown>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-white p-4 rounded-xl border-2 border-green-200">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">置信度</span>
                      <span className="text-lg font-bold text-green-600">{Math.round(currentResponse.confidence * 100)}%</span>
                    </div>
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-green-500 to-emerald-500 h-3 rounded-full transition-all duration-1000 ease-out" 
                        style={{ width: `${currentResponse.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="bg-white p-4 rounded-xl border-2 border-green-200">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">响应时间</span>
                      <span className="text-sm text-gray-600">{formatRelativeTime(currentResponse.timestamp)}</span>
                    </div>
                    <div className="mt-2 flex items-center text-green-600">
                      <ClockIcon className="h-5 w-5 mr-2" />
                      <span className="text-sm">快速响应</span>
                    </div>
                  </div>
                </div>

                {currentResponse.sources.length > 0 && (
                  <div className="bg-white p-6 rounded-xl border-2 border-green-200">
                    <h4 className="font-semibold text-lg text-gray-900 mb-4 flex items-center">
                      <DocumentTextIcon className="h-5 w-5 mr-2 text-green-600" />
                      参考来源
                    </h4>
                    <ul className="space-y-3">
                      {currentResponse.sources.map((source, index) => (
                        <li key={index} className="flex items-start">
                          <div className="flex-shrink-0 w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">
                            {index + 1}
                          </div>
                          <span className="text-sm text-gray-700 flex-1 leading-relaxed">{source}</span>
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
          <Card className="shadow-lg">
            <CardHeader className="bg-gradient-to-r from-gray-50 to-blue-50">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-2xl">查询历史</CardTitle>
                  <CardDescription className="text-base">最近的查询记录</CardDescription>
                </div>
                <div className="text-sm font-medium text-gray-600 bg-white px-4 py-2 rounded-full border-2 border-gray-200">
                  共 {history.length} 条记录
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="space-y-4">
                {history.slice(0, 5).map((item, index) => (
                  <div 
                    key={item.id} 
                    className="group border-2 border-gray-200 rounded-xl p-5 hover:border-blue-300 hover:bg-blue-50 transition-all cursor-pointer transform hover:scale-[1.02]"
                    onClick={() => {
                      setQuery(item.query)
                      setCurrentResponse(item.response)
                    }}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center flex-1">
                        <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">
                          {index + 1}
                        </div>
                        <h4 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">{item.query}</h4>
                      </div>
                      <span className="text-sm text-gray-500 ml-4 flex-shrink-0">{formatRelativeTime(item.timestamp)}</span>
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2 ml-11 mb-3 leading-relaxed">{item.response.response}</p>
                    <div className="flex items-center ml-11 space-x-4">
                      <div className="flex items-center text-xs text-gray-500">
                        <div className="w-16 bg-gray-200 rounded-full h-1.5 mr-2">
                          <div 
                            className="bg-blue-500 h-1.5 rounded-full" 
                            style={{ width: `${item.response.confidence * 100}%` }}
                          ></div>
                        </div>
                        <span className="font-medium">置信度 {Math.round(item.response.confidence * 100)}%</span>
                      </div>
                      {item.response.sources.length > 0 && (
                        <div className="flex items-center text-xs text-gray-500">
                          <DocumentTextIcon className="h-4 w-4 mr-1" />
                          <span>{item.response.sources.length} 个来源</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              {history.length > 5 && (
                <div className="mt-6 text-center">
                  <Button variant="outline" className="border-2 border-gray-300 hover:border-blue-400 hover:bg-blue-50">
                    查看更多历史记录 ({history.length - 5} 条)
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
