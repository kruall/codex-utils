import Kanban from '../components/Kanban'
import Navigation from '../components/Navigation'
import useTasks from '../hooks/useTasks'

export default function KanbanPage() {
  const tasks = useTasks()

  return (
    <div style={{ padding: 16 }}>
      <Navigation />
      <h1>Kanban Board</h1>
      <Kanban tasks={tasks} />
    </div>
  )
}
