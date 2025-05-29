import { loadTasks } from '../../lib/tasks'

export default function handler(req, res) {
  const tasks = loadTasks()
  res.status(200).json({ tasks })
}
