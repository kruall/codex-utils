import { dispatchWorkflow } from './githubActions'
import { safeGitHubCall } from './githubClient'

jest.mock('./githubClient', () => ({
  safeGitHubCall: jest.fn()
}))

describe('dispatchWorkflow', () => {
  test('calls safeGitHubCall with correct parameters', async () => {
    const result = await dispatchWorkflow('owner/repo', 'build.yml', 'main', {foo: 'bar'}, 'tkn')
    expect(result).toBe(true)
    const callArgs = (safeGitHubCall as unknown as jest.Mock).mock.calls[0]
    expect(typeof callArgs[0]).toBe('function')
    expect(callArgs[1]).toBe('tkn')
  })

  test('returns false when safeGitHubCall fails', async () => {
    ;(safeGitHubCall as unknown as jest.Mock).mockResolvedValueOnce(null)
    const ok = await dispatchWorkflow('owner/repo', 'build.yml')
    expect(ok).toBe(false)
  })

  test('throws error for invalid repo string', async () => {
    await expect(dispatchWorkflow('badrepo', 'build.yml')).rejects.toThrow()
  })
})

