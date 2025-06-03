export async function dispatchWorkflow(
  repo: string,
  workflow: string,
  ref: string = 'main',
  inputs?: Record<string, any>,
  token?: string
): Promise<boolean> {
  const [owner, repoName] = repo.split('/', 2);
  if (!owner || !repoName) {
    throw new Error('Invalid repo format; expected owner/repo');
  }

  const call = async (client: any) => {
    return client.actions.createWorkflowDispatch({
      owner,
      repo: repoName,
      workflow_id: workflow,
      ref,
      inputs,
    });
  };

  const { safeGitHubCall } = await import('./githubClient');
  const result = await safeGitHubCall(call, token);
  return result !== null;
}

