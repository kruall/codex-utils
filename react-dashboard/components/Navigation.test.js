import React from 'react'
import { render, screen } from '@testing-library/react'
import Navigation from './Navigation'
import { AuthProvider } from '../context/AuthContext'

test('renders navigation links', () => {
  render(<AuthProvider><Navigation /></AuthProvider>)
  expect(screen.getByText(/Home/)).toBeInTheDocument()
  expect(screen.getByText(/Task List/)).toBeInTheDocument()
  expect(screen.getByText(/Repos/)).toBeInTheDocument()
  expect(screen.getByText(/Login/)).toBeInTheDocument()
})
import { fireEvent, waitFor } from '@testing-library/react'

afterEach(() => {
  localStorage.clear()
})

test('shows logout when authenticated and clears session on click', async () => {
  localStorage.setItem('githubToken', 'tok')
  localStorage.setItem('githubTokenExpiry', String(Date.now() + 5000))
  localStorage.setItem('csrfToken', 'c')
  render(<AuthProvider><Navigation /></AuthProvider>)
  await waitFor(() => expect(screen.getByText(/Logout/)).toBeInTheDocument())
  fireEvent.click(screen.getByText(/Logout/))
  await waitFor(() => expect(screen.getByText(/Login/)).toBeInTheDocument())
  expect(localStorage.getItem('githubToken')).toBeNull()
})
