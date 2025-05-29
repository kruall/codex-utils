import fs from 'fs'
import path from 'path'
import TaskTable from '../components/TaskTable'
import Navigation from '../components/Navigation'

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
          if (data.id && data.status === 'todo') {
            tasks.push(data)
          }
        }
      }
    }
  } catch (error) {
    console.error('Error reading tasks directory:', error);
  }
  return { props: { tasks } }
}

export default function TodoPage({ tasks }) {
  return (
    <div style={{ padding: 16 }}>
      <Navigation />
      <h1>Todo Tasks</h1>
      <TaskTable tasks={tasks} />
    </div>
  )
}
