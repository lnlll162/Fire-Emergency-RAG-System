import { FireIcon } from '@heroicons/react/24/outline'

export default function Loading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-red-50 to-orange-50 flex items-center justify-center">
      <div className="text-center">
        {/* 动画 Logo */}
        <div className="flex justify-center mb-8">
          <div className="relative">
            {/* 外圈旋转效果 */}
            <div className="absolute inset-0 rounded-full border-4 border-red-200 border-t-red-600 animate-spin"></div>
            
            {/* Logo */}
            <div className="relative p-8 bg-gradient-to-br from-red-500 to-orange-500 rounded-full m-2 animate-pulse">
              <FireIcon className="h-12 w-12 text-white" />
            </div>
          </div>
        </div>

        {/* 加载文字 */}
        <h2 className="text-2xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent mb-4">
          加载中...
        </h2>
        <p className="text-gray-600">正在为您准备内容</p>

        {/* 加载点动画 */}
        <div className="flex justify-center space-x-2 mt-8">
          <div className="w-3 h-3 bg-red-500 rounded-full animate-bounce"></div>
          <div className="w-3 h-3 bg-orange-500 rounded-full animate-bounce animation-delay-200"></div>
          <div className="w-3 h-3 bg-yellow-500 rounded-full animate-bounce animation-delay-400"></div>
        </div>
      </div>
    </div>
  )
}

