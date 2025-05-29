import fs from 'fs'
import path from 'path'

export default function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' })
    return
  }

  const { id, updates } = req.body
  if (!id || !updates) {
    res.status(400).json({ error: 'Invalid request' })
    return
  }

  try {
    const queue = id.split('-')[0]
    const file = path.join(process.cwd(), '..', '.tasks', queue, `${id}.json`)
    const data = JSON.parse(fs.readFileSync(file, 'utf8'))
    Object.assign(data, updates, { updated_at: Date.now() / 1000 })
    fs.writeFileSync(file, JSON.stringify(data, null, 2))
    res.status(200).json({ success: true, task: data })
  } catch (err) {
    res.status(500).json({ error: 'Failed to update task' })
  }
}
