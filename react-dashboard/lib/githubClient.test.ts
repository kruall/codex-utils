import { getGitHubClient, safeGitHubCall } from './githubClient'

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
