import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from './AuthContext'

describe('AuthProvider', () => {
  function Wrapper() {
    const { token, login, logout } = useAuth()
    return (
      <div>
        <span data-testid="token">{token ?? ''}</span>
        <button onClick={login}>login</button>
        <button onClick={logout}>logout</button>
      </div>
    )
  }

  beforeEach(() => {
    localStorage.clear()
    jest.spyOn(window, 'alert').mockImplementation(() => {})
    Object.defineProperty(window, 'confirm', { value: jest.fn(() => true), writable: true })
    Object.defineProperty(window, 'prompt', { value: jest.fn(() => 'pat'), writable: true })
    process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID = 'cid'
  })

  afterEach(() => {
    jest.restoreAllMocks()
    localStorage.clear()
    delete (window as any).confirm
    delete (window as any).prompt
    delete process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID
  })

  test('loads token from storage', async () => {
    localStorage.setItem('githubToken', 'abc')
    localStorage.setItem('githubTokenExpiry', String(Date.now() + 5000))
    localStorage.setItem('csrfToken', 'csrf')
    render(
      <AuthProvider>
        <Wrapper />
      </AuthProvider>
    )
    await waitFor(() => expect(screen.getByTestId('token')).toHaveTextContent('abc'))
  })

  test('login stores token and csrf token', async () => {
    render(
      <AuthProvider>
        <Wrapper />
      </AuthProvider>
    )
    fireEvent.click(screen.getByText('login'))
    expect(localStorage.getItem('githubToken')).toBe('pat')
    expect(localStorage.getItem('csrfToken')).not.toBeNull()
    await waitFor(() => expect(screen.getByTestId('token')).toHaveTextContent('pat'))
  })

  test('logout clears token from storage', async () => {
    localStorage.setItem('githubToken', 'abc')
    localStorage.setItem('githubTokenExpiry', String(Date.now() + 5000))
    localStorage.setItem('csrfToken', 'csrf')
    render(
      <AuthProvider>
        <Wrapper />
      </AuthProvider>
    )
    await waitFor(() => expect(screen.getByTestId('token')).toHaveTextContent('abc'))
    fireEvent.click(screen.getByText('logout'))
    await waitFor(() => expect(screen.getByTestId('token')).toHaveTextContent(''))
    expect(localStorage.getItem('githubToken')).toBeNull()
  })
})
