import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { Task, TaskContextType } from '../types'
import { useAuth } from './AuthContext'
import { useRepo } from './RepoContext'
import { fetchTasksFromRepos } from '../lib/githubTasks'

const TaskContext = createContext<TaskContextType>({ tasks: [], setTasks: () => {} })

interface TaskProviderProps {
  children: ReactNode;
}

export function TaskProvider({ children }: TaskProviderProps) {
  const [tasks, setTasks] = useState<Task[]>([])
  const { token } = useAuth()
  const { repo } = useRepo()

  useEffect(() => {
    async function fetchTasks() {
      const repos: string[] = []
      if (repo) {
        repos.push(repo)
      }
      const reposEnv = process.env.NEXT_PUBLIC_GITHUB_REPOS
      if (reposEnv) {
        repos.push(...reposEnv.split(',').map(r => r.trim()).filter(Boolean))
      }
      if (repos.length > 0) {
        const repoResults = await fetchTasksFromRepos(repos, token || undefined)

        // Extract and flatten tasks from all repositories
        const allTasks: Task[] = []
        let anySuccess = false
        repoResults.forEach(result => {
          if (result.tasks && Array.isArray(result.tasks) && !result.error) {
            allTasks.push(...result.tasks)
            anySuccess = true
          }
        })

        if (anySuccess && allTasks.length > 0) {
          setTasks(allTasks)
          if (typeof window !== 'undefined') {
            localStorage.setItem('cachedTasks', JSON.stringify(allTasks))
          }
        } else {
          const cached = typeof window !== 'undefined' ? localStorage.getItem('cachedTasks') : null
          if (cached) {
            try {
              setTasks(JSON.parse(cached))
            } catch {
              setTasks([])
            }
          } else {
            setTasks([])
          }
        }
        return
      }
      try {
        const res = await fetch('/codex-utils/tasks.json')
        const data: Task[] = await res.json()
        setTasks(data || [])
      } catch {
        const cached = typeof window !== 'undefined' ? localStorage.getItem('cachedTasks') : null
        if (cached) {
          try {
            setTasks(JSON.parse(cached))
            return
          } catch { /* ignore */ }
        }
        setTasks([])
      }
    }
    fetchTasks()
  }, [token, repo])

  return (
    <TaskContext.Provider value={{ tasks, setTasks }}>
      {children}
    </TaskContext.Provider>
  )
}

export function useTaskContext(): TaskContextType {
  return useContext(TaskContext)
} 