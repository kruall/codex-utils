import React from 'react'
import { render, screen } from '@testing-library/react'
import EpicTree from './EpicTree'
import { Epic, Task } from '../types'

test('renders epic with progress', () => {
  const epics: Epic[] = [
    { id: 'epic-1', title: 'A', status: 'open', child_tasks: ['TM-1'], child_epics: [], parent_epic: null }
  ]
  const tasks: Task[] = [
    { id: 'TM-1', title: 't', status: 'done' }
  ]

  render(<ul><EpicTree epic={epics[0]} epics={epics} tasks={tasks} /></ul>)
  expect(screen.getByText('epic-1')).toBeInTheDocument()
  expect(screen.getByText(/100%/)).toBeInTheDocument()
})

test('handles circular references without crashing', () => {
  const epics: Epic[] = [
    { id: 'epic-a', title: 'A', status: 'open', child_tasks: [], child_epics: ['epic-b'], parent_epic: null },
    { id: 'epic-b', title: 'B', status: 'open', child_tasks: [], child_epics: ['epic-a'], parent_epic: null }
  ]
  const tasks: Task[] = []

  render(<ul><EpicTree epic={epics[0]} epics={epics} tasks={tasks} /></ul>)
  expect(screen.getByText('epic-a')).toBeInTheDocument()
  expect(screen.getByText('epic-b')).toBeInTheDocument()
})

