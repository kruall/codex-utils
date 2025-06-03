import { fetchTasksFromRepo, createTaskInRepo } from './githubTasks';
import { safeGitHubCall } from './githubClient';

jest.mock('./githubClient', () => ({
  safeGitHubCall: jest.fn()
}))

describe('fetchTasksFromRepo', () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
    jest.resetAllMocks();
  });

  test('retrieves tasks from GitHub repository', async () => {
    const firstDir = [
      { name: 'TM_WEB', path: '.tasks/TM_WEB', type: 'dir', url: 'dir-url' }
    ];
    const secondDir = [
      { name: 'TM_WEB-1.json', path: '.tasks/TM_WEB/TM_WEB-1.json', type: 'file', download_url: 'file-url' }
    ];
    const fileData = { id: 'TM_WEB-1', title: 'Test', status: 'todo' };

    global.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => firstDir })
      .mockResolvedValueOnce({ ok: true, json: async () => secondDir })
      .mockResolvedValueOnce({ ok: true, json: async () => fileData });

    const tasks = await fetchTasksFromRepo('owner/repo', 'tkn');
    expect(tasks).toEqual([fileData]);
    expect((global.fetch as jest.Mock).mock.calls[0][0]).toContain('owner/repo');
  });
});

describe('createTaskInRepo', () => {
  test('calls safeGitHubCall with correct parameters', async () => {
    const task = { id: 'TM_WEB-99', title: 'demo', status: 'todo' }

    const result = await createTaskInRepo('owner/repo', task, 'tkn')
    expect(result).toBe(true)
    const callArgs = (safeGitHubCall as unknown as jest.Mock).mock.calls[0]
    expect(typeof callArgs[0]).toBe('function')
    expect(callArgs[1]).toBe('tkn')
  })

  test('returns false when safeGitHubCall fails', async () => {
    ;(safeGitHubCall as unknown as jest.Mock).mockResolvedValueOnce(null)
    const task = { id: 'TM_WEB-1', title: 'demo', status: 'todo' }
    const result = await createTaskInRepo('owner/repo', task, 'tkn')
    expect(result).toBe(false)
  })

  test('throws error for invalid repo string', async () => {
    const task = { id: 'TM_WEB-2', title: 'demo', status: 'todo' }
    await expect(createTaskInRepo('invalidrepo', task)).rejects.toThrow()
  })
})
