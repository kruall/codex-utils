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

  const rootUrl = `https://api.github.com/repos/${repo}/contents/.tasks`;
  const rootItems = await fetchDir(rootUrl);
  
  const rootTasks = await Promise.all(
    rootItems.map(async (item) => {
      if (item.type === 'file' && item.name.endsWith('.json')) {
        return fetchFile(item.download_url);
      } else if (item.type === 'dir') {
        const subItems = await fetchDir(item.url);
        const subTasks = await Promise.all(
          subItems
            .filter((sub) => sub.type === 'file' && sub.name.endsWith('.json'))
            .map((sub) => fetchFile(sub.download_url))
        );
        return subTasks;
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
