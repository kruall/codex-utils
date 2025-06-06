import { createOrUpdateFile, deleteFile } from './githubFiles'
import { safeGitHubCall } from './githubClient'

jest.mock('./githubClient', () => ({
  safeGitHubCall: jest.fn(async () => true)
}))

test('createOrUpdateFile calls safeGitHubCall', async () => {
  const ok = await createOrUpdateFile('a/b', 'path.txt', 'content', 'msg', 't')
  expect(ok).toBe(true)
  expect(safeGitHubCall).toHaveBeenCalled()
})

test('deleteFile calls safeGitHubCall', async () => {
  const ok = await deleteFile('a/b', 'path.txt', 'msg', 't')
  expect(ok).toBe(true)
  expect(safeGitHubCall).toHaveBeenCalled()
})
