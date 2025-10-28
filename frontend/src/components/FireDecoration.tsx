'use client'

import { FireIcon } from '@heroicons/react/24/outline'

interface FireDecorationProps {
  variant?: 'flame' | 'spark' | 'ember'
  size?: 'sm' | 'md' | 'lg'
  animated?: boolean
  className?: string
}

export default function FireDecoration({ 
  variant = 'flame', 
  size = 'md',
  animated = true,
  className = '' 
}: FireDecorationProps) {
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-16 w-16',
    lg: 'h-32 w-32'
  }

  const variants = {
    flame: (
      <div className={`relative ${className}`}>
        {/* 外围光晕 */}
        <div className={`absolute inset-0 bg-gradient-to-t from-red-500 via-orange-500 to-yellow-500 rounded-full blur-xl opacity-40 ${animated ? 'animate-pulse' : ''}`}></div>
        
        {/* 火焰核心 */}
        <div className="relative">
          <FireIcon className={`${sizeClasses[size]} text-red-600 ${animated ? 'animate-pulse' : ''}`} />
          
          {/* 火花效果 */}
          {animated && (
            <>
              <div className="absolute -top-2 -right-2 w-2 h-2 bg-yellow-400 rounded-full animate-ping"></div>
              <div className="absolute -bottom-2 -left-2 w-1 h-1 bg-orange-400 rounded-full animate-ping animation-delay-200"></div>
            </>
          )}
        </div>
      </div>
    ),
    
    spark: (
      <div className={`relative ${className}`}>
        {/* 火花组合 */}
        <div className="relative">
          <div className={`${sizeClasses[size]} flex items-center justify-center`}>
            <div className="relative w-full h-full">
              {/* 中心火花 */}
              <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full ${animated ? 'animate-pulse' : ''}`}></div>
              
              {/* 周围火花 */}
              {animated && (
                <>
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 w-2 h-2 bg-yellow-300 rounded-full animate-ping"></div>
                  <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-2 h-2 bg-orange-300 rounded-full animate-ping animation-delay-200"></div>
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-red-300 rounded-full animate-ping animation-delay-400"></div>
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-yellow-400 rounded-full animate-ping"></div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    ),
    
    ember: (
      <div className={`relative ${className}`}>
        {/* 余烬效果 */}
        <div className={`${sizeClasses[size]} relative`}>
          {/* 发光圆圈 */}
          <div className={`absolute inset-0 bg-gradient-radial from-orange-500 via-red-500 to-transparent rounded-full ${animated ? 'animate-pulse' : ''}`}></div>
          
          {/* 中心点 */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-1/3 h-1/3 bg-yellow-400 rounded-full blur-sm"></div>
          
          {/* 飘散粒子 */}
          {animated && (
            <>
              <div className="absolute -top-4 left-1/2 w-1 h-1 bg-orange-400 rounded-full opacity-60 animate-bounce"></div>
              <div className="absolute -top-6 left-1/3 w-1 h-1 bg-red-400 rounded-full opacity-40 animate-bounce animation-delay-200"></div>
              <div className="absolute -top-8 left-2/3 w-1 h-1 bg-yellow-400 rounded-full opacity-50 animate-bounce animation-delay-400"></div>
            </>
          )}
        </div>
      </div>
    )
  }

  return variants[variant]
}

// 消防警告条纹背景
export function FireWarningStripes({ className = '' }: { className?: string }) {
  return (
    <div className={`relative overflow-hidden ${className}`}>
      <div className="absolute inset-0 bg-gradient-to-r from-red-600 via-orange-500 to-red-600 opacity-10">
        <div className="absolute inset-0" style={{
          backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(0,0,0,.05) 35px, rgba(0,0,0,.05) 70px)'
        }}></div>
      </div>
    </div>
  )
}

// 紧急闪烁指示器
export function EmergencyBlinker({ className = '' }: { className?: string }) {
  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <div className="relative">
        <div className="w-3 h-3 bg-red-600 rounded-full animate-pulse"></div>
        <div className="absolute inset-0 w-3 h-3 bg-red-600 rounded-full animate-ping"></div>
      </div>
      <span className="text-red-600 font-bold text-sm">应急</span>
    </div>
  )
}

// 消防安全徽章
export function FireSafetyBadge({ text, icon }: { text: string; icon?: React.ReactNode }) {
  return (
    <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-red-100 via-orange-100 to-yellow-100 border-2 border-red-300 rounded-full shadow-sm">
      {icon && <span className="mr-2">{icon}</span>}
      <span className="text-red-800 font-semibold text-sm">{text}</span>
    </div>
  )
}

