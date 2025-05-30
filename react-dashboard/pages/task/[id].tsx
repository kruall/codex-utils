import fs from 'fs'
import path from 'path'
import { useState, ChangeEvent } from 'react'
import { GetStaticPaths, GetStaticProps } from 'next'
import { useTaskContext } from '../../context/TaskContext'
import Navigation from '../../components/Navigation'
import styles from '../Page.module.css'
import { Task } from '../../types'

interface TaskPageProps {
  task: Task & {
    description?: string;
    comments?: Array<{ id: string; text: string }>;
    links?: Record<string, string[]>;
  };
}

export const getStaticPaths: GetStaticPaths = async () => {
  const tasksDir = path.join(process.cwd(), '..', '.tasks')
  const paths: Array<{ params: { id: string } }> = []
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

export const getStaticProps: GetStaticProps<TaskPageProps> = async ({ params }) => {
  if (!params || !params.id) {
    return { notFound: true }
  }
  
  const id = params.id as string
  const queue = id.split('-')[0]
  const file = path.join(process.cwd(), '..', '.tasks', queue, `${id}.json`)
  const task = JSON.parse(fs.readFileSync(file, 'utf8'))
  return { props: { task } }
}

export default function TaskPage({ task }: TaskPageProps) {
  const [title, setTitle] = useState<string>(task.title)
  const [status, setStatus] = useState<string>(task.status)
  const [saving, setSaving] = useState<boolean>(false)
  const [error, setError] = useState<string>('')
  const [success, setSuccess] = useState<boolean>(false)
  const { setTasks } = useTaskContext()

  const save = async (): Promise<void> => {
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
        setTasks((ts: Task[]) => ts.map((t: Task) => (t.id === task.id ? { ...t, ...data.task } : t)))
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
      {error && <p className={styles.error} role="alert">{error}</p>}
      {success && <p className={styles.success}>Task updated</p>}
      <div className={styles.marginBottom}>
        <label>
          Title:
          <input value={title} onChange={(e: ChangeEvent<HTMLInputElement>) => setTitle(e.target.value)} className={styles.inline} />
        </label>
      </div>
      <div className={styles.marginBottom}>
        <label>
          Status:
          <select value={status} onChange={(e: ChangeEvent<HTMLSelectElement>) => setStatus(e.target.value)} className={styles.inline}>
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
        {(task.comments || []).map((c) => (
          <li key={c.id}>{c.text}</li>
        ))}
      </ul>
      <h2>Links</h2>
      <ul>
        {Object.entries(task.links || {}).flatMap(([rel, list]) =>
          list.map((l: string) => <li key={`${rel}-${l}`}>{rel}: {l}</li>)
        )}
      </ul>
    </div>
  )
} 