'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FireIcon, LightBulbIcon } from '@heroicons/react/24/outline'

const safetyTips = [
  {
    id: 1,
    emoji: '🚨',
    title: '发现火灾',
    tip: '发现火情立即拨打119，说清地点、火势、是否有人员被困'
  },
  {
    id: 2,
    emoji: '🧯',
    title: '初期扑救',
    tip: '使用灭火器时记住：提、拔、瞄、压四步法，对准火焰根部喷射'
  },
  {
    id: 3,
    emoji: '🚪',
    title: '安全逃生',
    tip: '火灾逃生时低姿前进，用湿毛巾捂住口鼻，切勿乘坐电梯'
  },
  {
    id: 4,
    emoji: '⚡',
    title: '电器火灾',
    tip: '电器着火先断电，不能用水扑灭，应使用干粉灭火器'
  },
  {
    id: 5,
    emoji: '🏢',
    title: '高层逃生',
    tip: '高层建筑火灾不可盲目跳楼，应向避难层或楼顶平台转移'
  },
  {
    id: 6,
    emoji: '🚭',
    title: '预防为主',
    tip: '不在床上吸烟，离家前检查电器、燃气，定期清理阳台杂物'
  },
  {
    id: 7,
    emoji: '💧',
    title: '消防栓使用',
    tip: '打开消防栓门，取出水带和水枪，连接后打开阀门喷水灭火'
  },
  {
    id: 8,
    emoji: '🆘',
    title: '被困求救',
    tip: '被困时关闭房门，用湿毛巾堵门缝，在窗口挥舞鲜艳物品求救'
  }
]

export default function FireSafetyTips() {
  const [currentTipIndex, setCurrentTipIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTipIndex((prev) => (prev + 1) % safetyTips.length)
    }, 8000) // 每8秒切换一次

    return () => clearInterval(interval)
  }, [])

  const currentTip = safetyTips[currentTipIndex]

  return (
    <Card className="border-2 border-orange-200 bg-gradient-to-br from-orange-50 to-red-50 shadow-lg">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center text-lg">
          <div className="p-2 bg-orange-100 rounded-lg mr-3">
            <LightBulbIcon className="h-5 w-5 text-orange-600" />
          </div>
          <span className="bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent">
            消防安全提示
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* 当前提示 */}
        <div className="mb-4 p-4 bg-white rounded-xl border-2 border-orange-200 transition-all duration-500 hover:shadow-md">
          <div className="flex items-start">
            <div className="text-4xl mr-3 animate-bounce">{currentTip.emoji}</div>
            <div className="flex-1">
              <h4 className="font-bold text-gray-900 mb-2 flex items-center">
                {currentTip.title}
                <span className="ml-2 px-2 py-0.5 bg-red-100 text-red-600 text-xs rounded">重要</span>
              </h4>
              <p className="text-gray-700 text-sm leading-relaxed">{currentTip.tip}</p>
            </div>
          </div>
        </div>

        {/* 进度指示器 */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs text-gray-500">提示 {currentTipIndex + 1}/{safetyTips.length}</span>
          <div className="flex space-x-1">
            {safetyTips.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentTipIndex(index)}
                className={`h-1.5 rounded-full transition-all duration-300 ${
                  index === currentTipIndex 
                    ? 'w-8 bg-gradient-to-r from-red-500 to-orange-500' 
                    : 'w-1.5 bg-gray-300 hover:bg-gray-400'
                }`}
                aria-label={`切换到提示 ${index + 1}`}
              />
            ))}
          </div>
        </div>

        {/* 紧急电话 */}
        <div className="mt-4 p-3 bg-gradient-to-r from-red-600 to-orange-600 rounded-xl text-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <FireIcon className="h-6 w-6 mr-2 animate-pulse" />
              <div>
                <div className="text-xs opacity-90">火警电话</div>
                <div className="text-2xl font-bold">119</div>
              </div>
            </div>
            <div className="text-right text-xs opacity-90">
              24小时<br />随时拨打
            </div>
          </div>
        </div>

        {/* 其他紧急电话 */}
        <div className="mt-3 grid grid-cols-2 gap-2 text-center text-xs">
          <div className="p-2 bg-white rounded-lg border border-gray-200">
            <div className="font-bold text-gray-900">110</div>
            <div className="text-gray-600">匪警</div>
          </div>
          <div className="p-2 bg-white rounded-lg border border-gray-200">
            <div className="font-bold text-gray-900">120</div>
            <div className="text-gray-600">急救</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// 快速安全检查清单
export function SafetyChecklist() {
  const [checkedItems, setCheckedItems] = useState<Set<number>>(new Set())

  const checklistItems = [
    { id: 1, text: '检查消防器材是否完好' },
    { id: 2, text: '确认安全出口畅通' },
    { id: 3, text: '电器使用后断电' },
    { id: 4, text: '燃气阀门关闭' },
    { id: 5, text: '楼道杂物清理' }
  ]

  const toggleItem = (id: number) => {
    const newChecked = new Set(checkedItems)
    if (newChecked.has(id)) {
      newChecked.delete(id)
    } else {
      newChecked.add(id)
    }
    setCheckedItems(newChecked)
  }

  return (
    <Card className="border-2 border-green-200 bg-gradient-to-br from-green-50 to-emerald-50">
      <CardHeader>
        <CardTitle className="text-lg flex items-center">
          <span className="text-2xl mr-2">✅</span>
          每日安全检查
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {checklistItems.map((item) => (
            <label
              key={item.id}
              className="flex items-center p-3 bg-white rounded-lg border-2 border-gray-200 hover:border-green-300 cursor-pointer transition-all"
            >
              <input
                type="checkbox"
                checked={checkedItems.has(item.id)}
                onChange={() => toggleItem(item.id)}
                className="w-5 h-5 text-green-600 rounded focus:ring-2 focus:ring-green-500"
              />
              <span className={`ml-3 ${checkedItems.has(item.id) ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                {item.text}
              </span>
            </label>
          ))}
        </div>
        
        <div className="mt-4 text-center">
          <div className="text-sm text-gray-600">
            已完成 <span className="font-bold text-green-600">{checkedItems.size}</span>/{checklistItems.length}
          </div>
          {checkedItems.size === checklistItems.length && (
            <div className="mt-2 text-green-600 font-semibold animate-pulse">
              🎉 今日检查已完成！
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

