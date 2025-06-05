import { useRouter } from 'next/router'
import Navigation from '../../components/Navigation'
import EpicTree from '../../components/EpicTree'
import styles from '../Page.module.css'
import useEpics from '../../hooks/useEpics'
import useTasks from '../../hooks/useTasks'
import { calculateEpicProgress } from '../../lib/epicUtils'

export default function EpicPage() {
  const router = useRouter()
  const { id } = router.query
  const epics = useEpics()
  const tasks = useTasks()
  const current = epics.find(e => e.id === id)

  if (!router.isReady || !id) {
    return (
      <div className={styles.container}>
        <Navigation />
        <p>Loading...</p>
      </div>
    )
  }

  if (!current) {
    return (
      <div className={styles.container}>
        <Navigation />
        <p>Epic not found</p>
      </div>
    )
  }
  const progress = calculateEpicProgress(current, tasks, epics)
  const pct = progress.total ? Math.round((progress.done / progress.total) * 100) : 0

  return (
    <div className={styles.container}>
      <Navigation />
      <h1>{current.id}</h1>
      <p>{current.title}</p>
      <p>Status: {current.status}</p>
      <p>Progress: {pct}% ({progress.done}/{progress.total})</p>
      <h2>Hierarchy</h2>
      <ul>
        <EpicTree epic={current} epics={epics} tasks={tasks} />
      </ul>
    </div>
  )
}

