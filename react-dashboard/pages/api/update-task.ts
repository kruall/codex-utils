import type { NextApiRequest, NextApiResponse } from 'next'
import { updateTaskInRepo, NewTask } from '../../lib/githubTasks'

function setCors(res: NextApiResponse) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-CSRF-Token, Authorization')
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  setCors(res)
  if (req.method === 'OPTIONS') {
    return res.status(200).end()
  }

  const csrfCookie = req.cookies['csrfToken']
  const csrfHeader = req.headers['x-csrf-token']
  if (!csrfCookie || csrfCookie !== csrfHeader) {
    return res.status(403).json({ error: 'CSRF token mismatch' })
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { repo, task } = req.body
  const authHeader = req.headers['authorization']
  const token = authHeader?.toString()?.replace('token ', '')

  if (!repo || !task) {
    return res.status(400).json({ error: 'Invalid request' })
  }
  try {
    const success = await updateTaskInRepo(repo, task as NewTask, token)
    if (!success) {
      return res.status(500).json({ error: 'Failed to update task' })
    }
    return res.status(200).json({ task })
  } catch (err) {
    return res.status(500).json({ error: 'Server error' })
  }
}
