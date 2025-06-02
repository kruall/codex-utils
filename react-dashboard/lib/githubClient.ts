export async function getGitHubClient(token?: string) {
  try {
    // Dynamically import to avoid errors when module is not installed
    const mod = await import('@octokit/rest')
    const { Octokit } = mod as { Octokit: new (options: any) => any }
    return new Octokit({ auth: token })
  } catch (err) {
    console.error('Failed to initialize GitHub client', err)
    return null
  }
}

export async function safeGitHubCall<T>(fn: (client: any) => Promise<T>, token?: string): Promise<T | null> {
  const client = await getGitHubClient(token)
  if (!client) return null
  try {
    return await fn(client)
  } catch (err) {
    console.error('GitHub API call failed', err)
    return null
  }
}
