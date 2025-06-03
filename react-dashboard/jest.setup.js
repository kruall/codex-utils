import '@testing-library/jest-dom'

// Suppress React deprecation warnings from testing library
const originalError = console.error
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('ReactDOMTestUtils.act') &&
      args[0].includes('deprecated')
    ) {
      return
    }
    originalError.call(console, ...args)
  }
})
