import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'

export interface RepoContextType {
  repo: string | null
  setRepo: (r: string | null) => void
}

const RepoContext = createContext<RepoContextType>({ repo: null, setRepo: () => {} })

interface RepoProviderProps {
  children: ReactNode
}

export function RepoProvider({ children }: RepoProviderProps) {
  const [repo, setRepoState] = useState<string | null>(null)

  useEffect(() => {
    const stored = typeof window !== 'undefined' ? localStorage.getItem('selectedRepo') : null
    if (stored) {
      setRepoState(stored)
    }
  }, [])

  const setRepo = (r: string | null): void => {
    setRepoState(r)
    if (typeof window !== 'undefined') {
      if (r) {
        localStorage.setItem('selectedRepo', r)
      } else {
        localStorage.removeItem('selectedRepo')
      }
    }
  }

  return <RepoContext.Provider value={{ repo, setRepo }}>{children}</RepoContext.Provider>
}

export function useRepo(): RepoContextType {
  return useContext(RepoContext)
}
