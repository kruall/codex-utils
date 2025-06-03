import { fetchTasksFromRepo } from './githubTasks';

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
