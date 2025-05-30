import TaskTable from '../components/TaskTable'
import Navigation from '../components/Navigation'
import useTasks from '../hooks/useTasks'
import styles from './Page.module.css'
import { Task } from '../types'

export default function TodoPage() {
  const allTasks = useTasks()
  const tasks = allTasks.filter((t: Task) => t.status === 'todo')

  return (
    <div className={styles.container}>
      <Navigation />
      <h1>Todo Tasks</h1>
      <TaskTable tasks={tasks} />
    </div>
  )
} 