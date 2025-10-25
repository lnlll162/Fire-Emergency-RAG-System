'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { knowledgeGraphAPI, type KnowledgeGraphNode, type KnowledgeGraphEdge } from '@/lib/api'
import { 
  MagnifyingGlassIcon,
  ChartBarIcon,
  CircleStackIcon,
  LinkIcon,
  FireIcon,
  ExclamationTriangleIcon,
  WrenchScrewdriverIcon
} from '@heroicons/react/24/outline'

interface GraphData {
  nodes: KnowledgeGraphNode[]
  edges: KnowledgeGraphEdge[]
}

export default function KnowledgePage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] })
  const [selectedNode, setSelectedNode] = useState<KnowledgeGraphNode | null>(null)
  const [error, setError] = useState<string | null>(null)

  // 模拟数据，实际应该从API获取
  const mockData: GraphData = {
    nodes: [
      {
        id: '1',
        label: '火灾',
        type: 'event',
        properties: {
          type: '火灾事件',
          severity: 'high',
          description: '建筑物火灾'
        }
      },
      {
        id: '2',
        label: '消防栓',
        type: 'equipment',
        properties: {
          type: '消防设备',
          location: '一楼大厅',
          status: '正常'
        }
      },
      {
        id: '3',
        label: '疏散路线',
        type: 'procedure',
        properties: {
          type: '应急程序',
          priority: 'high',
          description: '紧急疏散路径'
        }
      },
      {
        id: '4',
        label: '烟雾报警器',
        type: 'equipment',
        properties: {
          type: '消防设备',
          location: '各楼层',
          status: '正常'
        }
      },
      {
        id: '5',
        label: '消防员',
        type: 'personnel',
        properties: {
          type: '人员',
          role: '救援人员',
          department: '消防队'
        }
      }
    ],
    edges: [
      {
        id: 'e1',
        source: '1',
        target: '2',
        type: 'uses',
        properties: {
          relationship: '使用',
          description: '火灾时使用消防栓'
        }
      },
      {
        id: 'e2',
        source: '1',
        target: '3',
        type: 'triggers',
        properties: {
          relationship: '触发',
          description: '火灾触发疏散程序'
        }
      },
      {
        id: 'e3',
        source: '1',
        target: '4',
        type: 'detected_by',
        properties: {
          relationship: '被检测',
          description: '烟雾报警器检测火灾'
        }
      },
      {
        id: 'e4',
        source: '5',
        target: '1',
        type: 'responds_to',
        properties: {
          relationship: '响应',
          description: '消防员响应火灾'
        }
      }
    ]
  }

  useEffect(() => {
    setGraphData(mockData)
  }, [])

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      const results = await knowledgeGraphAPI.search(searchQuery)
      // 这里应该处理搜索结果并更新图谱
      console.log('Search results:', results)
    } catch (err) {
      setError('搜索失败，请稍后重试')
      console.error('Knowledge graph search error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'event':
        return <FireIcon className="h-5 w-5 text-red-500" />
      case 'equipment':
        return <WrenchScrewdriverIcon className="h-5 w-5 text-blue-500" />
      case 'procedure':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />
      case 'personnel':
        return <CircleStackIcon className="h-5 w-5 text-green-500" />
      default:
        return <CircleStackIcon className="h-5 w-5 text-gray-500" />
    }
  }

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'event':
        return 'bg-red-100 border-red-300 text-red-800'
      case 'equipment':
        return 'bg-blue-100 border-blue-300 text-blue-800'
      case 'procedure':
        return 'bg-yellow-100 border-yellow-300 text-yellow-800'
      case 'personnel':
        return 'bg-green-100 border-green-300 text-green-800'
      default:
        return 'bg-gray-100 border-gray-300 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">消防知识图谱</h1>
          <p className="text-lg text-gray-600">探索消防知识之间的关联关系</p>
        </div>

        {/* 搜索栏 */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <ChartBarIcon className="h-6 w-6 text-blue-600 mr-2" />
              知识图谱搜索
            </CardTitle>
            <CardDescription>
              搜索消防相关的实体和关系
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Input
                placeholder="搜索消防知识实体..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button onClick={handleSearch} disabled={isLoading || !searchQuery.trim()}>
                <MagnifyingGlassIcon className="h-4 w-4 mr-2" />
                搜索
              </Button>
            </div>
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 知识图谱可视化区域 */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>知识图谱</CardTitle>
                <CardDescription>
                  节点表示实体，连线表示关系
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-96 bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <ChartBarIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">知识图谱可视化区域</p>
                    <p className="text-sm text-gray-500 mt-2">
                      这里将集成图形可视化组件
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 节点列表和详情 */}
          <div className="space-y-6">
            {/* 节点列表 */}
            <Card>
              <CardHeader>
                <CardTitle>实体列表</CardTitle>
                <CardDescription>
                  点击查看详细信息
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {graphData.nodes.map((node) => (
                    <div
                      key={node.id}
                      className={`p-3 rounded-lg border cursor-pointer hover:shadow-md transition-shadow ${getNodeColor(node.type)}`}
                      onClick={() => setSelectedNode(node)}
                    >
                      <div className="flex items-center">
                        {getNodeIcon(node.type)}
                        <span className="ml-2 font-medium">{node.label}</span>
                      </div>
                      <p className="text-sm mt-1 opacity-75">
                        {(node.properties.type as string) || node.type}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 关系列表 */}
            <Card>
              <CardHeader>
                <CardTitle>关系列表</CardTitle>
                <CardDescription>
                  实体间的关系
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {graphData.edges.map((edge) => {
                    const sourceNode = graphData.nodes.find(n => n.id === edge.source)
                    const targetNode = graphData.nodes.find(n => n.id === edge.target)
                    return (
                      <div key={edge.id} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center text-sm">
                          <span className="font-medium">{sourceNode?.label}</span>
                          <LinkIcon className="h-4 w-4 mx-2 text-gray-400" />
                          <span className="text-blue-600">{edge.properties.relationship as string}</span>
                          <LinkIcon className="h-4 w-4 mx-2 text-gray-400" />
                          <span className="font-medium">{targetNode?.label}</span>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {edge.properties.description as string}
                        </p>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* 选中节点详情 */}
        {selectedNode && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle className="flex items-center">
                {getNodeIcon(selectedNode.type)}
                <span className="ml-2">{selectedNode.label}</span>
              </CardTitle>
              <CardDescription>
                {(selectedNode.properties.type as string) || selectedNode.type}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-2">属性信息</h4>
                  <div className="space-y-2">
                    {Object.entries(selectedNode.properties).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-gray-600">{key}:</span>
                        <span className="font-medium">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">相关关系</h4>
                  <div className="space-y-2">
                    {graphData.edges
                      .filter(edge => edge.source === selectedNode.id || edge.target === selectedNode.id)
                      .map((edge) => {
                        const relatedNode = graphData.nodes.find(
                          n => n.id === (edge.source === selectedNode.id ? edge.target : edge.source)
                        )
                        return (
                          <div key={edge.id} className="text-sm">
                            <span className="font-medium">{relatedNode?.label}</span>
                            <span className="text-gray-500 mx-2">-</span>
                            <span className="text-blue-600">{edge.properties.relationship as string}</span>
                          </div>
                        )
                      })}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
