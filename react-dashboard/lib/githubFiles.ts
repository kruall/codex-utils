import { safeGitHubCall } from './githubClient'

export async function createOrUpdateFile(
  repo: string,
  path: string,
  content: string,
  message: string,
  token?: string
): Promise<boolean> {
  const [owner, repoName] = repo.split('/')
  if (!owner || !repoName) {
    throw new Error('Invalid repo format; expected owner/repo')
  }
  const encoded = Buffer.from(content).toString('base64')
  const call = async (client: any) => {
    let sha: string | undefined
    try {
      const { data } = await client.repos.getContent({ owner, repo: repoName, path })
      if (typeof data === 'object' && 'sha' in data) {
        sha = (data as { sha: string }).sha
      }
    } catch (_) {
      /* ignore */
    }
    return client.repos.createOrUpdateFileContents({ owner, repo: repoName, path, message, content: encoded, sha })
  }
  const result = await safeGitHubCall(call, token)
  return result !== null
}

export async function deleteFile(
  repo: string,
  path: string,
  message: string,
  token?: string
): Promise<boolean> {
  const [owner, repoName] = repo.split('/')
  if (!owner || !repoName) {
    throw new Error('Invalid repo format; expected owner/repo')
  }
  const call = async (client: any) => {
    try {
      const { data } = await client.repos.getContent({ owner, repo: repoName, path })
      const sha = (data as any).sha
      return client.repos.deleteFile({ owner, repo: repoName, path, message, sha })
    } catch (_) {
      return null
    }
  }
  const result = await safeGitHubCall(call, token)
  return result !== null
}
