import React from 'react'
import { render, screen } from '@testing-library/react'
import TaskTable from './TaskTable'
import { Task } from '../types'

it('sorts tasks by queue and numeric id', () => {
  const tasks: Task[] = [
    { id: 'TM_WEB-18', title: 'a', status: 'todo' },
    { id: 'TM_WEB-2', title: 'b', status: 'todo' },
    { id: 'TM_TUI-1', title: 'c', status: 'todo' },
    { id: 'TM_WEB-10', title: 'd', status: 'todo' }
  ]

  render(<TaskTable tasks={tasks} />)
  const rows = screen.getAllByRole('row').slice(1) // skip header
  const ids = rows.map(r => r.querySelector('td')?.textContent)
  expect(ids).toEqual(['TM_TUI-1', 'TM_WEB-2', 'TM_WEB-10', 'TM_WEB-18'])
})
