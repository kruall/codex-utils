import TaskTable from '../components/TaskTable'
import Navigation from '../components/Navigation'
import useTasks from '../hooks/useTasks'
import styles from './Page.module.css'

export default function TablePage() {
  const tasks = useTasks()

  return (
    <div className={styles.container}>
      <Navigation />
      <h1>Task List</h1>
      <TaskTable tasks={tasks} />
    </div>
  )
}
