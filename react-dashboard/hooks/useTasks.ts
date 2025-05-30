import { useTaskContext } from '../context/TaskContext'
import { Task } from '../types'

export default function useTasks(): Task[] {
  const { tasks } = useTaskContext()
  return tasks
} 