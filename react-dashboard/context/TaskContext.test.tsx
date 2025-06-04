import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { TaskProvider, useTaskContext } from './TaskContext'
import { AuthProvider } from './AuthContext'

function CountTasks() {
  const { tasks } = useTaskContext()
  return <div data-testid="count">{tasks.length}</div>
}

describe('TaskProvider', () => {
  beforeEach(() => {
    ;(global as any).fetch = jest.fn(async () => ({
      json: async () => [{ id: 'T1', title: 't', status: 'todo' }]
    }))
  })

  afterEach(() => {
    ;(global as any).fetch = undefined
    jest.restoreAllMocks()
  })

  test('loads tasks from tasks.json', async () => {
    render(
      <AuthProvider>
        <TaskProvider>
          <CountTasks />
        </TaskProvider>
      </AuthProvider>
    )
    await waitFor(() => expect(screen.getByTestId('count')).toHaveTextContent('1'))
  })
})
