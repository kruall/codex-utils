import { useState, FormEvent } from 'react'
import Navigation from '../components/Navigation'
import styles from './Page.module.css'
import { useAuth } from '../context/AuthContext'
import { dispatchWorkflow } from '../lib/githubActions'

export default function WorkflowsPage() {
  const { token } = useAuth()
  const [repo, setRepo] = useState('')
  const [workflow, setWorkflow] = useState('')
  const [ref, setRef] = useState('main')
  const [message, setMessage] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!repo || !workflow) {
      alert('Repository and workflow file are required')
      return
    }
    const ok = await dispatchWorkflow(repo, workflow, ref, undefined, token || undefined)
    setMessage(ok ? 'Workflow dispatched successfully' : 'Failed to dispatch workflow')
  }

  return (
    <div className={styles.container}>
      <Navigation />
      <h1>Dispatch GitHub Workflow</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Repository:
          <input type="text" value={repo} onChange={e => setRepo(e.target.value)} placeholder="owner/repo" />
        </label>
        <label>
          Workflow file:
          <input type="text" value={workflow} onChange={e => setWorkflow(e.target.value)} placeholder="build.yml" />
        </label>
        <label>
          Ref:
          <input type="text" value={ref} onChange={e => setRef(e.target.value)} />
        </label>
        <button type="submit">Run Workflow</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  )
}

