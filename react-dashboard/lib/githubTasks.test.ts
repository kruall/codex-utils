import { fetchTasksFromRepo, createTaskInRepo, updateTaskInRepo, createQueueInRepo, updateQueueInRepo, deleteQueueInRepo } from './githubTasks';
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
      { name: 'TM_WEB-1.json', path: '.tasks/TM_WEB/TM_WEB-1.json', type: 'file', url: 'file-api-url' }
    ];
    const fileData = { id: 'TM_WEB-1', title: 'Test', status: 'todo' as const };
    const fileApiResponse = { 
      content: Buffer.from(JSON.stringify(fileData)).toString('base64'), 
      encoding: 'base64' 
    };

    global.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => firstDir })
      .mockResolvedValueOnce({ ok: true, json: async () => secondDir })
      .mockResolvedValueOnce({ ok: true, json: async () => fileApiResponse });

    const tasks = await fetchTasksFromRepo('owner/repo', 'tkn');
    expect(tasks).toEqual([fileData]);
    const call1 = (global.fetch as jest.Mock).mock.calls[0];
    expect(call1[0]).toContain('owner/repo');
    expect(call1[1].headers.Accept).toBe('application/vnd.github.v3+json');
    const call3 = (global.fetch as jest.Mock).mock.calls[2];
    expect(call3[1].headers.Accept).toBe('application/vnd.github.v3+json');
  });

  test('handles base64 decoding correctly', async () => {
    const testData = { id: 'test-1', title: 'Test Task', status: 'todo' as const };
    const base64Content = Buffer.from(JSON.stringify(testData)).toString('base64');
    const apiResponse = {
      content: base64Content,
      encoding: 'base64'
    };

    global.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => [{ name: 'test-1.json', type: 'file', url: 'api-url' }] })
      .mockResolvedValueOnce({ ok: true, json: async () => apiResponse });

    const tasks = await fetchTasksFromRepo('owner/repo', 'token');
    expect(tasks).toEqual([testData]);
  });

  test('handles invalid file content format', async () => {
    const invalidResponse = { content: 'invalid', encoding: 'invalid' };

    global.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => [{ name: 'test-1.json', type: 'file', url: 'api-url' }] })
      .mockResolvedValueOnce({ ok: true, json: async () => invalidResponse });

    await expect(fetchTasksFromRepo('owner/repo', 'token')).rejects.toThrow('Invalid file content format');
  });
});

describe('createTaskInRepo', () => {
  test('calls safeGitHubCall with correct parameters', async () => {
    const task = { id: 'TM_WEB-99', title: 'demo', status: 'todo' as const }

    const result = await createTaskInRepo('owner/repo', task, 'tkn')
    expect(result).toBe(true)
    const callArgs = (safeGitHubCall as unknown as jest.Mock).mock.calls[0]
    expect(typeof callArgs[0]).toBe('function')
    expect(callArgs[1]).toBe('tkn')
  })

  test('returns false when safeGitHubCall fails', async () => {
    ;(safeGitHubCall as unknown as jest.Mock).mockResolvedValueOnce(null)
    const task = { id: 'TM_WEB-1', title: 'demo', status: 'todo' as const }
    const result = await createTaskInRepo('owner/repo', task, 'tkn')
    expect(result).toBe(false)
  })

  test('throws error for invalid repo string', async () => {
    const task = { id: 'TM_WEB-2', title: 'demo', status: 'todo' as const }
    await expect(createTaskInRepo('invalidrepo', task)).rejects.toThrow()
  })
})

describe('updateTaskInRepo', () => {
  test('calls safeGitHubCall with correct parameters', async () => {
    const task = { id: 'TM_WEB-5', title: 'demo', status: 'todo' as const }

    const result = await updateTaskInRepo('owner/repo', task, 'tkn')
    expect(result).toBe(true)
    const callArgs = (safeGitHubCall as unknown as jest.Mock).mock.calls.pop()
    expect(typeof callArgs[0]).toBe('function')
    expect(callArgs[1]).toBe('tkn')
  })

  test('returns false when safeGitHubCall fails', async () => {
    ;(safeGitHubCall as unknown as jest.Mock).mockResolvedValueOnce(null)
    const task = { id: 'TM_WEB-6', title: 'demo', status: 'todo' as const }
    const result = await updateTaskInRepo('owner/repo', task, 'tkn')
    expect(result).toBe(false)
  })

  test('throws error for invalid repo string', async () => {
    const task = { id: 'TM_WEB-7', title: 'demo', status: 'todo' as const }
    await expect(updateTaskInRepo('invalidrepo', task)).rejects.toThrow()
  })
})

describe('createQueueInRepo', () => {
  test('calls safeGitHubCall with correct parameters', async () => {
    const q = { name: 'web', title: 'Web', description: 'desc' }
    const result = await createQueueInRepo('owner/repo', q, 'tkn')
    expect(result).toBe(true)
    const callArgs = (safeGitHubCall as unknown as jest.Mock).mock.calls.pop()
    expect(typeof callArgs[0]).toBe('function')
    expect(callArgs[1]).toBe('tkn')
  })

  test('returns false when safeGitHubCall fails', async () => {
    ;(safeGitHubCall as unknown as jest.Mock).mockResolvedValueOnce(null)
    const q = { name: 'a', title: 'b', description: 'c' }
    const result = await createQueueInRepo('owner/repo', q, 'tkn')
    expect(result).toBe(false)
  })

  test('throws error for invalid repo string', async () => {
    const q = { name: 'x', title: 'y', description: 'z' }
    await expect(createQueueInRepo('invalidrepo', q)).rejects.toThrow()
  })
})

describe('updateQueueInRepo', () => {
  test('calls safeGitHubCall with correct parameters', async () => {
    const q = { name: 'web', title: 'New', description: 'new' }
    const result = await updateQueueInRepo('owner/repo', q, 'tkn')
    expect(result).toBe(true)
    const callArgs = (safeGitHubCall as unknown as jest.Mock).mock.calls.pop()
    expect(typeof callArgs[0]).toBe('function')
    expect(callArgs[1]).toBe('tkn')
  })

  test('returns false when safeGitHubCall fails', async () => {
    ;(safeGitHubCall as unknown as jest.Mock).mockResolvedValueOnce(null)
    const q = { name: 'web', title: 'x', description: 'y' }
    const result = await updateQueueInRepo('owner/repo', q, 'tkn')
    expect(result).toBe(false)
  })

  test('throws error for invalid repo string', async () => {
    const q = { name: 'bad', title: 'c', description: 'd' }
    await expect(updateQueueInRepo('invalidrepo', q)).rejects.toThrow()
  })
})

describe('deleteQueueInRepo', () => {
  test('calls safeGitHubCall with correct parameters', async () => {
    const result = await deleteQueueInRepo('owner/repo', 'web', 'tkn')
    expect(result).toBe(true)
    const callArgs = (safeGitHubCall as unknown as jest.Mock).mock.calls.pop()
    expect(typeof callArgs[0]).toBe('function')
    expect(callArgs[1]).toBe('tkn')
  })

  test('returns false when safeGitHubCall fails', async () => {
    ;(safeGitHubCall as unknown as jest.Mock).mockResolvedValueOnce(null)
    const result = await deleteQueueInRepo('owner/repo', 'web', 'tkn')
    expect(result).toBe(false)
  })

  test('throws error for invalid repo string', async () => {
    await expect(deleteQueueInRepo('invalidrepo', 'web')).rejects.toThrow()
  })
})
