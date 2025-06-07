export async function getGitHubClient(token?: string) {
  try {
    // Dynamically import to avoid errors when module is not installed
    const mod = await import('@octokit/rest')
    const { Octokit } = mod as { Octokit: new (options: any) => any }
    return new Octokit({ auth: token })
  } catch (err) {
    console.error('Failed to initialize GitHub client. Make sure @octokit/rest is installed:', err)
    return null
  }
}

export async function safeGitHubCall<T>(fn: (client: any) => Promise<T>, token?: string): Promise<T | null> {
  const client = await getGitHubClient(token)
  if (!client) {
    console.warn('GitHub client not available. API calls will be skipped.')
    return null
  }
  try {
    return await fn(client)
  } catch (err: any) {
    if (err?.status === 404) {
      console.error('GitHub API call failed: Resource not found (404)', err)
    } else if (err?.status === 401) {
      console.error('GitHub API call failed: Authentication required (401). Please check your GitHub token.', err)
    } else if (err?.status === 403) {
      console.error('GitHub API call failed: Access forbidden (403). Check repository permissions or rate limits.', err)
    } else {
      console.error('GitHub API call failed:', err)
    }
    return null
  }
}
