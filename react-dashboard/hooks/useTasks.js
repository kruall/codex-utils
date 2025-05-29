import { useEffect, useState } from 'react'

export default function useTasks() {
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    async function fetchTasks() {
      try {
        const res = await fetch('/api/tasks')
        const data = await res.json()
        setTasks(data.tasks || [])
      } catch {
        setTasks([])
      }
    }
    fetchTasks()
  }, [])

  return tasks
}
