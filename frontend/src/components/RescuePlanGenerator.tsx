'use client'

import { useState, useCallback, useMemo } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  FireIcon, 
  MapPinIcon, 
  ClockIcon, 
  UserGroupIcon,
  CheckCircleIcon,
  WrenchScrewdriverIcon,
  ExclamationTriangleIcon,
  SparklesIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline'

interface RescuePlan {
  scenario: string
  location: string
  severity: string
  personnel_count: string
}

interface RescueStep {
  step_number: number
  title: string
  description: string
  estimated_time: number
  equipment: string[]
  warnings: string[]
}

interface RescueResponse {
  rescue_plan: {
    steps: RescueStep[]
    total_time: number
    risk_level: string
  }
}

export default function RescuePlanGenerator() {
  const [formData, setFormData] = useState<RescuePlan>({
    scenario: '',
    location: '',
    severity: '中等',
    personnel_count: ''
  })
  const [isLoading, setIsLoading] = useState(false)
  const [rescuePlan, setRescuePlan] = useState<RescueResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  // 使用 useCallback 优化表单提交
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8003/rescue-plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        throw new Error('生成救援方案失败')
      }

      const data = await response.json()
      setRescuePlan(data)
    } catch (err) {
      setError('生成失败，请稍后重试')
      console.error('Rescue plan error:', err)
    } finally {
      setIsLoading(false)
    }
  }, [formData])

  const getRiskLevelColor = useMemo(() => (risk: string) => {
    if (risk.includes('高')) return 'text-red-600'
    if (risk.includes('中')) return 'text-orange-600'
    return 'text-green-600'
  }, [])

  return (
    <div className="space-y-8">
      {/* 输入表单 */}
      <Card className="shadow-2xl border-2 border-red-300 bg-gradient-to-br from-white to-red-50">
        <CardHeader className="bg-gradient-to-r from-red-100 to-orange-100 border-b-2 border-red-200">
          <CardTitle className="flex items-center text-2xl">
            <div className="p-3 bg-red-200 rounded-xl mr-3">
              <FireIcon className="h-7 w-7 text-red-700" />
            </div>
            智能救援方案生成器
          </CardTitle>
          <CardDescription className="text-base">
            基于AI的个性化救援方案，提供详细的步骤、设备和安全提示
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* 火灾场景 */}
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-700 flex items-center">
                  <FireIcon className="h-4 w-4 mr-2 text-red-600" />
                  火灾场景 *
                </label>
                <Input
                  placeholder="例如：办公楼二楼电器火灾"
                  value={formData.scenario}
                  onChange={(e) => setFormData({ ...formData, scenario: e.target.value })}
                  className="border-2 focus:border-red-400 h-12 text-base"
                  required
                />
              </div>

              {/* 地点 */}
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-700 flex items-center">
                  <MapPinIcon className="h-4 w-4 mr-2 text-blue-600" />
                  具体地点 *
                </label>
                <Input
                  placeholder="例如：XX科技园A座"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="border-2 focus:border-red-400 h-12 text-base"
                  required
                />
              </div>

              {/* 严重程度 */}
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-700 flex items-center">
                  <ExclamationTriangleIcon className="h-4 w-4 mr-2 text-orange-600" />
                  严重程度 *
                </label>
                <select
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  className="w-full h-12 px-4 border-2 border-gray-300 rounded-lg focus:border-red-400 focus:outline-none text-base bg-white"
                  required
                >
                  <option value="低">低 - 小型火情</option>
                  <option value="中等">中等 - 可控火势</option>
                  <option value="高">高 - 快速蔓延</option>
                  <option value="极高">极高 - 大规模火灾</option>
                </select>
              </div>

              {/* 人员数量 */}
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-700 flex items-center">
                  <UserGroupIcon className="h-4 w-4 mr-2 text-green-600" />
                  现场人员数量 *
                </label>
                <Input
                  placeholder="例如：50人"
                  value={formData.personnel_count}
                  onChange={(e) => setFormData({ ...formData, personnel_count: e.target.value })}
                  className="border-2 focus:border-red-400 h-12 text-base"
                  required
                />
              </div>
            </div>

            <div className="flex justify-center pt-4">
              <Button 
                type="submit" 
                disabled={isLoading}
                size="lg"
                className="bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white shadow-lg hover:shadow-xl transition-all transform hover:scale-105 min-w-[200px] h-14 text-lg"
              >
                {isLoading ? (
                  <>
                    <ClockIcon className="h-6 w-6 mr-2 animate-spin" />
                    生成中...
                  </>
                ) : (
                  <>
                    <SparklesIcon className="h-6 w-6 mr-2" />
                    生成救援方案
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* 错误提示 */}
      {error && (
        <Card className="border-red-300 bg-red-50 shadow-lg">
          <CardContent className="pt-6">
            <div className="flex items-center text-red-800">
              <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
              {error}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 救援方案展示 */}
      {rescuePlan && (
        <div className="space-y-6 animate-in fade-in duration-500">
          {/* 方案概览 */}
          <Card className="shadow-2xl border-2 border-green-300 bg-gradient-to-br from-white to-green-50">
            <CardHeader className="bg-gradient-to-r from-green-100 to-emerald-100 border-b-2 border-green-200">
              <CardTitle className="flex items-center text-2xl text-green-800">
                <CheckCircleIcon className="h-8 w-8 mr-3" />
                救援方案已生成
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-5 rounded-xl border-2 border-green-200 shadow-md">
                  <div className="flex items-center mb-2">
                    <ClockIcon className="h-5 w-5 text-green-600 mr-2" />
                    <span className="text-sm font-medium text-gray-600">总计用时</span>
                  </div>
                  <p className="text-3xl font-bold text-green-600">
                    {rescuePlan.rescue_plan.total_time} 分钟
                  </p>
                </div>
                <div className="bg-white p-5 rounded-xl border-2 border-green-200 shadow-md">
                  <div className="flex items-center mb-2">
                    <ExclamationTriangleIcon className="h-5 w-5 text-orange-600 mr-2" />
                    <span className="text-sm font-medium text-gray-600">风险等级</span>
                  </div>
                  <p className={`text-2xl font-bold ${getRiskLevelColor(rescuePlan.rescue_plan.risk_level)}`}>
                    {rescuePlan.rescue_plan.risk_level}
                  </p>
                </div>
                <div className="bg-white p-5 rounded-xl border-2 border-green-200 shadow-md">
                  <div className="flex items-center mb-2">
                    <CheckCircleIcon className="h-5 w-5 text-blue-600 mr-2" />
                    <span className="text-sm font-medium text-gray-600">救援步骤</span>
                  </div>
                  <p className="text-3xl font-bold text-blue-600">
                    {rescuePlan.rescue_plan.steps.length} 步
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 详细步骤 */}
          <div className="space-y-6">
            {rescuePlan.rescue_plan.steps.map((step) => (
              <Card 
                key={step.step_number} 
                className="shadow-xl border-2 hover:border-blue-400 transition-all transform hover:scale-[1.01] bg-gradient-to-br from-white to-blue-50"
              >
                <CardHeader className="bg-gradient-to-r from-blue-50 to-cyan-50 border-b-2 border-blue-200">
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center text-xl">
                      <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 text-white rounded-xl font-bold text-lg mr-4 shadow-lg">
                        {step.step_number}
                      </div>
                      <div>
                        <div className="text-xl font-bold text-gray-900">{step.title}</div>
                        <div className="text-sm text-gray-600 mt-1 flex items-center">
                          <ClockIcon className="h-4 w-4 mr-1" />
                          预计 {step.estimated_time} 分钟
                        </div>
                      </div>
                    </CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="pt-6 space-y-6">
                  {/* 描述 */}
                  <div className="bg-white p-5 rounded-xl border-2 border-blue-200 shadow-md">
                    <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                      <div className="w-1 h-5 bg-gradient-to-b from-blue-500 to-cyan-500 rounded-full mr-2"></div>
                      操作描述
                    </h4>
                    <p className="text-gray-700 leading-relaxed">{step.description}</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* 所需设备 */}
                    {step.equipment.length > 0 && (
                      <div className="bg-white p-5 rounded-xl border-2 border-green-200 shadow-md">
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                          <WrenchScrewdriverIcon className="h-5 w-5 text-green-600 mr-2" />
                          所需设备
                        </h4>
                        <ul className="space-y-2">
                          {step.equipment.map((item, i) => (
                            <li key={i} className="flex items-start text-sm">
                              <ChevronRightIcon className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                              <span className="text-gray-700">{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* 注意事项 */}
                    {step.warnings.length > 0 && (
                      <div className="bg-white p-5 rounded-xl border-2 border-red-200 shadow-md">
                        <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                          <ExclamationTriangleIcon className="h-5 w-5 text-red-600 mr-2" />
                          注意事项
                        </h4>
                        <ul className="space-y-2">
                          {step.warnings.map((warning, i) => (
                            <li key={i} className="flex items-start text-sm">
                              <span className="text-red-500 mr-2 flex-shrink-0 font-bold">⚠</span>
                              <span className="text-gray-700">{warning}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

