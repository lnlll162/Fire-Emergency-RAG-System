'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { GraphVisualization } from '@/components/ui/graph-visualization'
import { knowledgeGraphAPI, type KnowledgeGraphNode, type KnowledgeGraphEdge } from '@/lib/api'
import { 
  MagnifyingGlassIcon,
  ChartBarIcon,
  CircleStackIcon,
  LinkIcon,
  FireIcon,
  ExclamationTriangleIcon,
  WrenchScrewdriverIcon,
  SparklesIcon
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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* 页面标题 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center px-4 py-2 mb-4 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
            <ChartBarIcon className="h-4 w-4 mr-2" />
            知识网络可视化
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            消防知识图谱
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            探索消防知识之间的关联关系，直观展示实体和关系网络
          </p>
        </div>

        {/* 搜索栏 */}
        <Card className="mb-8 shadow-xl border-2 hover:border-blue-200 transition-colors">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50">
            <CardTitle className="flex items-center text-2xl">
              <MagnifyingGlassIcon className="h-7 w-7 text-blue-600 mr-3" />
              知识图谱搜索
            </CardTitle>
            <CardDescription className="text-base">
              搜索消防相关的实体和关系，探索知识网络
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="flex gap-4">
              <Input
                placeholder="搜索消防知识实体，例如：火灾、消防栓、疏散..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="text-lg border-2 focus:border-blue-400 rounded-xl"
              />
              <Button 
                onClick={handleSearch} 
                disabled={isLoading || !searchQuery.trim()}
                size="lg"
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all min-w-[120px]"
              >
                <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
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
            <Card className="shadow-2xl border-2 border-blue-200">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50 border-b-2 border-blue-100">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-2xl flex items-center">
                      <SparklesIcon className="h-6 w-6 text-blue-600 mr-2" />
                      知识图谱可视化
                    </CardTitle>
                    <CardDescription className="text-base mt-2">
                      节点表示实体，箭头表示关系。点击节点查看详情
                    </CardDescription>
                  </div>
                  <div className="text-sm text-gray-600 bg-white px-4 py-2 rounded-full border-2 border-gray-200">
                    {graphData.nodes.length} 个节点
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="h-[600px] relative">
                  <GraphVisualization
                    nodes={graphData.nodes}
                    edges={graphData.edges}
                    selectedNodeId={selectedNode?.id}
                    onNodeClick={setSelectedNode}
                  />
                  {/* 图例 */}
                  <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm rounded-xl p-4 shadow-lg border-2 border-gray-200">
                    <h4 className="font-semibold text-sm text-gray-900 mb-3">节点类型</h4>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <div className="w-4 h-4 rounded-full bg-red-500 mr-2"></div>
                        <span className="text-xs text-gray-700">事件</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-4 h-4 rounded-full bg-blue-500 mr-2"></div>
                        <span className="text-xs text-gray-700">设备</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-4 h-4 rounded-full bg-yellow-500 mr-2"></div>
                        <span className="text-xs text-gray-700">程序</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-4 h-4 rounded-full bg-green-500 mr-2"></div>
                        <span className="text-xs text-gray-700">人员</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 节点列表和详情 */}
          <div className="space-y-6">
            {/* 节点列表 */}
            <Card className="shadow-xl border-2 border-gray-200">
              <CardHeader className="bg-gradient-to-r from-gray-50 to-blue-50">
                <CardTitle className="text-xl">实体列表</CardTitle>
                <CardDescription className="text-base">
                  点击查看详细信息
                </CardDescription>
              </CardHeader>
              <CardContent className="max-h-[400px] overflow-y-auto">
                <div className="space-y-3">
                  {graphData.nodes.map((node) => (
                    <div
                      key={node.id}
                      className={`p-4 rounded-xl border-2 cursor-pointer hover:shadow-lg transition-all transform hover:scale-105 ${
                        getNodeColor(node.type)
                      } ${
                        selectedNode?.id === node.id ? 'ring-2 ring-blue-400 shadow-lg' : ''
                      }`}
                      onClick={() => setSelectedNode(node)}
                    >
                      <div className="flex items-center">
                        {getNodeIcon(node.type)}
                        <span className="ml-2 font-semibold">{node.label}</span>
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
            <Card className="shadow-xl border-2 border-gray-200">
              <CardHeader className="bg-gradient-to-r from-gray-50 to-purple-50">
                <CardTitle className="text-xl flex items-center">
                  <LinkIcon className="h-5 w-5 text-purple-600 mr-2" />
                  关系列表
                </CardTitle>
                <CardDescription className="text-base">
                  实体间的关系
                </CardDescription>
              </CardHeader>
              <CardContent className="max-h-[300px] overflow-y-auto">
                <div className="space-y-3">
                  {graphData.edges.map((edge) => {
                    const sourceNode = graphData.nodes.find(n => n.id === edge.source)
                    const targetNode = graphData.nodes.find(n => n.id === edge.target)
                    return (
                      <div key={edge.id} className="p-4 bg-gradient-to-br from-gray-50 to-blue-50 rounded-xl border-2 border-gray-200 hover:border-purple-300 transition-all">
                        <div className="flex items-center text-sm flex-wrap gap-2">
                          <span className="font-semibold text-gray-900 bg-white px-2 py-1 rounded">{sourceNode?.label}</span>
                          <span className="text-purple-600 font-medium">→ {edge.properties.relationship as string} →</span>
                          <span className="font-semibold text-gray-900 bg-white px-2 py-1 rounded">{targetNode?.label}</span>
                        </div>
                        <p className="text-xs text-gray-600 mt-2 italic">
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
          <Card className="mt-8 shadow-2xl border-2 border-blue-300 bg-gradient-to-br from-white to-blue-50 animate-in fade-in duration-500">
            <CardHeader className="border-b-2 border-blue-200">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center text-2xl">
                  <div className={`p-3 rounded-xl mr-3 ${
                    selectedNode.type === 'event' ? 'bg-red-100' :
                    selectedNode.type === 'equipment' ? 'bg-blue-100' :
                    selectedNode.type === 'procedure' ? 'bg-yellow-100' :
                    'bg-green-100'
                  }`}>
                    {getNodeIcon(selectedNode.type)}
                  </div>
                  <span>{selectedNode.label}</span>
                </CardTitle>
                <span className={`px-4 py-2 rounded-full text-sm font-medium ${getNodeColor(selectedNode.type)}`}>
                  {(selectedNode.properties.type as string) || selectedNode.type}
                </span>
              </div>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h4 className="font-bold text-lg mb-4 flex items-center">
                    <div className="h-1 w-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mr-2"></div>
                    属性信息
                  </h4>
                  <div className="space-y-3 bg-white p-4 rounded-xl border-2 border-blue-200">
                    {Object.entries(selectedNode.properties).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center pb-2 border-b border-gray-200 last:border-0">
                        <span className="text-gray-600 font-medium">{key}</span>
                        <span className="font-semibold text-gray-900">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-bold text-lg mb-4 flex items-center">
                    <div className="h-1 w-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full mr-2"></div>
                    相关关系
                  </h4>
                  <div className="space-y-3">
                    {graphData.edges
                      .filter(edge => edge.source === selectedNode.id || edge.target === selectedNode.id)
                      .map((edge) => {
                        const relatedNode = graphData.nodes.find(
                          n => n.id === (edge.source === selectedNode.id ? edge.target : edge.source)
                        )
                        return (
                          <div key={edge.id} className="bg-white p-4 rounded-xl border-2 border-purple-200 hover:border-purple-400 transition-colors">
                            <div className="flex items-center justify-between">
                              <span className="font-semibold text-gray-900">{relatedNode?.label}</span>
                              <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded-full">
                                {edge.properties.relationship as string}
                              </span>
                            </div>
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
