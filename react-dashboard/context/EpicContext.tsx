import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { Epic } from '../types'
import { useAuth } from './AuthContext'
import { useRepo } from './RepoContext'
import { fetchEpicsFromRepo } from '../lib/githubEpics'

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
  const { token } = useAuth()
  const { repo } = useRepo()

  useEffect(() => {
    async function fetchEpics() {
      const repos: string[] = []
      if (repo) {
        repos.push(repo)
      }
      const env = process.env.NEXT_PUBLIC_GITHUB_REPOS
      if (env) {
        repos.push(...env.split(',').map(r => r.trim()).filter(Boolean))
      }
      
      if (repos.length > 0) {
        const all: Epic[] = []
        let anySuccess = false
        for (const r of repos) {
          try {
            const eps = await fetchEpicsFromRepo(r, token || undefined)
            all.push(...eps)
            anySuccess = true
          } catch (err) {
            console.error('Failed to fetch epics', err)
          }
        }
        if (anySuccess) {
          setEpics(all)
          if (typeof window !== 'undefined') {
            localStorage.setItem('cachedEpics', JSON.stringify(all))
          }
        } else {
          // GitHub API failed, use cached data if available
          const cached = typeof window !== 'undefined' ? localStorage.getItem('cachedEpics') : null
          if (cached) {
            try {
              setEpics(JSON.parse(cached))
            } catch {
              setEpics([])
            }
          } else {
            setEpics([])
          }
        }
      } else {
        // No repos configured, use cached data if available
        const cached = typeof window !== 'undefined' ? localStorage.getItem('cachedEpics') : null
        if (cached) {
          try {
            setEpics(JSON.parse(cached))
          } catch {
            setEpics([])
          }
        } else {
          setEpics([])
        }
      }
    }
    fetchEpics()
  }, [token, repo])

  return (
    <EpicContext.Provider value={{ epics, setEpics }}>
      {children}
    </EpicContext.Provider>
  )
}

export function useEpicContext(): EpicContextType {
  return useContext(EpicContext)
}

