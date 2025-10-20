'use client'

import { useState } from 'react'
import Link from 'next/link'
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

  return (
    <header className="bg-white shadow-sm border-b">
      <nav className="mx-auto flex max-w-7xl items-center justify-between p-6 lg:px-8" aria-label="Global">
        <div className="flex lg:flex-1">
          <Link href="/" className="-m-1.5 p-1.5 flex items-center">
            <FireIcon className="h-8 w-8 text-red-600" />
            <span className="ml-2 text-xl font-bold text-gray-900">消防应急RAG系统</span>
          </Link>
        </div>
        
        <div className="flex lg:hidden">
          <button
            type="button"
            className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-700"
            onClick={() => setMobileMenuOpen(true)}
          >
            <span className="sr-only">打开主菜单</span>
            <Bars3Icon className="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
        
        <div className="hidden lg:flex lg:gap-x-12">
          {navigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className="text-sm font-semibold leading-6 text-gray-900 hover:text-red-600 transition-colors"
            >
              {item.name}
            </Link>
          ))}
        </div>
        
        <div className="hidden lg:flex lg:flex-1 lg:justify-end">
          <Button variant="outline" size="sm">
            登录
          </Button>
        </div>
      </nav>
      
      {/* 移动端菜单 */}
      {mobileMenuOpen && (
        <div className="lg:hidden">
          <div className="fixed inset-0 z-50" />
          <div className="fixed inset-y-0 right-0 z-50 w-full overflow-y-auto bg-white px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-gray-900/10">
            <div className="flex items-center justify-between">
              <Link href="/" className="-m-1.5 p-1.5 flex items-center">
                <FireIcon className="h-8 w-8 text-red-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">消防应急RAG系统</span>
              </Link>
              <button
                type="button"
                className="-m-2.5 rounded-md p-2.5 text-gray-700"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span className="sr-only">关闭菜单</span>
                <XMarkIcon className="h-6 w-6" aria-hidden="true" />
              </button>
            </div>
            <div className="mt-6 flow-root">
              <div className="-my-6 divide-y divide-gray-500/10">
                <div className="space-y-2 py-6">
                  {navigation.map((item) => (
                    <Link
                      key={item.name}
                      href={item.href}
                      className="-mx-3 flex items-center rounded-lg px-3 py-2 text-base font-semibold leading-7 text-gray-900 hover:bg-gray-50"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      <item.icon className="h-5 w-5 mr-3 text-gray-400" />
                      {item.name}
                    </Link>
                  ))}
                </div>
                <div className="py-6">
                  <Button variant="outline" className="w-full">
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
