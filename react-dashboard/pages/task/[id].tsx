import { useState, ChangeEvent, useEffect } from 'react'
import { useRouter } from 'next/router'
import { useTaskContext } from '../../context/TaskContext'
import { useAuth } from '../../context/AuthContext'
import Navigation from '../../components/Navigation'
import useEpics from '../../hooks/useEpics'
import useTasks from '../../hooks/useTasks'
import TaskEpicInfo from '../../components/TaskEpicInfo'
import styles from '../Page.module.css'
import { Task } from '../../types'

export default function TaskPage() {
  const router = useRouter()
  const { id } = router.query
  const tasks = useTasks()
  const task = tasks.find(t => t.id === id)

  const [title, setTitle] = useState<string>('')
  const [status, setStatus] = useState<string>('todo')
  const [saving, setSaving] = useState<boolean>(false)
  const [error, setError] = useState<string>('')
  const [success, setSuccess] = useState<boolean>(false)
  const { setTasks } = useTaskContext()
  const { csrfToken, token } = useAuth()
  const epics = useEpics()
  const tasksList = useTasks()

  useEffect(() => {
    if (task) {
      setTitle(task.title)
      setStatus(task.status)
    }
  }, [task])

  if (!router.isReady || !id) {
    return (
      <div className={styles.container}>
        <Navigation />
        <p>Loading...</p>
      </div>
    )
  }

  if (!task) {
    return (
      <div className={styles.container}>
        <Navigation />
        <p>Task not found</p>
      </div>
    )
  }

  const save = async (): Promise<void> => {
    setSaving(true)
    setError('')
    setSuccess(false)
    try {
      const res = await fetch('/api/update-task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfToken || '',
          ...(token ? { Authorization: `token ${token}` } : {})
        },
        body: JSON.stringify({
          repo: (process.env.NEXT_PUBLIC_GITHUB_REPOS || '').split(',')[0],
          task: { id: task.id, title, status }
        })
      })

      const data = await res.json().catch(() => null)

      if (!res.ok) {
        const message = data && typeof data.error === 'string'
          ? data.error
          : `Request failed: ${res.status} ${res.statusText}`
        throw new Error(message)
      }

      if (data && data.task) {
        setTasks((ts: Task[]) => ts.map((t: Task) => (t.id === task.id ? { ...t, ...data.task } : t)))
      }
      setSuccess(true)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to update task')
      }
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
      <TaskEpicInfo taskId={task.id} epics={epics} tasks={tasksList} />
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
