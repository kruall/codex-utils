import '@testing-library/jest-dom'
// provide minimal crypto.randomUUID for tests
if (!global.crypto) {
  global.crypto = {
    randomUUID: () => 'test-uuid'
  }
} else if (!global.crypto.randomUUID) {
  global.crypto.randomUUID = () => 'test-uuid'
}

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
