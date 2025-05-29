const fs = require('fs')
const path = require('path')

function loadTasks() {
  const tasksDir = path.join(__dirname, '..', '..', '.tasks')
  const tasks = []
  
  try {
    const queues = fs.readdirSync(tasksDir)
    for (const q of queues) {
      const queueDir = path.join(tasksDir, q)
      if (!fs.statSync(queueDir).isDirectory()) continue
      
      for (const file of fs.readdirSync(queueDir)) {
        if (file.endsWith('.json') && file !== 'meta.json') {
          try {
            const data = JSON.parse(fs.readFileSync(path.join(queueDir, file), 'utf8'))
            if (data.id) {
              tasks.push(data)
            }
          } catch (err) {
            console.warn(`Failed to parse ${file}:`, err.message)
          }
        }
      }
    }
  } catch (err) {
    console.warn('Failed to load tasks:', err.message)
  }
  
  return tasks
}

function generateTasksJson() {
  const tasks = loadTasks()
  const outputPath = path.join(__dirname, '..', 'public', 'tasks.json')
  
  // Ensure public directory exists
  const publicDir = path.dirname(outputPath)
  if (!fs.existsSync(publicDir)) {
    fs.mkdirSync(publicDir, { recursive: true })
  }
  
  fs.writeFileSync(outputPath, JSON.stringify(tasks, null, 2))
  console.log(`Generated ${outputPath} with ${tasks.length} tasks`)
}

if (require.main === module) {
  generateTasksJson()
}

module.exports = { loadTasks, generateTasksJson } 