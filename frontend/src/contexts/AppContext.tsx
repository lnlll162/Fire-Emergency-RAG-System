'use client'

import { createContext, useContext, useState, ReactNode } from 'react'

interface AppState {
  isLoading: boolean
  error: string | null
  theme: 'light' | 'dark'
}

interface AppContextType {
  state: AppState
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setTheme: (theme: 'light' | 'dark') => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AppState>({
    isLoading: false,
    error: null,
    theme: 'light'
  })

  const setLoading = (loading: boolean) => {
    setState(prev => ({ ...prev, isLoading: loading }))
  }

  const setError = (error: string | null) => {
    setState(prev => ({ ...prev, error }))
  }

  const setTheme = (theme: 'light' | 'dark') => {
    setState(prev => ({ ...prev, theme }))
  }

  return (
    <AppContext.Provider value={{ state, setLoading, setError, setTheme }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}

