'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  QuestionMarkCircleIcon, 
  ChartBarIcon, 
  CogIcon,
  SparklesIcon,
  ShieldCheckIcon,
  ClockIcon,
  UsersIcon,
  DocumentTextIcon,
  CpuChipIcon,
  FireIcon,
  ExclamationTriangleIcon,
  ShieldExclamationIcon
} from '@heroicons/react/24/outline'
import { useState, useEffect } from 'react'
import FireSafetyTips, { SafetyChecklist } from '@/components/FireSafetyTips'

const features = [
  {
    name: '智能应急查询',
    description: '基于RAG技术的智能问答系统，提供准确的消防应急指导',
    icon: QuestionMarkCircleIcon,
    href: '/emergency',
    color: 'text-red-600'
  },
  {
    name: '知识图谱',
    description: '可视化消防知识关系网络，探索知识间的关联',
    icon: ChartBarIcon,
    href: '/knowledge',
    color: 'text-blue-600'
  },
  {
    name: '系统管理',
    description: '实时监控系统状态，管理服务配置和性能',
    icon: CogIcon,
    href: '/admin',
    color: 'text-gray-600'
  }
]

const stats = [
  { name: '知识库文档', value: '1,247' },
  { name: '应急案例', value: '892' },
  { name: '响应时间', value: '< 2秒' },
  { name: '准确率', value: '95%+' }
]

