import fs from 'fs'
import path from 'path'
import TaskTable from '../components/TaskTable'
import Kanban from '../components/Kanban'

export async function getStaticProps() {
  const tasksDir = path.join(process.cwd(), '..', '.tasks')
  let tasks = []
  try {
    const queues = fs.readdirSync(tasksDir)
    for (const q of queues) {
      const queueDir = path.join(tasksDir, q)
      for (const file of fs.readdirSync(queueDir)) {
        if (file.endsWith('.json') && file !== 'meta.json') {
          const data = JSON.parse(fs.readFileSync(path.join(queueDir, file), 'utf8'))
          if (data.id) {
            tasks.push(data)
          }
        }
      }
    }
  } catch {
    // ignore errors for build portability
  }
  return { props: { tasks } }
}

export default function Home({ tasks }) {
  return (
    <div style={{ padding: 16 }}>
      <h1>Task Dashboard</h1>
      <h2>Table View</h2>
      <TaskTable tasks={tasks} />
      <h2>Kanban View</h2>
      <Kanban tasks={tasks} />
    </div>
  )
}
