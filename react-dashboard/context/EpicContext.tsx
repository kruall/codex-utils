import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { Epic } from '../types'

interface EpicContextType {
  epics: Epic[]
  setEpics: (epics: Epic[] | ((prev: Epic[]) => Epic[])) => void
}

const EpicContext = createContext<EpicContextType>({ epics: [], setEpics: () => {} })

interface EpicProviderProps {
  children: ReactNode
}

export function EpicProvider({ children }: EpicProviderProps) {
  const [epics, setEpics] = useState<Epic[]>([])

  useEffect(() => {
    async function fetchEpics() {
      try {
        const res = await fetch('/codex-utils/epics.json')
        const data: Epic[] = await res.json()
        setEpics(data || [])
      } catch {
        setEpics([])
      }
    }
    fetchEpics()
  }, [])

  return (
    <EpicContext.Provider value={{ epics, setEpics }}>
      {children}
    </EpicContext.Provider>
  )
}

export function useEpicContext(): EpicContextType {
  return useContext(EpicContext)
}

