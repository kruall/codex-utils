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
    ;(fetchTasksFromRepos as jest.Mock).mockResolvedValue([])
  })

  afterEach(() => {
    jest.restoreAllMocks()
    localStorage.clear()
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

  test('loads tasks from GitHub API', async () => {
    ;(fetchTasksFromRepos as jest.Mock).mockResolvedValueOnce([
      { repo: 'owner/repo', tasks: [{ id: 'T1', title: 'GitHub task', status: 'todo' }] }
    ])
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
  })
})
