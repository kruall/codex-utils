import { fetchEpicsFromRepo } from './githubEpics'

// Keep reference to original fetch
const originalFetch = global.fetch

afterEach(() => {
  global.fetch = originalFetch
  jest.resetAllMocks()
})

describe('fetchEpicsFromRepo', () => {
  test('retrieves epics from GitHub repository', async () => {
    const dirListing = [
      { name: 'epic-1.json', type: 'file', url: 'file-api-url' }
    ]
    const epicData = { id: 'epic-1', title: 'Demo', status: 'open' as const, child_tasks: [], child_epics: [] }
    const fileApiResponse = { 
      content: Buffer.from(JSON.stringify(epicData)).toString('base64'), 
      encoding: 'base64' 
    };

    global.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => dirListing })
      .mockResolvedValueOnce({ ok: true, json: async () => fileApiResponse })

    const epics = await fetchEpicsFromRepo('owner/repo', 'tkn')
    expect(epics).toEqual([epicData])
    const firstCall = (global.fetch as jest.Mock).mock.calls[0]
    expect(firstCall[0]).toContain('owner/repo')
    expect(firstCall[1].headers.Accept).toBe('application/vnd.github.v3+json')
    const secondCall = (global.fetch as jest.Mock).mock.calls[1]
    expect(secondCall[1].headers.Accept).toBe('application/vnd.github.v3+json')
  })
})
