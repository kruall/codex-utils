import React from 'react'
import { render, screen } from '@testing-library/react'
import Navigation from './Navigation'
import { AuthProvider } from '../context/AuthContext'

test('renders navigation links', () => {
  render(<AuthProvider><Navigation /></AuthProvider>)
  expect(screen.getByText(/Home/)).toBeInTheDocument()
  expect(screen.getByText(/Task List/)).toBeInTheDocument()
  expect(screen.getByText(/Login/)).toBeInTheDocument()
})
