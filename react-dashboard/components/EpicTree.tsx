import React from 'react'
import Link from 'next/link'
import { Epic, Task } from '../types'
import { calculateEpicProgress } from '../lib/epicUtils'

interface EpicTreeProps {
  epic: Epic
  epics: Epic[]
  tasks: Task[]
}

export default function EpicTree({ epic, epics, tasks }: EpicTreeProps) {
  const progress = calculateEpicProgress(epic, tasks, epics)
  const pct = progress.total ? Math.round((progress.done / progress.total) * 100) : 0

  return (
    <li>
      <Link href={`/epic/${epic.id}`}>{epic.id}</Link> - {epic.title} ({pct}%)
      {epic.child_tasks.length > 0 && (
        <ul>
          {epic.child_tasks.map(tid => (
            <li key={tid}>
              <Link href={`/task/${tid}`}>{tid}</Link>
            </li>
          ))}
        </ul>
      )}
      {epic.child_epics.length > 0 && (
        <ul>
          {epic.child_epics.map(eid => {
            const child = epics.find(e => e.id === eid)
            return child ? (
              <EpicTree key={eid} epic={child} epics={epics} tasks={tasks} />
            ) : (
              <li key={eid}>{eid}</li>
            )
          })}
        </ul>
      )}
    </li>
  )
}

