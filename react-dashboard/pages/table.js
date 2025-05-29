import TaskTable from '../components/TaskTable'
import Navigation from '../components/Navigation'
import useTasks from '../hooks/useTasks'

export default function TablePage() {
  const tasks = useTasks()

  return (
    <div style={{ padding: 16 }}>
      <Navigation />
      <h1>Task List</h1>
      <TaskTable tasks={tasks} />
    </div>
  )
}
