export interface GitHubContentItem {
  name: string
  path: string
  type: 'file' | 'dir'
  download_url?: string
  url?: string
}

export async function fetchEpicsFromRepo(repo: string, token?: string): Promise<any[]> {
  function makeHeaders(raw = false): Record<string, string> {
    const headers: Record<string, string> = {
      Accept: raw ? 'application/vnd.github.v3.raw' : 'application/vnd.github.v3+json',
    }
    if (token) {
      headers.Authorization = `token ${token}`
    }
    return headers
  }

  async function fetchJson(url: string, raw = false): Promise<any> {
    const res = await fetch(url, { headers: makeHeaders(raw) })
    if (!res.ok) {
      throw new Error(`Failed to fetch ${url}`)
    }
    return res.json()
  }

  async function fetchFile(apiUrl: string): Promise<any> {
    // Use the GitHub API content endpoint instead of download_url to avoid CORS
    const response = await fetchJson(apiUrl);
    if (response.content && response.encoding === 'base64') {
      // Decode base64 content
      const decoded = atob(response.content.replace(/\s/g, ''));
      return JSON.parse(decoded);
    }
    throw new Error('Invalid file content format');
  }

  const rootUrl = `https://api.github.com/repos/${repo}/contents/.epics`
  const items: GitHubContentItem[] = await fetchJson(rootUrl)
  const epics = await Promise.all(
    items.map(item => {
      if (item.type === 'file' && item.url && item.name.endsWith('.json')) {
        return fetchFile(item.url)
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

