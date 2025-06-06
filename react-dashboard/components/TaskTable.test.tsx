import React from 'react'
import { render, screen } from '@testing-library/react'
import TaskTable from './TaskTable'
import { Task } from '../types'
import { fireEvent } from '@testing-library/react'

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

it('handles tasks with undefined or null IDs', () => {
  const tasks: Task[] = [
    { id: 'TM_WEB-1', title: 'Valid task', status: 'todo' },
    { id: undefined as any, title: 'Undefined ID', status: 'todo' },
    { id: null as any, title: 'Null ID', status: 'todo' },
    { id: 'TM_WEB-2', title: 'Another valid task', status: 'todo' }
  ]
  
  // Should not throw an error
  expect(() => render(<TaskTable tasks={tasks} />)).not.toThrow()
  
  // Should render all tasks
  const rows = screen.getAllByRole('row').slice(1) // skip header
  expect(rows).toHaveLength(4)
  
  // Tasks with undefined/null IDs should be sorted to the end
  expect(rows[0]).toHaveTextContent('TM_WEB-1')
  expect(rows[1]).toHaveTextContent('TM_WEB-2')
  expect(rows[2]).toHaveTextContent('Undefined ID')
  expect(rows[3]).toHaveTextContent('Null ID')
})
