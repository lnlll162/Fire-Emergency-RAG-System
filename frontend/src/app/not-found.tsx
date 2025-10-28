import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { 
  HomeIcon, 
  ArrowLeftIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-red-50 to-orange-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        {/* 动画背景 */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-20 w-64 h-64 bg-red-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
          <div className="absolute top-40 right-20 w-64 h-64 bg-orange-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
        </div>

        <div className="relative z-10">
          {/* 错误图标 */}
          <div className="flex justify-center mb-8">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-red-500 to-orange-500 rounded-full blur-xl opacity-50 animate-pulse"></div>
              <div className="relative p-6 bg-white rounded-full shadow-2xl border-4 border-red-200">
                <ExclamationTriangleIcon className="h-16 w-16 text-red-600" />
              </div>
            </div>
          </div>

          {/* 404 文字 */}
          <h1 className="text-9xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent mb-4">
            404
          </h1>
          
          {/* 描述 */}
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            页面未找到
          </h2>
          <p className="text-lg text-gray-600 mb-8 max-w-md mx-auto">
            抱歉，您访问的页面不存在或已被移除。请检查URL是否正确，或返回首页继续浏览。
          </p>

          {/* 操作按钮 */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/">
              <Button 
                size="lg"
                className="bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
              >
                <HomeIcon className="h-5 w-5 mr-2" />
                返回首页
              </Button>
            </Link>
            <Button 
              size="lg"
              variant="outline"
              onClick={() => window.history.back()}
              className="border-2 border-gray-300 hover:border-red-400 hover:bg-red-50 transition-all"
            >
              <ArrowLeftIcon className="h-5 w-5 mr-2" />
              返回上一页
            </Button>
          </div>

          {/* 快速链接 */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-600 mb-4">或者访问这些页面：</p>
            <div className="flex flex-wrap justify-center gap-3">
              <Link 
                href="/emergency"
                className="px-4 py-2 bg-white border-2 border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:border-red-400 hover:text-red-600 transition-all"
              >
                应急查询
              </Link>
              <Link 
                href="/knowledge"
                className="px-4 py-2 bg-white border-2 border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:border-blue-400 hover:text-blue-600 transition-all"
              >
                知识图谱
              </Link>
              <Link 
                href="/admin"
                className="px-4 py-2 bg-white border-2 border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:border-purple-400 hover:text-purple-600 transition-all"
              >
                管理后台
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

