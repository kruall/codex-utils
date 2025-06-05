export interface GitHubContentItem {
  name: string
  path: string
  type: 'file' | 'dir'
  download_url?: string
  url?: string
}

export async function fetchEpicsFromRepo(repo: string, token?: string): Promise<any[]> {
  const headers: Record<string, string> = { Accept: 'application/vnd.github.v3.raw' }
  if (token) {
    headers.Authorization = `token ${token}`
  }

  async function fetchJson(url: string): Promise<any> {
    const res = await fetch(url, { headers })
    if (!res.ok) {
      throw new Error(`Failed to fetch ${url}`)
    }
    return res.json()
  }

  const rootUrl = `https://api.github.com/repos/${repo}/contents/.epics`
  const items: GitHubContentItem[] = await fetchJson(rootUrl)
  const epics = await Promise.all(
    items.map(item => {
      if (item.type === 'file' && item.download_url && item.name.endsWith('.json')) {
        return fetchJson(item.download_url)
      }
      return null
    })
  )
  return epics.filter(e => e !== null)
}

export async function fetchEpicsFromRepos(repos: string[], token?: string): Promise<{ repo: string; epics?: any[]; error?: Error }[]> {
  const results: { repo: string; epics?: any[]; error?: Error }[] = []
  for (const repo of repos) {
    try {
      const epics = await fetchEpicsFromRepo(repo, token)
      results.push({ repo, epics })
    } catch (err) {
      console.error('Failed to fetch epics for repo', repo, err)
      results.push({ repo, error: err as Error })
    }
  }
  return results
}

