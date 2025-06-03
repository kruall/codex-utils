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
  return `.tasks/${taskId.split('-')[0]}/${taskId}.json`
}

export async function fetchTasksFromRepo(repo: string, token?: string): Promise<any[]> {
  const headers: Record<string, string> = {
    Accept: 'application/vnd.github.v3.raw'
  };
  if (token) {
    headers.Authorization = `token ${token}`;
  }

  async function fetchJson(url: string): Promise<any> {
    const res = await fetch(url, { headers });
    if (!res.ok) {
      throw new Error(`Failed to fetch ${url}`);
    }
    return res.json();
  }

  async function fetchDir(url: string): Promise<GitHubContentItem[]> {
    return fetchJson(url);
  }

  async function fetchFile(url: string): Promise<any> {
    return fetchJson(url);
  }

  const rootUrl = `https://api.github.com/repos/${repo}/contents/.tasks`;
  const rootItems = await fetchDir(rootUrl);
  
  const rootTasks = await Promise.all(
    rootItems.map(async (item) => {
      if (item.type === 'file' && item.name.endsWith('.json')) {
        if (!item.download_url) {
          console.warn(`No download_url for file ${item.name}`);
          return null;
        }
        return fetchFile(item.download_url);
      } else if (item.type === 'dir') {
        if (!item.url) {
          console.warn(`No url for directory ${item.name}`);
          return null;
        }
        const subItems = await fetchDir(item.url);
        const subTasks = await Promise.all(
          subItems
            .filter((sub) => sub.type === 'file' && sub.name.endsWith('.json'))
            .map((sub) => {
              if (!sub.download_url) {
                console.warn(`No download_url for file ${sub.name}`);
                return null;
              }
              return fetchFile(sub.download_url);
            })
        );
        return subTasks.filter(task => task !== null);
      }
      return null;
    })
  );

  const tasks = rootTasks.flat().filter((task) => task !== null);
  return tasks;
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
