'use client'

import { useEffect, useState } from 'react'
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon, 
  InformationCircleIcon,
  XCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface ToastProps {
  id: string
  type: ToastType
  message: string
  duration?: number
  onClose: (id: string) => void
}

const icons = {
  success: CheckCircleIcon,
  error: XCircleIcon,
  warning: ExclamationTriangleIcon,
  info: InformationCircleIcon,
}

const colors = {
  success: {
    bg: 'bg-green-50',
    border: 'border-green-200',
    icon: 'text-green-600',
    text: 'text-green-800',
  },
  error: {
    bg: 'bg-red-50',
    border: 'border-red-200',
    icon: 'text-red-600',
    text: 'text-red-800',
  },
  warning: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-200',
    icon: 'text-yellow-600',
    text: 'text-yellow-800',
  },
  info: {
    bg: 'bg-blue-50',
    border: 'border-blue-200',
    icon: 'text-blue-600',
    text: 'text-blue-800',
  },
}

export function Toast({ id, type, message, duration = 5000, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true)
  const Icon = icons[type]
  const style = colors[type]

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      setTimeout(() => onClose(id), 300)
    }, duration)

    return () => clearTimeout(timer)
  }, [duration, id, onClose])

  return (
    <div
      className={`flex items-start p-4 mb-3 rounded-xl border-2 shadow-lg backdrop-blur-sm transition-all duration-300 ${
        style.bg
      } ${style.border} ${
        isVisible
          ? 'opacity-100 translate-x-0'
          : 'opacity-0 translate-x-full'
      }`}
    >
      <Icon className={`h-6 w-6 ${style.icon} mr-3 flex-shrink-0 mt-0.5`} />
      <div className="flex-1">
        <p className={`text-sm font-medium ${style.text}`}>{message}</p>
      </div>
      <button
        onClick={() => {
          setIsVisible(false)
          setTimeout(() => onClose(id), 300)
        }}
        className={`ml-3 flex-shrink-0 p-1 rounded-lg hover:bg-white/50 transition-colors ${style.text}`}
        aria-label="关闭"
      >
        <XMarkIcon className="h-5 w-5" />
      </button>
    </div>
  )
}

export function ToastContainer({ toasts }: { toasts: ToastProps[] }) {
  return (
    <div className="fixed top-20 right-4 z-50 w-full max-w-sm space-y-3">
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} />
      ))}
    </div>
  )
}

