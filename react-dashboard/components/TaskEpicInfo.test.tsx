import React from 'react'
import { render, screen } from '@testing-library/react'
import TaskEpicInfo from './TaskEpicInfo'
import { Epic, Task } from '../types'

test('renders parent epic details with related tasks and child epics', () => {
  const epics: Epic[] = [
    { id: 'epic-1', title: 'E1', status: 'open', description: 'desc', child_tasks: ['TM-1', 'TM-2'], child_epics: ['epic-2'], parent_epic: null },
    { id: 'epic-2', title: 'E2', status: 'open', child_tasks: [], child_epics: [], parent_epic: 'epic-1' }
  ]
  const tasks: Task[] = [
    { id: 'TM-1', title: 'Task1', status: 'todo' },
    { id: 'TM-2', title: 'Task2', status: 'done' }
  ]
  render(<TaskEpicInfo taskId="TM-1" epics={epics} tasks={tasks} />)
  expect(screen.getByText('epic-1')).toBeInTheDocument()
  expect(screen.getByText(/Task2/)).toBeInTheDocument()
  expect(screen.getByText('epic-2')).toBeInTheDocument()
})
