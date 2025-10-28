'use client'

import React, { Component, ReactNode } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 flex items-center justify-center p-4">
          <Card className="max-w-2xl w-full shadow-2xl border-2 border-red-300">
            <CardHeader className="bg-gradient-to-r from-red-100 to-orange-100">
              <CardTitle className="flex items-center text-2xl text-red-800">
                <ExclamationTriangleIcon className="h-8 w-8 mr-3" />
                应用出错了
              </CardTitle>
              <CardDescription className="text-base">
                很抱歉，应用遇到了一个错误。您可以尝试刷新页面。
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              {this.state.error && (
                <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
                  <p className="text-sm font-mono text-red-800 break-all">
                    {this.state.error.toString()}
                  </p>
                </div>
              )}
              <div className="flex justify-center pt-4">
                <Button
                  onClick={this.handleReset}
                  className="bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700"
                  size="lg"
                >
                  <ArrowPathIcon className="h-5 w-5 mr-2" />
                  重新加载页面
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary

