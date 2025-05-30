import React from 'react'
import { render, screen } from '@testing-library/react'
import Navigation from './Navigation'

test('renders navigation links', () => {
  render(<Navigation />)
  expect(screen.getByText(/Home/)).toBeInTheDocument()
  expect(screen.getByText(/Task List/)).toBeInTheDocument()
  expect(screen.getByText(/Kanban Board/)).toBeInTheDocument()
  expect(screen.getByText(/TODO Tasks/)).toBeInTheDocument()
})
