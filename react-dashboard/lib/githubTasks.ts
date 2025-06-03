export interface GitHubContentItem {
  name: string;
  path: string;
  type: 'file' | 'dir';
  download_url?: string;
  url?: string;
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

  const tasks: any[] = [];
  const rootUrl = `https://api.github.com/repos/${repo}/contents/.tasks`;
  const rootItems = await fetchDir(rootUrl);
  for (const item of rootItems) {
    if (item.type === 'file' && item.name.endsWith('.json')) {
      const data = await fetchFile(item.download_url);
      tasks.push(data);
    } else if (item.type === 'dir') {
      const subItems = await fetchDir(item.url);
      for (const sub of subItems) {
        if (sub.type === 'file' && sub.name.endsWith('.json')) {
          const data = await fetchFile(sub.download_url);
          tasks.push(data);
        }
      }
    }
  }

  return tasks;
}

export async function fetchTasksFromRepos(repos: string[], token?: string): Promise<any[]> {
  const all: any[] = [];
  for (const repo of repos) {
    try {
      const tasks = await fetchTasksFromRepo(repo, token);
      all.push(...tasks);
    } catch (err) {
      console.error('Failed to fetch tasks for repo', repo, err);
    }
  }
  return all;
}
