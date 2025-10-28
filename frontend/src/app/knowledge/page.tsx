'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { GraphVisualization } from '@/components/ui/graph-visualization'
import { knowledgeGraphAPI, type KnowledgeGraphNode, type KnowledgeGraphEdge } from '@/lib/api'
import { 
  MagnifyingGlassIcon,
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {/* 页面标题 */}
        <div className="text-center mb-8 sm:mb-12">
          <div className="inline-flex items-center px-5 py-2 mb-4 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-full text-sm font-semibold shadow-lg hover:shadow-xl transition-shadow">
            <SparklesIcon className="h-4 w-4 mr-2 animate-pulse" />
            知识图谱可视化
          </div>
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent mb-4">
            消防知识图谱
          </h1>
          <p className="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            节点表示实体，箭头表示关系。点击节点查看详情
          </p>
        </div>

        {/* 搜索栏 */}
        <Card className="mb-8 shadow-2xl border-0 overflow-hidden backdrop-blur-sm bg-white/80">
          <CardHeader className="bg-gradient-to-r from-blue-500/10 via-indigo-500/10 to-purple-500/10 border-b border-gray-200/50">
            <CardTitle className="flex items-center text-2xl font-bold">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-lg mr-3 shadow-md">
                <MagnifyingGlassIcon className="h-6 w-6 text-white" />
              </div>
              知识图谱搜索
            </CardTitle>
            <CardDescription className="text-base mt-1">
              搜索消防相关的实体和关系，探索知识网络
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-6 pb-6">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 relative group">
                <Input
                  placeholder="搜索消防知识实体，例如：火灾、消防栓、疏散..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="text-base h-12 border-2 border-gray-300 focus:border-indigo-500 rounded-xl shadow-sm group-hover:border-indigo-400 transition-colors pl-4"
                />
              </div>
              <Button 
                onClick={handleSearch} 
                disabled={isLoading || !searchQuery.trim()}
                size="lg"
                className="h-12 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 rounded-xl font-semibold min-w-[140px]"
              >
                <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
                {isLoading ? '搜索中...' : '搜索'}
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8 items-start">
          {/* 知识图谱可视化区域 */}
          <div className="lg:col-span-2">
            <Card className="shadow-2xl border-0 overflow-hidden bg-white/90 backdrop-blur-sm h-full">
              <CardHeader className="bg-gradient-to-r from-blue-500/10 via-indigo-500/10 to-purple-500/10 border-b border-gray-200/50">
                <div className="flex items-center justify-between flex-wrap gap-3">
                  <div>
                    <CardTitle className="text-2xl flex items-center font-bold">
                      <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg mr-3 shadow-md">
                        <SparklesIcon className="h-5 w-5 text-white" />
                      </div>
                      知识图谱可视化
                    </CardTitle>
                    <CardDescription className="text-base mt-2 ml-14">
                      节点表示实体，箭头表示关系。点击节点查看详情
                    </CardDescription>
                  </div>
                  <div className="text-sm font-semibold text-indigo-700 bg-indigo-50 px-5 py-2.5 rounded-full border-2 border-indigo-200 shadow-sm">
                    <span className="text-lg mr-1">{graphData.nodes.length}</span>
                    个节点
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="h-[600px] relative bg-gradient-to-br from-gray-50 to-blue-50/30">
                  <GraphVisualization
                    nodes={graphData.nodes}
                    edges={graphData.edges}
                    selectedNodeId={selectedNode?.id}
                    onNodeClick={setSelectedNode}
                  />
                  {/* 图例 */}
                  <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-md rounded-2xl p-5 shadow-2xl border border-gray-200">
                    <h4 className="font-bold text-base text-gray-900 mb-4 flex items-center">
                      <div className="h-1 w-6 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full mr-2"></div>
                      节点类型
                    </h4>
                    <div className="space-y-3">
                      <div className="flex items-center group cursor-default hover:bg-red-50 px-2 py-1.5 rounded-lg transition-colors">
                        <div className="w-5 h-5 rounded-full bg-gradient-to-br from-red-400 to-red-600 mr-3 shadow-md group-hover:scale-110 transition-transform"></div>
                        <span className="text-sm font-medium text-gray-700">事件</span>
                      </div>
                      <div className="flex items-center group cursor-default hover:bg-blue-50 px-2 py-1.5 rounded-lg transition-colors">
                        <div className="w-5 h-5 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 mr-3 shadow-md group-hover:scale-110 transition-transform"></div>
                        <span className="text-sm font-medium text-gray-700">设备</span>
                      </div>
                      <div className="flex items-center group cursor-default hover:bg-yellow-50 px-2 py-1.5 rounded-lg transition-colors">
                        <div className="w-5 h-5 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-600 mr-3 shadow-md group-hover:scale-110 transition-transform"></div>
                        <span className="text-sm font-medium text-gray-700">程序</span>
                      </div>
                      <div className="flex items-center group cursor-default hover:bg-green-50 px-2 py-1.5 rounded-lg transition-colors">
                        <div className="w-5 h-5 rounded-full bg-gradient-to-br from-green-400 to-green-600 mr-3 shadow-md group-hover:scale-110 transition-transform"></div>
                        <span className="text-sm font-medium text-gray-700">人员</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 节点列表和详情 */}
          <div className="space-y-5 lg:space-y-6">
            {/* 节点列表 */}
            <Card className="shadow-2xl border-0 overflow-hidden bg-white/90 backdrop-blur-sm">
              <CardHeader className="bg-gradient-to-r from-gray-500/10 to-blue-500/10 border-b border-gray-200/50">
                <CardTitle className="text-xl font-bold flex items-center">
                  <div className="h-1 w-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full mr-3"></div>
                  实体列表
                </CardTitle>
                <CardDescription className="text-sm mt-1">
                  点击查看详细信息
                </CardDescription>
              </CardHeader>
              <CardContent className="overflow-y-auto p-4 h-[280px]">
                <div className="space-y-2.5">
                  {graphData.nodes.map((node) => (
                    <div
                      key={node.id}
                      className={`p-4 rounded-xl border-2 cursor-pointer hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02] ${
                        getNodeColor(node.type)
                      } ${
                        selectedNode?.id === node.id ? 'ring-4 ring-indigo-400 shadow-xl scale-[1.02]' : ''
                      }`}
                      onClick={() => setSelectedNode(node)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center flex-1">
                          <div className={`p-2 rounded-lg mr-3 ${
                            node.type === 'event' ? 'bg-red-200' :
                            node.type === 'equipment' ? 'bg-blue-200' :
                            node.type === 'procedure' ? 'bg-yellow-200' :
                            'bg-green-200'
                          }`}>
                            {getNodeIcon(node.type)}
                          </div>
                          <div>
                            <span className="font-bold text-base">{node.label}</span>
                            <p className="text-xs mt-0.5 opacity-80">
                              {(node.properties.type as string) || node.type}
                            </p>
                          </div>
                        </div>
                        {selectedNode?.id === node.id && (
                          <div className="ml-2 w-2 h-2 rounded-full bg-indigo-600 animate-pulse"></div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* 关系列表 */}
            <Card className="shadow-2xl border-0 overflow-hidden bg-white/90 backdrop-blur-sm">
              <CardHeader className="bg-gradient-to-r from-purple-500/10 to-pink-500/10 border-b border-gray-200/50">
                <CardTitle className="text-xl font-bold flex items-center">
                  <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg mr-3 shadow-md">
                    <LinkIcon className="h-5 w-5 text-white" />
                  </div>
                  关系列表
                </CardTitle>
                <CardDescription className="text-sm mt-1">
                  实体间的关系
                </CardDescription>
              </CardHeader>
              <CardContent className="overflow-y-auto p-4 h-[250px]">
                <div className="space-y-3">
                  {graphData.edges.map((edge) => {
                    const sourceNode = graphData.nodes.find(n => n.id === edge.source)
                    const targetNode = graphData.nodes.find(n => n.id === edge.target)
                    return (
                      <div key={edge.id} className="group p-4 bg-gradient-to-br from-purple-50/50 via-pink-50/50 to-blue-50/50 rounded-xl border-2 border-purple-200/60 hover:border-purple-400 hover:shadow-lg transition-all duration-300">
                        <div className="flex items-center text-sm flex-wrap gap-2 mb-2">
                          <span className="font-bold text-gray-900 bg-white px-3 py-1.5 rounded-lg shadow-sm border border-gray-200 group-hover:border-purple-300 transition-colors">{sourceNode?.label}</span>
                          <div className="flex items-center gap-1 text-purple-600 font-semibold">
                            <span>→</span>
                            <span className="text-xs px-2 py-1 bg-purple-100 rounded-md">{edge.properties.relationship as string}</span>
                            <span>→</span>
                          </div>
                          <span className="font-bold text-gray-900 bg-white px-3 py-1.5 rounded-lg shadow-sm border border-gray-200 group-hover:border-purple-300 transition-colors">{targetNode?.label}</span>
                        </div>
                        <p className="text-xs text-gray-600 pl-1 leading-relaxed">
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
          <Card className="mt-6 lg:mt-8 shadow-2xl border-0 bg-gradient-to-br from-white via-blue-50/30 to-purple-50/30 backdrop-blur-sm animate-in fade-in slide-in-from-bottom-4 duration-500">
            <CardHeader className="border-b border-gray-200/50 bg-gradient-to-r from-blue-500/5 via-indigo-500/5 to-purple-500/5">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <CardTitle className="flex items-center text-2xl font-bold">
                  <div className={`p-3 rounded-xl mr-4 shadow-lg ${
                    selectedNode.type === 'event' ? 'bg-gradient-to-br from-red-400 to-red-600' :
                    selectedNode.type === 'equipment' ? 'bg-gradient-to-br from-blue-400 to-blue-600' :
                    selectedNode.type === 'procedure' ? 'bg-gradient-to-br from-yellow-400 to-yellow-600' :
                    'bg-gradient-to-br from-green-400 to-green-600'
                  }`}>
                    <div className="text-white">
                      {getNodeIcon(selectedNode.type)}
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-900">{selectedNode.label}</span>
                    <p className="text-sm text-gray-500 font-normal mt-1">节点详细信息</p>
                  </div>
                </CardTitle>
                <span className={`px-5 py-2.5 rounded-xl text-sm font-bold shadow-md ${getNodeColor(selectedNode.type)}`}>
                  {(selectedNode.properties.type as string) || selectedNode.type}
                </span>
              </div>
            </CardHeader>
            <CardContent className="pt-8 pb-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
                <div className="space-y-4">
                  <h4 className="font-bold text-xl mb-5 flex items-center">
                    <div className="h-1.5 w-10 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 rounded-full mr-3"></div>
                    属性信息
                  </h4>
                  <div className="space-y-2 bg-white/80 backdrop-blur-sm p-6 rounded-2xl border-2 border-blue-200/50 shadow-lg">
                    {Object.entries(selectedNode.properties).map(([key, value]) => (
                      <div key={key} className="group flex justify-between items-center py-3 px-3 rounded-lg hover:bg-blue-50 transition-colors border-b border-gray-200/70 last:border-0">
                        <span className="text-gray-600 font-semibold text-sm">{key}</span>
                        <span className="font-bold text-gray-900 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent group-hover:from-purple-600 group-hover:to-pink-600 transition-all">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="space-y-4">
                  <h4 className="font-bold text-xl mb-5 flex items-center">
                    <div className="h-1.5 w-10 bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 rounded-full mr-3"></div>
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
                          <div key={edge.id} className="group bg-white/80 backdrop-blur-sm p-5 rounded-2xl border-2 border-purple-200/50 hover:border-purple-400 hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02]">
                            <div className="flex items-center justify-between mb-2">
                              <span className="font-bold text-gray-900 text-base">{relatedNode?.label}</span>
                              <div className="w-2 h-2 rounded-full bg-purple-500 group-hover:animate-ping"></div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs px-3 py-1.5 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 rounded-lg font-semibold border border-purple-200">
                                {edge.properties.relationship as string}
                              </span>
                              <span className="text-xs text-gray-500 flex-1">{edge.properties.description as string}</span>
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
