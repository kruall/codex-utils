import React from 'react'
import Link from 'next/link'
import { Epic, Task } from '../types'

interface TaskEpicInfoProps {
  taskId: string
  epics: Epic[]
  tasks: Task[]
}

export default function TaskEpicInfo({ taskId, epics, tasks }: TaskEpicInfoProps) {
  const parents = epics.filter(e => e.child_tasks.includes(taskId))
  if (parents.length === 0) return null

  const findTask = (tid: string): Task | undefined => tasks.find(t => t.id === tid)
  const findEpic = (eid: string): Epic | undefined => epics.find(e => e.id === eid)

  return (
    <div>
      <h2>Epics</h2>
      {parents.map(epic => {
        const otherTasks = epic.child_tasks.filter(tid => tid !== taskId)
        return (
          <div key={epic.id} style={{ marginBottom: '1rem' }}>
            <p>
              <Link href={`/epic/${epic.id}`}>{epic.id}</Link> - {epic.title} [{epic.status}]
            </p>
            {epic.description && <p>{epic.description}</p>}
            {otherTasks.length > 0 && (
              <>
                <h3>Tasks</h3>
                <ul>
                  {otherTasks.map(tid => {
                    const t = findTask(tid)
                    return (
                      <li key={tid}>
                        {t ? <Link href={`/task/${tid}`}>{tid}</Link> : tid}
                        {t ? `: ${t.title} (${t.status})` : ' (missing)'}
                      </li>
                    )
                  })}
                </ul>
              </>
            )}
            {epic.child_epics.length > 0 && (
              <>
                <h3>Child Epics</h3>
                <ul>
                  {epic.child_epics.map(eid => {
                    const child = findEpic(eid)
                    return (
                      <li key={eid}>
                        {child ? <Link href={`/epic/${eid}`}>{eid}</Link> : eid}
                        {child ? `: ${child.title} (${child.status})` : ' (missing)'}
                      </li>
                    )
                  })}
                </ul>
              </>
            )}
          </div>
        )
      })}
    </div>
  )
}
