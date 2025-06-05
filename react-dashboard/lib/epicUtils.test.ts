import { calculateEpicProgress } from './epicUtils'
import { Epic, Task } from '../types'

test('shared epics are only counted once', () => {
  const epics: Epic[] = [
    { id: 'A', title: 'A', status: 'open', child_tasks: [], child_epics: ['B', 'C'], parent_epic: null },
    { id: 'B', title: 'B', status: 'open', child_tasks: [], child_epics: ['D'], parent_epic: 'A' },
    { id: 'C', title: 'C', status: 'open', child_tasks: [], child_epics: ['D'], parent_epic: 'A' },
    { id: 'D', title: 'D', status: 'open', child_tasks: ['T1'], child_epics: [], parent_epic: null }
  ]
  const tasks: Task[] = [
    { id: 'T1', title: 't', status: 'done' }
  ]

  const progress = calculateEpicProgress(epics[0], tasks, epics)
  expect(progress).toEqual({ total: 1, done: 1 })
})
