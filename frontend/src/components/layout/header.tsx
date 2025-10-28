'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { 
  FireIcon, 
  Bars3Icon, 
  XMarkIcon,
  HomeIcon,
  ChartBarIcon,
  CogIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline'

const navigation = [
  { name: '首页', href: '/', icon: HomeIcon },
  { name: '应急查询', href: '/emergency', icon: QuestionMarkCircleIcon },
  { name: '知识图谱', href: '/knowledge', icon: ChartBarIcon },
  { name: '管理后台', href: '/admin', icon: CogIcon },
]

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const pathname = usePathname()

  const isActive = (href: string) => {
    if (href === '/') {
      return pathname === '/'
    }
    return pathname.startsWith(href)
  }

  return (
    <header className="bg-white/95 backdrop-blur-sm shadow-sm border-b sticky top-0 z-40">
      <nav className="mx-auto flex max-w-7xl items-center justify-between p-6 lg:px-8" aria-label="Global">
        <div className="flex lg:flex-1">
          <Link href="/" className="-m-1.5 p-1.5 flex items-center group">
            {/* 火焰Logo动画效果 */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-red-500 to-orange-500 rounded-lg blur-md opacity-50 group-hover:opacity-75 transition-opacity"></div>
              <div className="relative p-1 bg-gradient-to-br from-red-500 to-orange-500 rounded-lg group-hover:scale-110 transition-transform">
                <FireIcon className="h-6 w-6 text-white animate-pulse" />
              </div>
            </div>
            <span className="ml-2 text-xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent">
              消防应急RAG系统
            </span>
            {/* 应急标识 */}
            <span className="ml-2 px-2 py-0.5 bg-red-100 text-red-600 text-xs font-bold rounded">
              应急
            </span>
          </Link>
        </div>
        
        <div className="flex lg:hidden">
          <button
            type="button"
            className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-700 hover:bg-gray-100 transition-colors"
            onClick={() => setMobileMenuOpen(true)}
            aria-label="打开主菜单"
          >
            <Bars3Icon className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
        
        <div className="hidden lg:flex lg:gap-x-2">
          {navigation.map((item) => {
            const active = isActive(item.href)
            const Icon = item.icon
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                  active
                    ? 'bg-gradient-to-r from-red-500 to-orange-500 text-white shadow-md'
                    : 'text-gray-700 hover:bg-red-50 hover:text-red-600'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {item.name}
              </Link>
            )
          })}
        </div>
        
        <div className="hidden lg:flex lg:flex-1 lg:justify-end">
          <Button 
            variant="outline" 
            size="sm"
            className="border-2 border-gray-300 hover:border-red-500 hover:text-red-600 transition-all"
          >
            登录
          </Button>
        </div>
      </nav>
      
      {/* 移动端菜单 */}
      {mobileMenuOpen && (
        <div className="lg:hidden">
          <div 
            className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200" 
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-white px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-gray-900/10 shadow-2xl animate-in slide-in-from-right duration-300">
            <div className="flex items-center justify-between">
              <Link href="/" className="-m-1.5 p-1.5 flex items-center" onClick={() => setMobileMenuOpen(false)}>
                <div className="p-1 bg-gradient-to-br from-red-500 to-orange-500 rounded-lg">
                  <FireIcon className="h-6 w-6 text-white" />
                </div>
                <span className="ml-2 text-xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent">
                  消防应急RAG系统
                </span>
              </Link>
              <button
                type="button"
                className="-m-2.5 rounded-md p-2.5 text-gray-700 hover:bg-gray-100 transition-colors"
                onClick={() => setMobileMenuOpen(false)}
                aria-label="关闭菜单"
              >
                <XMarkIcon className="h-6 w-6" aria-hidden="true" />
              </button>
            </div>
            <div className="mt-6 flow-root">
              <div className="-my-6 divide-y divide-gray-200">
                <div className="space-y-2 py-6">
                  {navigation.map((item) => {
                    const active = isActive(item.href)
                    const Icon = item.icon
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        className={`-mx-3 flex items-center rounded-lg px-3 py-3 text-base font-semibold leading-7 transition-all ${
                          active
                            ? 'bg-gradient-to-r from-red-500 to-orange-500 text-white shadow-md'
                            : 'text-gray-900 hover:bg-red-50 hover:text-red-600'
                        }`}
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        <Icon className={`h-5 w-5 mr-3 ${active ? 'text-white' : 'text-gray-400'}`} />
                        {item.name}
                      </Link>
                    )
                  })}
                </div>
                <div className="py-6">
                  <Button 
                    variant="outline" 
                    className="w-full border-2 border-gray-300 hover:border-red-500 hover:text-red-600 transition-all"
                  >
                    登录
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
