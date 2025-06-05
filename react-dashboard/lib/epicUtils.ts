import { Epic, Task } from '../types'

export interface EpicProgress {
  total: number
  done: number
}

export function calculateEpicProgress(
  epic: Epic,
  tasks: Task[],
  epics: Epic[],
): EpicProgress {
  const taskMap = new Map(tasks.map(t => [t.id, t]))
  const epicMap = new Map(epics.map(e => [e.id, e]))

  function helper(e: Epic, seen: Set<string>): EpicProgress {
    if (seen.has(e.id)) {
      return { total: 0, done: 0 }
    }
    seen.add(e.id)

    let total = 0
    let done = 0

    e.child_tasks.forEach(tid => {
      const t = taskMap.get(tid)
      if (t) {
        total += 1
        if (t.status === 'done') done += 1
      }
    })

    e.child_epics.forEach(eid => {
      const child = epicMap.get(eid)
      if (child) {
        const p = helper(child, new Set(seen))
        total += p.total
        done += p.done
      }
    })

    return { total, done }
  }

  return helper(epic, new Set())
}

