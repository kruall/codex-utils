import Navigation from '../../components/Navigation'
import EpicTree from '../../components/EpicTree'
import styles from '../Page.module.css'
import useEpics from '../../hooks/useEpics'
import useTasks from '../../hooks/useTasks'

export default function EpicsPage() {
  const epics = useEpics()
  const tasks = useTasks()

  const topLevel = epics.filter(e => !e.parent_epic)

  return (
    <div className={styles.container}>
      <Navigation />
      <h1>Epics</h1>
      <ul>
        {topLevel.map(e => (
          <EpicTree key={e.id} epic={e} epics={epics} tasks={tasks} />
        ))}
      </ul>
    </div>
  )
}

