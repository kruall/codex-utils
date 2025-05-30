import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { Task, TaskContextType } from '../types'

const TaskContext = createContext<TaskContextType>({ tasks: [], setTasks: () => {} })

interface TaskProviderProps {
  children: ReactNode;
}

export function TaskProvider({ children }: TaskProviderProps) {
  const [tasks, setTasks] = useState<Task[]>([])

  useEffect(() => {
    async function fetchTasks() {
      try {
        const res = await fetch('/codex-utils/tasks.json')
        const data: Task[] = await res.json()
        setTasks(data || [])
      } catch {
        setTasks([])
      }
    }
    fetchTasks()
  }, [])

  return (
    <TaskContext.Provider value={{ tasks, setTasks }}>
      {children}
    </TaskContext.Provider>
  )
}

export function useTaskContext(): TaskContextType {
  return useContext(TaskContext)
} 