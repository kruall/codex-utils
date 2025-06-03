import handler from './update-task'
import type { NextApiRequest, NextApiResponse } from 'next'
import { updateTaskInRepo } from '../../lib/githubTasks'

jest.mock('../../lib/githubTasks', () => ({
  updateTaskInRepo: jest.fn(async () => true)
}))

function createRes() {
  const res: any = {}
  res.status = jest.fn().mockReturnValue(res)
  res.json = jest.fn().mockReturnValue(res)
  res.setHeader = jest.fn()
  res.end = jest.fn()
  return res as NextApiResponse
}

test('rejects when csrf token mismatch', async () => {
  const req = {
    method: 'POST',
    body: { repo: 'r', task: {} },
    headers: { 'x-csrf-token': 'bad' },
    cookies: { csrfToken: 'good' }
  } as unknown as NextApiRequest
  const res = createRes()
  await handler(req, res)
  expect(res.status).toHaveBeenCalledWith(403)
})


test('calls updateTaskInRepo when csrf token valid', async () => {
  const req = {
    method: 'POST',
    body: { repo: 'r', task: { id: 't' } },
    headers: { 'x-csrf-token': 'a', authorization: 'token tok' },
    cookies: { csrfToken: 'a' }
  } as unknown as NextApiRequest
  const res = createRes()
  await handler(req, res)
  expect(updateTaskInRepo).toHaveBeenCalled()
  expect(res.status).toHaveBeenCalledWith(200)
})
