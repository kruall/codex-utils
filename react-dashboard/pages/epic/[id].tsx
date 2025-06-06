import { useRouter } from 'next/router'
import Link from 'next/link'
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
  const parent = current && current.parent_epic ? epics.find(e => e.id === current.parent_epic) : null

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
      {current.description && <p>{current.description}</p>}
      <p>Status: {current.status}</p>
      <p>Progress: {pct}% ({progress.done}/{progress.total})</p>
      {parent && (
        <p>
          Parent Epic: <Link href={`/epic/${parent.id}`}>{parent.id}</Link> - {parent.title}
        </p>
      )}
      {current.child_tasks.length > 0 && (
        <>
          <h2>Tasks</h2>
          <ul>
            {current.child_tasks.map(tid => {
              const t = tasks.find(t => t.id === tid)
              return (
                <li key={tid}>
                  <Link href={`/task/${tid}`}>{tid}</Link>
                  {t ? `: ${t.title} (${t.status})` : ' (missing)'}
                </li>
              )
            })}
          </ul>
        </>
      )}
      {current.child_epics.length > 0 && (
        <>
          <h2>Child Epics</h2>
          <ul>
            {current.child_epics.map(eid => {
              const child = epics.find(e => e.id === eid)
              return (
                <li key={eid}>
                  <Link href={`/epic/${eid}`}>{eid}</Link>
                  {child ? `: ${child.title} (${child.status})` : ' (missing)'}
                </li>
              )
            })}
          </ul>
        </>
      )}
      <h2>Hierarchy</h2>
      <ul>
        <EpicTree epic={current} epics={epics} tasks={tasks} />
      </ul>
    </div>
  )
}

