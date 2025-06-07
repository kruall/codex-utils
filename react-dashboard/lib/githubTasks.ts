import { safeGitHubCall } from './githubClient'

export interface GitHubContentItem {
  name: string;
  path: string;
  type: 'file' | 'dir';
  download_url?: string;
  url?: string;
}

// Helper function to generate task file path
export function generateTaskPath(taskId: string): string {
  return `.tasks/${taskId.includes('-') ? taskId.split('-')[0] : 'default'}/${taskId}.json`
}

export async function fetchTasksFromRepo(repo: string, token?: string): Promise<any[]> {
  function makeHeaders(raw = false): Record<string, string> {
    const h: Record<string, string> = {
      Accept: raw ? 'application/vnd.github.v3.raw' : 'application/vnd.github.v3+json'
    }
    if (token) {
      h.Authorization = `token ${token}`
    }
    return h
  }

  async function fetchJson(url: string, raw = false): Promise<any> {
    const res = await fetch(url, { headers: makeHeaders(raw) });
    if (!res.ok) {
      if (res.status === 404) {
        throw new Error(`Repository or .tasks directory not found: ${url}`)
      } else if (res.status === 401) {
        throw new Error(`Authentication failed. Please check your GitHub token: ${url}`)
      } else if (res.status === 403) {
        throw new Error(`Access forbidden. Check repository permissions or rate limits: ${url}`)
      } else {
        throw new Error(`Failed to fetch ${url} (${res.status}: ${res.statusText})`)
      }
    }
    return res.json();
  }

  async function fetchDir(url: string): Promise<GitHubContentItem[]> {
    return fetchJson(url);
  }

  async function fetchFile(apiUrl: string): Promise<any> {
    try {
      // Use the GitHub API content endpoint instead of download_url to avoid CORS
      const response = await fetchJson(apiUrl);
      if (response.content && response.encoding === 'base64') {
        // Decode base64 content
        const decoded = atob(response.content.replace(/\s/g, ''));
        return JSON.parse(decoded);
      }
      throw new Error('Invalid file content format');
    } catch (err) {
      console.warn(`Failed to fetch file ${apiUrl}:`, err);
      return null;
    }
  }

  try {
    const rootUrl = `https://api.github.com/repos/${repo}/contents/.tasks`;
    const rootItems = await fetchDir(rootUrl);
    
    const rootTasks = await Promise.all(
      rootItems.map(async (item) => {
        if (item.type === 'file' && item.name.endsWith('.json')) {
          if (!item.url) {
            console.warn(`No API url for file ${item.name}`);
            return null;
          }
          return fetchFile(item.url);
        } else if (item.type === 'dir') {
          if (!item.url) {
            console.warn(`No url for directory ${item.name}`);
            return null;
          }
          try {
            const subItems = await fetchDir(item.url);
            const subTasks = await Promise.all(
              subItems
                .filter((sub) => sub.type === 'file' && sub.name.endsWith('.json'))
                .map((sub) => {
                  if (!sub.url) {
                    console.warn(`No API url for file ${sub.name}`);
                    return null;
                  }
                  return fetchFile(sub.url);
                })
            );
            return subTasks.filter(task => task !== null);
          } catch (err) {
            console.warn(`Failed to fetch directory ${item.name}:`, err);
            return null;
          }
        }
        return null;
      })
    );

    const tasks = rootTasks.flat().filter((task) => task !== null);
    return tasks;
  } catch (err) {
    console.error(`Failed to fetch tasks from repo ${repo}:`, err);
    // Return empty array instead of throwing to allow graceful fallback
    return [];
  }
}

export async function fetchTasksFromRepos(repos: string[], token?: string): Promise<{
  repo: string, tasks?: any[], error?: Error }[]> {
  const results: { repo: string, tasks?: any[], error?: Error }[] = [];
  for (const repo of repos) {
    try {
      const tasks = await fetchTasksFromRepo(repo, token);
      results.push({ repo, tasks });
    } catch (err) {
      console.error('Failed to fetch tasks for repo', repo, err);
      results.push({ repo, error: err as Error });
    }
  }
  return results;
}

export interface NewTask {
  id: string
  title: string
  status: 'todo' | 'in_progress' | 'done'
  description?: string
}

export async function createTaskInRepo(repo: string, task: NewTask, token?: string): Promise<boolean> {
  const [owner, repoName] = repo.split('/')
  if (!owner || !repoName) {
    throw new Error('Invalid repo format; expected owner/repo')
  }

  const path = generateTaskPath(task.id)
  const content = Buffer.from(JSON.stringify(task, null, 2) + '\n').toString('base64')
  const message = `Add task ${task.id}`

  const call = async (client: any) => {
    let sha: string | undefined
    try {
      // Check if file already exists to include its sha for updates
      const { data } = await client.repos.getContent({ owner, repo: repoName, path })
      if (typeof data === 'object' && 'sha' in data) {
        sha = (data as { sha: string }).sha
      }
    } catch (_) {
      // Ignore errors - file likely does not exist
    }

    return client.repos.createOrUpdateFileContents({
      owner,
      repo: repoName,
      path,
      message,
      content,
      sha,
    })
  }

  const result = await safeGitHubCall(call, token)
  return result !== null
}

