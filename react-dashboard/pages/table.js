import TaskTable from '../components/TaskTable'
import Navigation from '../components/Navigation'
import styles from './Page.module.css'

export default function TablePage() {
  return (
    <div className={styles.container}>
      <Navigation />
      <h1>Task List</h1>
      <TaskTable />
    </div>
  )
}
