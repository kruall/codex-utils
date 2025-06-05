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
      { name: 'epic-1.json', type: 'file', download_url: 'file-url' }
    ]
    const epicData = { id: 'epic-1', title: 'Demo', status: 'open' as const, child_tasks: [], child_epics: [] }

    global.fetch = jest.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => dirListing })
      .mockResolvedValueOnce({ ok: true, json: async () => epicData })

    const epics = await fetchEpicsFromRepo('owner/repo', 'tkn')
    expect(epics).toEqual([epicData])
    expect((global.fetch as jest.Mock).mock.calls[0][0]).toContain('owner/repo')
  })
})
