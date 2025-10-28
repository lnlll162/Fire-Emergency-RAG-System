'use client'

import { useState, useCallback } from 'react'
import { ToastProps, ToastType } from '@/components/ui/toast'

export function useToast() {
  const [toasts, setToasts] = useState<ToastProps[]>([])

  const addToast = useCallback((type: ToastType, message: string, duration?: number) => {
    const id = `toast-${Date.now()}-${Math.random()}`
    const newToast: ToastProps = {
      id,
      type,
      message,
      duration,
      onClose: (toastId: string) => {
        setToasts((prev) => prev.filter((t) => t.id !== toastId))
      },
    }
    setToasts((prev) => [...prev, newToast])
  }, [])

  const success = useCallback(
    (message: string, duration?: number) => addToast('success', message, duration),
    [addToast]
  )

  const error = useCallback(
    (message: string, duration?: number) => addToast('error', message, duration),
    [addToast]
  )

  const warning = useCallback(
    (message: string, duration?: number) => addToast('warning', message, duration),
    [addToast]
  )

  const info = useCallback(
    (message: string, duration?: number) => addToast('info', message, duration),
    [addToast]
  )

  return {
    toasts,
    success,
    error,
    warning,
    info,
  }
}

