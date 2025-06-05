import { useEffect, useState } from 'react'
import Navigation from '../components/Navigation'
import styles from './Page.module.css'
import { useAuth } from '../context/AuthContext'
import { useRepo } from '../context/RepoContext'

interface Repo {
  full_name: string
}

export default function ReposPage() {
  const { token } = useAuth()
  const { repo, setRepo } = useRepo()
  const [repos, setRepos] = useState<Repo[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      if (!token) return
      setLoading(true)
      setError('')
      try {
        const res = await fetch('https://api.github.com/user/repos?per_page=100', {
          headers: { Authorization: `token ${token}` }
        })
        if (!res.ok) throw new Error(`Failed to fetch repos: ${res.status}`)
        const data = await res.json()
        setRepos(Array.isArray(data) ? data : [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch repos')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [token])

  const select = async (r: string) => {
    if (!token) return
    try {
      const res = await fetch(`https://api.github.com/repos/${r}`, {
        headers: { Authorization: `token ${token}` }
      })
      if (!res.ok) throw new Error('Repository access failed')
      setRepo(r)
    } catch (err) {
      alert(err instanceof Error ? err.message : String(err))
    }
  }

  return (
    <div className={styles.container}>
      <Navigation />
      <h1>Select Repository</h1>
      {repo && <p>Current repository: {repo}</p>}
      {loading && <p>Loading...</p>}
      {error && <p className={styles.error}>{error}</p>}
      <ul>
        {repos.map(r => (
          <li key={r.full_name}>
            <button onClick={() => select(r.full_name)}>{r.full_name}</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
