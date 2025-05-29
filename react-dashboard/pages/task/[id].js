import fs from 'fs'
import path from 'path'
import { useState } from 'react'
import Navigation from '../../components/Navigation'

export async function getStaticPaths() {
  const tasksDir = path.join(process.cwd(), '..', '.tasks')
  const paths = []
  try {
    const queues = fs.readdirSync(tasksDir)
    for (const q of queues) {
      const queueDir = path.join(tasksDir, q)
      for (const file of fs.readdirSync(queueDir)) {
        if (file.endsWith('.json') && file !== 'meta.json') {
          const id = file.replace('.json', '')
          paths.push({ params: { id } })
        }
      }
    }
  } catch {
    // ignore build errors
  }
  return { paths, fallback: false }
}

export async function getStaticProps({ params }) {
  const { id } = params
  const queue = id.split('-')[0]
  const file = path.join(process.cwd(), '..', '.tasks', queue, `${id}.json`)
  const task = JSON.parse(fs.readFileSync(file, 'utf8'))
  return { props: { task } }
}

export default function TaskPage({ task }) {
  const [title, setTitle] = useState(task.title)
  const [status, setStatus] = useState(task.status)

  const save = async () => {
    await fetch('/api/update-task', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: task.id, updates: { title, status } })
    })
    alert('Task updated')
  }

  return (
    <div style={{ padding: 16 }}>
      <Navigation />
      <h1>{task.id}</h1>
      <div style={{ marginBottom: 8 }}>
        <label>
          Title:
          <input value={title} onChange={e => setTitle(e.target.value)} style={{ marginLeft: 4 }} />
        </label>
      </div>
      <div style={{ marginBottom: 8 }}>
        <label>
          Status:
          <select value={status} onChange={e => setStatus(e.target.value)} style={{ marginLeft: 4 }}>
            <option value="todo">todo</option>
            <option value="in_progress">in_progress</option>
            <option value="done">done</option>
          </select>
        </label>
      </div>
      <button onClick={save} style={{ marginBottom: 16 }}>Save</button>
      <h2>Description</h2>
      <p>{task.description}</p>
      <h2>Comments</h2>
      <ul>
        {(task.comments || []).map(c => (
          <li key={c.id}>{c.text}</li>
        ))}
      </ul>
      <h2>Links</h2>
      <ul>
        {Object.entries(task.links || {}).flatMap(([rel, list]) =>
          list.map(l => <li key={`${rel}-${l}`}>{rel}: {l}</li>)
        )}
      </ul>
    </div>
  )
}
