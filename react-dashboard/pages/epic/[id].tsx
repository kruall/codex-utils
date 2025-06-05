import fs from 'fs'
import path from 'path'
import { GetStaticPaths, GetStaticProps } from 'next'
import Navigation from '../../components/Navigation'
import EpicTree from '../../components/EpicTree'
import styles from '../Page.module.css'
import { Epic } from '../../types'
import useEpics from '../../hooks/useEpics'
import useTasks from '../../hooks/useTasks'
import { calculateEpicProgress } from '../../lib/epicUtils'

interface EpicPageProps {
  epic: Epic
}

export const getStaticPaths: GetStaticPaths = async () => {
  const epicsDir = path.join(process.cwd(), '..', '.epics')
  const paths: Array<{ params: { id: string } }> = []
  try {
    for (const file of fs.readdirSync(epicsDir)) {
      if (file.endsWith('.json')) {
        paths.push({ params: { id: file.replace('.json', '') } })
      }
    }
  } catch {
    // ignore
  }
  return { paths, fallback: false }
}

export const getStaticProps: GetStaticProps<EpicPageProps> = async ({ params }) => {
  if (!params || !params.id) {
    return { notFound: true }
  }
  const id = params.id as string
  const file = path.join(process.cwd(), '..', '.epics', `${id}.json`)
  try {
    const data = fs.readFileSync(file, 'utf8')
    const epic = JSON.parse(data)
    return { props: { epic } }
  } catch {
    return { notFound: true }
  }
}

export default function EpicPage({ epic }: EpicPageProps) {
  const epics = useEpics()
  const tasks = useTasks()
  const current = epics.find(e => e.id === epic.id) || epic
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

