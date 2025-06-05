import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { RepoProvider, useRepo } from './RepoContext'

function ShowRepo() {
  const { repo, setRepo } = useRepo()
  return (
    <div>
      <span data-testid="repo">{repo ?? ''}</span>
      <button onClick={() => setRepo('owner/repo')}>set</button>
      <button onClick={() => setRepo(null)}>clear</button>
    </div>
  )
}

describe('RepoProvider', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  test('loads repo from localStorage', () => {
    localStorage.setItem('selectedRepo', 'o/r')
    render(
      <RepoProvider>
        <ShowRepo />
      </RepoProvider>
    )
    expect(screen.getByTestId('repo')).toHaveTextContent('o/r')
  })

  test('stores repo to localStorage', () => {
    render(
      <RepoProvider>
        <ShowRepo />
      </RepoProvider>
    )
    fireEvent.click(screen.getByText('set'))
    expect(localStorage.getItem('selectedRepo')).toBe('owner/repo')
    fireEvent.click(screen.getByText('clear'))
    expect(localStorage.getItem('selectedRepo')).toBeNull()
  })
})
