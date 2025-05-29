import fs from 'fs'
import path from 'path'

export function loadTasks() {
  const tasksDir = path.join(process.cwd(), '..', '.tasks')
  const tasks = []
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
  return tasks
}
