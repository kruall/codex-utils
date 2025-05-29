import { useTaskContext } from '../context/TaskContext'

export default function useTasks() {
  const { tasks } = useTaskContext()
  return tasks
}
