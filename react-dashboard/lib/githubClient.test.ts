import { getGitHubClient, safeGitHubCall } from './githubClient'

// Mock console.error to prevent console output during tests
const originalConsoleError = console.error

beforeEach(() => {
  console.error = jest.fn()
})

afterEach(() => {
  console.error = originalConsoleError
})

test('getGitHubClient returns null when Octokit is missing', async () => {
  const client = await getGitHubClient('token')
  expect(client).toBeNull()
})

test('safeGitHubCall returns null when Octokit is missing', async () => {
  const result = await safeGitHubCall(async () => {
    return 'ok'
  }, 'token')
  expect(result).toBeNull()
})
