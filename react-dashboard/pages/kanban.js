import Kanban from '../components/Kanban'
import Navigation from '../components/Navigation'
import useTasks from '../hooks/useTasks'
import styles from './Page.module.css'

export default function KanbanPage() {
  const tasks = useTasks()

  return (
    <div className={styles.container}>
      <Navigation />
      <h1>Kanban Board</h1>
      <Kanban tasks={tasks} />
    </div>
  )
}
