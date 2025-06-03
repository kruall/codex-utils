import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { Task, TaskContextType } from '../types'
import { useAuth } from './AuthContext'
import { fetchTasksFromRepos } from '../lib/githubTasks'

const TaskContext = createContext<TaskContextType>({ tasks: [], setTasks: () => {} })

interface TaskProviderProps {
  children: ReactNode;
}

export function TaskProvider({ children }: TaskProviderProps) {
  const [tasks, setTasks] = useState<Task[]>([])
  const { token } = useAuth()

  useEffect(() => {
    async function fetchTasks() {
      const reposEnv = process.env.NEXT_PUBLIC_GITHUB_REPOS
      if (reposEnv) {
        const repos = reposEnv.split(',').map(r => r.trim()).filter(Boolean)
        const data = await fetchTasksFromRepos(repos, token || undefined)
        setTasks(data)
        return
      }
      try {
        const res = await fetch('/codex-utils/tasks.json')
        const data: Task[] = await res.json()
        setTasks(data || [])
      } catch {
        setTasks([])
      }
    }
    fetchTasks()
  }, [token])

  return (
    <TaskContext.Provider value={{ tasks, setTasks }}>
      {children}
    </TaskContext.Provider>
  )
}

export function useTaskContext(): TaskContextType {
  return useContext(TaskContext)
} 