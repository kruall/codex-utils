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
import { fireEvent } from '@testing-library/react'

it('filters tasks by status and search input', () => {
  const tasks: Task[] = [
    { id: 'TM_WEB-1', title: 'Fix bug', status: 'todo' },
    { id: 'TM_WEB-2', title: 'Add feature', status: 'done' },
    { id: 'TM_WEB-3', title: 'Write docs', status: 'todo' }
  ]
  render(<TaskTable tasks={tasks} />)
  fireEvent.change(screen.getByLabelText('Status:'), { target: { value: 'todo' } })
  fireEvent.change(screen.getByLabelText('Search:'), { target: { value: 'docs' } })
  const rows = screen.getAllByRole('row').slice(1)
  expect(rows).toHaveLength(1)
  expect(rows[0]).toHaveTextContent('TM_WEB-3')
})

it('paginates tasks when page size changes', () => {
  const tasks: Task[] = Array.from({ length: 12 }, (_, i) => ({
    id: `TM_WEB-${i + 1}`,
    title: `t${i + 1}`,
    status: 'todo'
  }))
  render(<TaskTable tasks={tasks} />)
  fireEvent.change(screen.getByLabelText('Page size:'), { target: { value: '5' } })
  let rows = screen.getAllByRole('row').slice(1)
  expect(rows[0]).toHaveTextContent('TM_WEB-1')
  fireEvent.click(screen.getByText('Next'))
  rows = screen.getAllByRole('row').slice(1)
  expect(rows[0]).toHaveTextContent('TM_WEB-6')
})
