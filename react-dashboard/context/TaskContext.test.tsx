import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { TaskProvider, useTaskContext } from './TaskContext'
import { AuthProvider } from './AuthContext'
import { RepoProvider } from './RepoContext'
import { fetchTasksFromRepos } from '../lib/githubTasks'

jest.mock('../lib/githubTasks', () => ({
  fetchTasksFromRepos: jest.fn()
}))

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
    localStorage.clear()
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

  test('uses cached tasks when GitHub fetch fails', async () => {
    ;(fetchTasksFromRepos as jest.Mock).mockResolvedValueOnce([{ repo: 'r', error: new Error('fail') }])
    localStorage.setItem(
      'cachedTasks',
      JSON.stringify([{ id: 'T1', title: 'cached', status: 'todo' }])
    )

    localStorage.setItem('selectedRepo', 'owner/repo')
    render(
      <AuthProvider>
        <RepoProvider>
          <TaskProvider>
            <CountTasks />
          </TaskProvider>
        </RepoProvider>
      </AuthProvider>
    )

    await waitFor(() => expect(screen.getByTestId('count')).toHaveTextContent('1'))
    expect(localStorage.getItem('cachedTasks')).not.toBeNull()
  })

  test('overwrites cache when GitHub fetch succeeds with empty list', async () => {
    ;(fetchTasksFromRepos as jest.Mock).mockResolvedValueOnce([{ repo: 'r', tasks: [] }])
    localStorage.setItem('cachedTasks', JSON.stringify([{ id: 'T1', title: 'cached', status: 'todo' }]))
    localStorage.setItem('selectedRepo', 'owner/repo')
    render(
      <AuthProvider>
        <RepoProvider>
          <TaskProvider>
            <CountTasks />
          </TaskProvider>
        </RepoProvider>
      </AuthProvider>
    )
    await waitFor(() => expect(screen.getByTestId('count')).toHaveTextContent('0'))
    expect(localStorage.getItem('cachedTasks')).toBe('[]')
  })
})