export async function updateTaskInRepo(repo: string, task: NewTask, token?: string): Promise<boolean> {
  const [owner, repoName] = repo.split('/')
  if (!owner || !repoName) {
    throw new Error('Invalid repo format; expected owner/repo')
  }

  const path = generateTaskPath(task.id)
  const content = Buffer.from(JSON.stringify(task, null, 2) + '\n').toString('base64')
  const message = `Update task ${task.id}`

  const call = async (client: any) => {
    let sha: string | undefined
    try {
      const { data } = await client.repos.getContent({ owner, repo: repoName, path })
      if (typeof data === 'object' && 'sha' in data) {
        sha = (data as { sha: string }).sha
      }
    } catch (_) {
      // File does not exist, cannot update
      return null
    }

    if (!sha) {
      return null
    }

    return client.repos.createOrUpdateFileContents({
      owner,
      repo: repoName,
      path,
      message,
      content,
      sha,
    })
  }

  const result = await safeGitHubCall(call, token)
  return result !== null
}

export interface NewQueue {
  name: string
  title: string
  description: string
}

export function generateQueueMetaPath(name: string): string {
  return `.tasks/${name}/meta.json`
}

export async function createQueueInRepo(repo: string, queue: NewQueue, token?: string): Promise<boolean> {
  const [owner, repoName] = repo.split('/')
  if (!owner || !repoName) {
    throw new Error('Invalid repo format; expected owner/repo')
  }

  const path = generateQueueMetaPath(queue.name)
  const meta = { title: queue.title, description: queue.description }
  const content = Buffer.from(JSON.stringify(meta, null, 2) + '\n').toString('base64')
  const message = `Add queue ${queue.name}`

  const call = async (client: any) => {
    let sha: string | undefined
    try {
      const { data } = await client.repos.getContent({ owner, repo: repoName, path })
      if (typeof data === 'object' && 'sha' in data) {
        sha = (data as { sha: string }).sha
      }
    } catch (_) {
      // Ignore errors - file likely does not exist
    }

    return client.repos.createOrUpdateFileContents({
      owner,
      repo: repoName,
      path,
      message,
      content,
      sha,
    })
  }

  const result = await safeGitHubCall(call, token)
  return result !== null
}

export async function updateQueueInRepo(repo: string, queue: NewQueue, token?: string): Promise<boolean> {
  const [owner, repoName] = repo.split('/')
  if (!owner || !repoName) {
    throw new Error('Invalid repo format; expected owner/repo')
  }

  const path = generateQueueMetaPath(queue.name)
  const meta = { title: queue.title, description: queue.description }
  const content = Buffer.from(JSON.stringify(meta, null, 2) + '\n').toString('base64')
  const message = `Update queue ${queue.name}`

  const call = async (client: any) => {
    let sha: string | undefined
    try {
      const { data } = await client.repos.getContent({ owner, repo: repoName, path })
      if (typeof data === 'object' && 'sha' in data) {
        sha = (data as { sha: string }).sha
      }
    } catch (_) {
      return null
    }

    if (!sha) {
      return null
    }

    return client.repos.createOrUpdateFileContents({
      owner,
      repo: repoName,
      path,
      message,
      content,
      sha,
    })
  }

  const result = await safeGitHubCall(call, token)
  return result !== null
}

export async function deleteQueueInRepo(repo: string, name: string, token?: string): Promise<boolean> {
  const [owner, repoName] = repo.split('/')
  if (!owner || !repoName) {
    throw new Error('Invalid repo format; expected owner/repo')
  }

  const call = async (client: any) => {
    try {
      const { data } = await client.repos.getContent({ owner, repo: repoName, path: `.tasks/${name}` })
      const items = Array.isArray(data) ? data : [data]
      for (const item of items) {
        if (item.type === 'file') {
          await client.repos.deleteFile({
            owner,
            repo: repoName,
            path: item.path,
            message: `Delete ${item.path}`,
            sha: item.sha,
          })
        } else if (item.type === 'dir') {
          const sub = await client.repos.getContent({ owner, repo: repoName, path: item.path })
          const subItems = Array.isArray(sub.data) ? sub.data : [sub.data]
          for (const s of subItems) {
            if (s.type === 'file') {
              await client.repos.deleteFile({
                owner,
                repo: repoName,
                path: s.path,
                message: `Delete ${s.path}`,
                sha: s.sha,
              })
            }
          }
        }
      }
      return true
    } catch (_) {
      return null
    }
  }

  const result = await safeGitHubCall(call, token)
  return result !== null
}
