import Kanban from '../components/Kanban'
import Navigation from '../components/Navigation'
import styles from './Page.module.css'

export default function KanbanPage() {
  return (
    <div className={styles.container}>
      <Navigation />
      <h1>Kanban Board</h1>
      <Kanban />
    </div>
  )
} 