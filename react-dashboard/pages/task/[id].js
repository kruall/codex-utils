import fs from 'fs'
import path from 'path'
import { useState } from 'react'
import { useTaskContext } from '../../context/TaskContext'
import Navigation from '../../components/Navigation'
import styles from '../Page.module.css'

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
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const { setTasks } = useTaskContext()

  const save = async () => {
    setSaving(true)
    setError('')
    setSuccess(false)
    try {
      const res = await fetch('/api/update-task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: task.id, updates: { title, status } })
      })
      if (!res.ok) {
        throw new Error(`Request failed: ${res.status} ${res.statusText}`)
      }
      const data = await res.json()
      if (data.task) {
        setTasks(ts => ts.map(t => (t.id === task.id ? { ...t, ...data.task } : t)))
      }
      setSuccess(true)
    } catch {
      setError('Failed to update task')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className={styles.container}>
      <Navigation />
      <h1>{task.id}</h1>
      {error && <p className={styles.error}>{error}</p>}
      {success && <p className={styles.success}>Task updated</p>}
      <div className={styles.marginBottom}>
        <label>
          Title:
          <input value={title} onChange={e => setTitle(e.target.value)} className={styles.inline} />
        </label>
      </div>
      <div className={styles.marginBottom}>
        <label>
          Status:
          <select value={status} onChange={e => setStatus(e.target.value)} className={styles.inline}>
            <option value="todo">todo</option>
            <option value="in_progress">in_progress</option>
            <option value="done">done</option>
          </select>
        </label>
      </div>
      <button onClick={save} disabled={saving} className={styles.marginBottomLarge}>
        {saving ? 'Saving...' : 'Save'}
      </button>
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
