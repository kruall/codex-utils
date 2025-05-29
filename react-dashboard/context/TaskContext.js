import React, { createContext, useContext, useEffect, useState } from 'react'

const TaskContext = createContext({ tasks: [], setTasks: () => {} })

export function TaskProvider({ children }) {
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    async function fetchTasks() {
      try {
        const res = await fetch('/codex-utils/tasks.json')
        const data = await res.json()
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

export function useTaskContext() {
  return useContext(TaskContext)
}
