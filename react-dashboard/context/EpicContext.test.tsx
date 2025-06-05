import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { EpicProvider, useEpicContext } from './EpicContext'
import { AuthProvider } from './AuthContext'
import { RepoProvider } from './RepoContext'
import { fetchEpicsFromRepo } from '../lib/githubEpics'

jest.mock('../lib/githubEpics', () => ({
  fetchEpicsFromRepo: jest.fn()
}))

function CountEpics() {
  const { epics } = useEpicContext()
  return <div data-testid="count">{epics.length}</div>
}

describe('EpicProvider', () => {
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    ;(console.error as jest.Mock).mockRestore()
    jest.resetAllMocks()
    localStorage.clear()
  })

  test('uses cached epics when GitHub fetch fails', async () => {
    ;(fetchEpicsFromRepo as jest.Mock).mockRejectedValueOnce(new Error('fail'))
    localStorage.setItem(
      'cachedEpics',
      JSON.stringify([{ id: 'e1', title: 'x', status: 'open', child_tasks: [], child_epics: [] }])
    )
    localStorage.setItem('selectedRepo', 'owner/repo')
    render(
      <AuthProvider>
        <RepoProvider>
          <EpicProvider>
            <CountEpics />
          </EpicProvider>
        </RepoProvider>
      </AuthProvider>
    )
    await waitFor(() => expect(screen.getByTestId('count')).toHaveTextContent('1'))
    expect(localStorage.getItem('cachedEpics')).not.toBeNull()
  })
})
