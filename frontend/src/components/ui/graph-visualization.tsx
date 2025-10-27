'use client'

import { useEffect, useRef, useState } from 'react'
import { KnowledgeGraphNode, KnowledgeGraphEdge } from '@/lib/api'

interface GraphVisualizationProps {
  nodes: KnowledgeGraphNode[]
  edges: KnowledgeGraphEdge[]
  selectedNodeId?: string
  onNodeClick?: (node: KnowledgeGraphNode) => void
}

interface CanvasNode extends KnowledgeGraphNode {
  x: number
  y: number
  vx: number
  vy: number
  radius: number
}

export function GraphVisualization({ nodes, edges, selectedNodeId, onNodeClick }: GraphVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [canvasNodes, setCanvasNodes] = useState<CanvasNode[]>([])
  const [hoveredNode, setHoveredNode] = useState<string | null>(null)
  const animationRef = useRef<number>()

  useEffect(() => {
    if (!canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // 设置画布大小
    const updateCanvasSize = () => {
      const rect = canvas.getBoundingClientRect()
      canvas.width = rect.width
      canvas.height = rect.height
    }
    updateCanvasSize()
    window.addEventListener('resize', updateCanvasSize)

    // 初始化节点位置
    const initNodes: CanvasNode[] = nodes.map((node, index) => {
      const angle = (Math.PI * 2 * index) / nodes.length
      const radius = Math.min(canvas.width, canvas.height) * 0.3
      return {
        ...node,
        x: canvas.width / 2 + Math.cos(angle) * radius,
        y: canvas.height / 2 + Math.sin(angle) * radius,
        vx: 0,
        vy: 0,
        radius: 30
      }
    })
    setCanvasNodes(initNodes)

    return () => {
      window.removeEventListener('resize', updateCanvasSize)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [nodes])

  useEffect(() => {
    if (!canvasRef.current || canvasNodes.length === 0) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // 绘制边
      edges.forEach(edge => {
        const sourceNode = canvasNodes.find(n => n.id === edge.source)
        const targetNode = canvasNodes.find(n => n.id === edge.target)
        
        if (sourceNode && targetNode) {
          ctx.beginPath()
          ctx.moveTo(sourceNode.x, sourceNode.y)
          ctx.lineTo(targetNode.x, targetNode.y)
          ctx.strokeStyle = selectedNodeId === sourceNode.id || selectedNodeId === targetNode.id 
            ? 'rgba(239, 68, 68, 0.6)' 
            : 'rgba(156, 163, 175, 0.4)'
          ctx.lineWidth = selectedNodeId === sourceNode.id || selectedNodeId === targetNode.id ? 3 : 2
          ctx.stroke()

          // 绘制箭头
          const angle = Math.atan2(targetNode.y - sourceNode.y, targetNode.x - sourceNode.x)
          const arrowLength = 10
          const arrowX = targetNode.x - Math.cos(angle) * (targetNode.radius + 5)
          const arrowY = targetNode.y - Math.sin(angle) * (targetNode.radius + 5)
          
          ctx.beginPath()
          ctx.moveTo(arrowX, arrowY)
          ctx.lineTo(
            arrowX - arrowLength * Math.cos(angle - Math.PI / 6),
            arrowY - arrowLength * Math.sin(angle - Math.PI / 6)
          )
          ctx.lineTo(
            arrowX - arrowLength * Math.cos(angle + Math.PI / 6),
            arrowY - arrowLength * Math.sin(angle + Math.PI / 6)
          )
          ctx.closePath()
          ctx.fillStyle = selectedNodeId === sourceNode.id || selectedNodeId === targetNode.id 
            ? 'rgba(239, 68, 68, 0.6)' 
            : 'rgba(156, 163, 175, 0.4)'
          ctx.fill()
        }
      })

      // 绘制节点
      canvasNodes.forEach(node => {
        const isSelected = node.id === selectedNodeId
        const isHovered = node.id === hoveredNode

        // 节点颜色
        let color = '#9CA3AF' // gray
        if (node.type === 'event') color = '#EF4444' // red
        if (node.type === 'equipment') color = '#3B82F6' // blue
        if (node.type === 'procedure') color = '#F59E0B' // yellow
        if (node.type === 'personnel') color = '#10B981' // green

        // 绘制节点阴影
        if (isSelected || isHovered) {
          ctx.beginPath()
          ctx.arc(node.x, node.y, node.radius + 8, 0, Math.PI * 2)
          ctx.fillStyle = `${color}20`
          ctx.fill()
        }

        // 绘制节点
        ctx.beginPath()
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2)
        ctx.fillStyle = isSelected ? color : `${color}CC`
        ctx.fill()
        ctx.strokeStyle = '#fff'
        ctx.lineWidth = isSelected || isHovered ? 4 : 2
        ctx.stroke()

        // 绘制节点标签
        ctx.fillStyle = '#fff'
        ctx.font = `bold ${isSelected || isHovered ? '14px' : '12px'} sans-serif`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(node.label, node.x, node.y)

        // 绘制类型标签
        ctx.font = '10px sans-serif'
        ctx.fillStyle = '#374151'
        ctx.fillText(node.type, node.x, node.y + node.radius + 15)
      })

      animationRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [canvasNodes, edges, selectedNodeId, hoveredNode])

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    const clickedNode = canvasNodes.find(node => {
      const dx = x - node.x
      const dy = y - node.y
      return Math.sqrt(dx * dx + dy * dy) <= node.radius
    })

    if (clickedNode && onNodeClick) {
      onNodeClick(clickedNode)
    }
  }

  const handleCanvasMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    const hoveredNode = canvasNodes.find(node => {
      const dx = x - node.x
      const dy = y - node.y
      return Math.sqrt(dx * dx + dy * dy) <= node.radius
    })

    setHoveredNode(hoveredNode?.id || null)
    canvas.style.cursor = hoveredNode ? 'pointer' : 'default'
  }

  return (
    <canvas
      ref={canvasRef}
      onClick={handleCanvasClick}
      onMouseMove={handleCanvasMouseMove}
      className="w-full h-full rounded-lg bg-gradient-to-br from-gray-50 to-blue-50"
    />
  )
}

