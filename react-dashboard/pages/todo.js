import TaskTable from '../components/TaskTable'
import Navigation from '../components/Navigation'
import useTasks from '../hooks/useTasks'

export default function TodoPage() {
  const allTasks = useTasks()
  const tasks = allTasks.filter(t => t.status === 'todo')

  return (
    <div style={{ padding: 16 }}>
      <Navigation />
      <h1>Todo Tasks</h1>
      <TaskTable tasks={tasks} />
    </div>
  )
}