export default function Home() {
  const [mounted, setMounted] = useState(false)
  const [activeFeature, setActiveFeature] = useState(0)

  useEffect(() => {
    setMounted(true)
    const interval = setInterval(() => {
      setActiveFeature((prev) => (prev + 1) % features.length)
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 relative overflow-hidden">
      {/* 动态背景效果 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-red-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-orange-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-96 h-96 bg-yellow-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
        
        {/* 消防元素装饰 */}
        <div className="absolute top-20 right-20 opacity-5">
          <FireIcon className="h-64 w-64 text-red-600 animate-pulse" />
        </div>
        <div className="absolute bottom-20 left-20 opacity-5">
          <ShieldExclamationIcon className="h-48 w-48 text-orange-600" />
        </div>
      </div>

      {/* 主要内容 */}
      <div className="relative z-10">
        {/* 英雄区域 */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className={`text-center transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}>
            {/* 消防主题徽章 */}
            <div className="inline-flex items-center px-6 py-3 mb-8 bg-gradient-to-r from-red-100 via-orange-100 to-yellow-100 text-red-800 rounded-full text-sm font-semibold shadow-lg border-2 border-red-200 animate-pulse">
              <FireIcon className="h-5 w-5 mr-2 text-red-600" />
              智能消防应急系统 · 快速响应 · 精准指导
              <ExclamationTriangleIcon className="h-5 w-5 ml-2 text-orange-600" />
            </div>
            <h1 className="text-4xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              消防应急
              <span className="bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent"> RAG系统</span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto leading-relaxed">
              基于<span className="font-semibold text-red-600">检索增强生成</span>技术的智能消防应急响应系统<br />
              为消防人员提供准确、及时的应急指导
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/emergency">
                <Button size="lg" className="bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white shadow-lg hover:shadow-xl transition-all transform hover:scale-105">
                  <SparklesIcon className="h-5 w-5 mr-2" />
                  开始查询
                </Button>
              </Link>
              <Link href="/knowledge">
                <Button size="lg" variant="outline" className="border-2 border-red-200 hover:border-red-400 hover:bg-red-50 transition-all">
                  <ChartBarIcon className="h-5 w-5 mr-2" />
                  探索知识图谱
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* 功能特性 */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">核心功能</h2>
            <p className="text-lg text-gray-600">为消防应急提供全方位的智能支持</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card 
                key={feature.name} 
                className={`group hover:shadow-2xl transition-all duration-300 cursor-pointer border-2 hover:border-red-300 transform hover:-translate-y-2 ${
                  index === activeFeature ? 'ring-2 ring-red-400 shadow-xl' : ''
                }`}
                onMouseEnter={() => setActiveFeature(index)}
              >
                <CardHeader>
                  <div className={`inline-flex p-4 rounded-xl ${
                    index === 0 ? 'bg-red-100' :
                    index === 1 ? 'bg-blue-100' :
                    'bg-gray-100'
                  } group-hover:scale-110 transition-transform mb-4`}>
                    <feature.icon className={`h-10 w-10 ${feature.color}`} />
                  </div>
                  <CardTitle className="text-xl mb-2">{feature.name}</CardTitle>
                  <CardDescription className="text-base">{feature.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href={feature.href}>
                    <Button variant="outline" className="w-full group-hover:bg-red-600 group-hover:text-white group-hover:border-red-600 transition-colors">
                      立即体验 →
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* 统计数据 */}
        <div className="bg-white/80 backdrop-blur-sm py-20 shadow-inner">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">系统优势</h2>
              <p className="text-lg text-gray-600">基于先进技术的可靠保障</p>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <div 
                  key={stat.name} 
                  className={`text-center p-6 rounded-2xl bg-gradient-to-br ${
                    index === 0 ? 'from-red-50 to-orange-50' :
                    index === 1 ? 'from-blue-50 to-cyan-50' :
                    index === 2 ? 'from-green-50 to-emerald-50' :
                    'from-purple-50 to-pink-50'
                  } hover:shadow-xl transition-all transform hover:scale-105 cursor-pointer`}
                >
                  <div className={`text-4xl md:text-5xl font-bold mb-3 bg-gradient-to-r ${
                    index === 0 ? 'from-red-600 to-orange-600' :
                    index === 1 ? 'from-blue-600 to-cyan-600' :
                    index === 2 ? 'from-green-600 to-emerald-600' :
                    'from-purple-600 to-pink-600'
                  } bg-clip-text text-transparent`}>
                    {stat.value}
                  </div>
                  <div className="text-gray-700 font-medium">{stat.name}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 消防安全提示 */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="bg-gradient-to-r from-red-600 via-orange-600 to-red-600 rounded-3xl p-1 shadow-2xl">
            <div className="bg-white rounded-3xl p-8 md:p-12">
              <div className="flex items-center justify-center mb-6">
                <div className="p-4 bg-red-100 rounded-full animate-pulse">
                  <FireIcon className="h-12 w-12 text-red-600" />
                </div>
              </div>
              <h3 className="text-3xl font-bold text-center text-gray-900 mb-6">
                🔥 消防安全，人人有责
              </h3>
              <div className="grid md:grid-cols-3 gap-6 text-center">
                <div className="p-6 bg-red-50 rounded-2xl border-2 border-red-200 hover:shadow-lg transition-all">
                  <div className="text-4xl mb-3">🚨</div>
                  <h4 className="font-bold text-gray-900 mb-2">发现火情</h4>
                  <p className="text-gray-600 text-sm">立即拨打119报警</p>
                </div>
                <div className="p-6 bg-orange-50 rounded-2xl border-2 border-orange-200 hover:shadow-lg transition-all">
                  <div className="text-4xl mb-3">🧯</div>
                  <h4 className="font-bold text-gray-900 mb-2">初期扑救</h4>
                  <p className="text-gray-600 text-sm">正确使用消防器材</p>
                </div>
                <div className="p-6 bg-yellow-50 rounded-2xl border-2 border-yellow-200 hover:shadow-lg transition-all">
                  <div className="text-4xl mb-3">🚪</div>
                  <h4 className="font-bold text-gray-900 mb-2">紧急疏散</h4>
                  <p className="text-gray-600 text-sm">保持冷静有序撤离</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 技术特点 */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl font-bold text-gray-900 mb-8">技术特点</h2>
              <div className="space-y-8">
                <div className="flex items-start group">
                  <div className="flex-shrink-0 p-3 bg-green-100 rounded-xl group-hover:bg-green-200 transition-colors">
                    <ShieldCheckIcon className="h-8 w-8 text-green-600" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">高准确性</h3>
                    <p className="text-gray-600 leading-relaxed">基于大量消防专业知识训练，结合RAG技术实时检索最新信息，确保回答的准确性和可靠性</p>
                  </div>
                </div>
                <div className="flex items-start group">
                  <div className="flex-shrink-0 p-3 bg-blue-100 rounded-xl group-hover:bg-blue-200 transition-colors">
                    <ClockIcon className="h-8 w-8 text-blue-600" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">快速响应</h3>
                    <p className="text-gray-600 leading-relaxed">优化的向量检索和生成算法，平均响应时间&lt;2秒，确保在紧急情况下快速获得指导</p>
                  </div>
                </div>
                <div className="flex items-start group">
                  <div className="flex-shrink-0 p-3 bg-purple-100 rounded-xl group-hover:bg-purple-200 transition-colors">
                    <UsersIcon className="h-8 w-8 text-purple-600" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">易于使用</h3>
                    <p className="text-gray-600 leading-relaxed">直观的用户界面，支持自然语言查询，无需专业技术背景，降低使用门槛</p>
                  </div>
                </div>
                <div className="flex items-start group">
                  <div className="flex-shrink-0 p-3 bg-orange-100 rounded-xl group-hover:bg-orange-200 transition-colors">
                    <CpuChipIcon className="h-8 w-8 text-orange-600" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">智能学习</h3>
                    <p className="text-gray-600 leading-relaxed">持续学习和优化，通过用户反馈不断提升系统性能和准确度</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="bg-gradient-to-br from-red-100 to-orange-100 rounded-3xl p-12 text-center shadow-2xl transform hover:scale-105 transition-transform">
                <div className="text-8xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent mb-6">
                  RAG
                </div>
                <p className="text-2xl font-semibold text-gray-800 mb-3">
                  Retrieval-Augmented Generation
                </p>
                <p className="text-lg text-gray-600 mb-6">
                  检索增强生成技术
                </p>
                <div className="grid grid-cols-3 gap-4 mt-8">
                  <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4">
                    <DocumentTextIcon className="h-8 w-8 text-red-600 mx-auto mb-2" />
                    <p className="text-sm font-medium text-gray-700">文档检索</p>
                  </div>
                  <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4">
                    <ChartBarIcon className="h-8 w-8 text-orange-600 mx-auto mb-2" />
                    <p className="text-sm font-medium text-gray-700">知识图谱</p>
                  </div>
                  <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4">
                    <SparklesIcon className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
                    <p className="text-sm font-medium text-gray-700">智能生成</p>
                  </div>
                </div>
              </div>
              {/* 装饰性元素 */}
              <div className="absolute -top-6 -right-6 w-24 h-24 bg-red-400 rounded-full opacity-20 blur-2xl"></div>
              <div className="absolute -bottom-6 -left-6 w-32 h-32 bg-orange-400 rounded-full opacity-20 blur-2xl"></div>
            </div>
          </div>
        </div>

        {/* 消防器材知识卡片 */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">常见消防器材</h2>
            <p className="text-lg text-gray-600">了解消防器材，掌握正确使用方法</p>
          </div>
          
          <div className="grid md:grid-cols-4 gap-6">
            <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-red-200 hover:border-red-400 transition-all hover:scale-105 cursor-pointer">
              <div className="text-5xl text-center mb-4">🧯</div>
              <h3 className="font-bold text-gray-900 text-center mb-2">灭火器</h3>
              <p className="text-sm text-gray-600 text-center">干粉灭火器适用于各类初期火灾</p>
            </div>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-blue-200 hover:border-blue-400 transition-all hover:scale-105 cursor-pointer">
              <div className="text-5xl text-center mb-4">💧</div>
              <h3 className="font-bold text-gray-900 text-center mb-2">消防栓</h3>
              <p className="text-sm text-gray-600 text-center">室内外消防栓用于大面积灭火</p>
            </div>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-green-200 hover:border-green-400 transition-all hover:scale-105 cursor-pointer">
              <div className="text-5xl text-center mb-4">🚨</div>
              <h3 className="font-bold text-gray-900 text-center mb-2">报警器</h3>
              <p className="text-sm text-gray-600 text-center">烟感报警器及时发现火情</p>
            </div>
            
            <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-yellow-200 hover:border-yellow-400 transition-all hover:scale-105 cursor-pointer">
              <div className="text-5xl text-center mb-4">🪜</div>
              <h3 className="font-bold text-gray-900 text-center mb-2">逃生梯</h3>
              <p className="text-sm text-gray-600 text-center">应急逃生梯用于高层逃生</p>
            </div>
          </div>
        </div>

        {/* 消防安全提示组件 */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid md:grid-cols-2 gap-6">
            <FireSafetyTips />
            <SafetyChecklist />
          </div>
        </div>
      </div>
    </div>
  )
}
