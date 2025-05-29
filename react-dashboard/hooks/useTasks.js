import { useEffect, useState } from 'react'

export default function useTasks() {
  const [tasks, setTasks] = useState([])

  useEffect(() => {
    async function fetchTasks() {
      try {
        // For static export, we need to load tasks from a pre-generated JSON file
        const res = await fetch('/codex-utils/tasks.json')
        const data = await res.json()
        setTasks(data || [])
      } catch {
        setTasks([])
      }
    }
    fetchTasks()
  }, [])

  return tasks
}
