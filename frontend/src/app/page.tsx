import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  FireIcon, 
  QuestionMarkCircleIcon, 
  ChartBarIcon, 
  CogIcon,
  SparklesIcon,
  ShieldCheckIcon,
  ClockIcon,
  UsersIcon
} from '@heroicons/react/24/outline'

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
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50">
      {/* 主要内容 */}
        {/* 英雄区域 */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              消防应急
              <span className="text-red-600"> RAG系统</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              基于先进RAG技术的智能消防应急响应系统，为消防人员提供准确、及时的应急指导
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="bg-red-600 hover:bg-red-700">
                <SparklesIcon className="h-5 w-5 mr-2" />
                开始查询
              </Button>
              <Button size="lg" variant="outline">
                了解更多
              </Button>
            </div>
          </div>
        </div>

        {/* 功能特性 */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">核心功能</h2>
            <p className="text-lg text-gray-600">为消防应急提供全方位的智能支持</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature) => (
              <Card key={feature.name} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <feature.icon className={`h-12 w-12 ${feature.color} mb-4`} />
                  <CardTitle>{feature.name}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href={feature.href}>
                    <Button variant="outline" className="w-full">
                      立即体验
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* 统计数据 */}
        <div className="bg-white py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">系统优势</h2>
              <p className="text-lg text-gray-600">基于先进技术的可靠保障</p>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {stats.map((stat) => (
                <div key={stat.name} className="text-center">
                  <div className="text-3xl font-bold text-red-600 mb-2">{stat.value}</div>
                  <div className="text-gray-600">{stat.name}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 技术特点 */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">技术特点</h2>
              <div className="space-y-6">
                <div className="flex items-start">
                  <ShieldCheckIcon className="h-6 w-6 text-green-600 mt-1 mr-3" />
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">高准确性</h3>
                    <p className="text-gray-600">基于大量消防专业知识训练，确保回答的准确性和可靠性</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <ClockIcon className="h-6 w-6 text-blue-600 mt-1 mr-3" />
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">快速响应</h3>
                    <p className="text-gray-600">优化的检索和生成算法，确保在紧急情况下快速获得指导</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <UsersIcon className="h-6 w-6 text-purple-600 mt-1 mr-3" />
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">易于使用</h3>
                    <p className="text-gray-600">直观的用户界面，支持自然语言查询，降低使用门槛</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-gray-100 rounded-lg p-8 text-center">
              <div className="text-6xl font-bold text-gray-400 mb-4">RAG</div>
              <p className="text-lg text-gray-600">
                Retrieval-Augmented Generation
              </p>
              <p className="text-sm text-gray-500 mt-2">
                检索增强生成技术
              </p>
            </div>
          </div>
        </div>
    </div>
  )
}
