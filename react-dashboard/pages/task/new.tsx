import { useState, ChangeEvent } from 'react'
import Navigation from '../../components/Navigation'
import styles from '../Page.module.css'
import { useAuth } from '../../context/AuthContext'
import { useRepo } from '../../context/RepoContext'
import { useTaskContext } from '../../context/TaskContext'
import { createTaskInRepo } from '../../lib/githubTasks'

export default function NewTaskPage() {
  const [id, setId] = useState('')
  const [title, setTitle] = useState('')
  const [status, setStatus] = useState<'todo' | 'in_progress' | 'done'>('todo')
  const [description, setDescription] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const { token } = useAuth()
  const { repo } = useRepo()
  const { setTasks } = useTaskContext()

  const validate = (): boolean => {
    if (!id.trim() || !title.trim()) {
      setError('ID and title are required')
      return false
    }
    return true
  }

  const save = async (): Promise<void> => {
    if (!validate()) return
    if (!repo) {
      setError('No repository selected')
      return
    }
    setSaving(true)
    setError('')
    setSuccess(false)
    try {
      const ok = await createTaskInRepo(
        repo,
        { id: id.trim(), title: title.trim(), status, description: description.trim() || undefined },
        token || undefined
      )
      if (!ok) {
        throw new Error('Failed to create task')
      }
      setTasks((ts) => [...ts, { id: id.trim(), title: title.trim(), status, description }])
      setSuccess(true)
      setId('')
      setTitle('')
      setDescription('')
      setStatus('todo')
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('Failed to create task')
      }
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className={styles.container}>
      <Navigation />
      <h1>New Task</h1>
      {error && <p className={styles.error}>{error}</p>}
      {success && <p className={styles.success}>Task created</p>}
      <div className={styles.marginBottom}>
        <label>
          ID:
          <input value={id} onChange={(e: ChangeEvent<HTMLInputElement>) => setId(e.target.value)} className={styles.inline} />
        </label>
      </div>
      <div className={styles.marginBottom}>
        <label>
          Title:
          <input value={title} onChange={(e: ChangeEvent<HTMLInputElement>) => setTitle(e.target.value)} className={styles.inline} />
        </label>
      </div>
      <div className={styles.marginBottom}>
        <label>
          Status:
          <select value={status} onChange={(e: ChangeEvent<HTMLSelectElement>) => setStatus(e.target.value as any)} className={styles.inline}>
            <option value="todo">todo</option>
            <option value="in_progress">in_progress</option>
            <option value="done">done</option>
          </select>
        </label>
      </div>
      <div className={styles.marginBottom}>
        <label>
          Description:
          <textarea value={description} onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setDescription(e.target.value)} />
        </label>
      </div>
      <button onClick={save} disabled={saving}>{saving ? 'Saving...' : 'Create'}</button>
    </div>
  )
}
