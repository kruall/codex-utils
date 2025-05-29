import React, { useState, useMemo, useEffect } from 'react'

export default function TaskTable({ tasks }) {
  const [pageSize, setPageSize] = useState(10)
  const [page, setPage] = useState(0)
  const [statusFilter, setStatusFilter] = useState('')
  const [queueFilter, setQueueFilter] = useState('')
  const [search, setSearch] = useState('')

  const queues = useMemo(
    () => Array.from(new Set(tasks.map(t => (t.id || '').split('-')[0]))),
    [tasks]
  )

  const filteredTasks = tasks.filter(t => {
    if (statusFilter && t.status !== statusFilter) return false
    if (queueFilter && !(t.id || '').startsWith(queueFilter + '-')) return false
    if (search && !t.title.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const pageCount = Math.ceil(filteredTasks.length / pageSize)
  const start = page * pageSize
  const pagedTasks = filteredTasks.slice(start, start + pageSize)

  const handlePrev = () => setPage(p => Math.max(0, p - 1))
  const handleNext = () => setPage(p => Math.min(pageCount - 1, p + 1))
  const handlePageSizeChange = e => {
    setPageSize(Number(e.target.value))
    setPage(0)
  }

  useEffect(() => {
    setPage(0)
  }, [statusFilter, queueFilter, search])

  return (
    <div>
      <div style={{ marginBottom: 8, display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
        <label>
          Preset:
          <select onChange={e => {
            const preset = e.target.value
            if (preset === 'todo' || preset === 'in_progress' || preset === 'done') {
              setStatusFilter(preset)
            } else {
              setStatusFilter('')
            }
            setQueueFilter('')
          }} style={{ marginLeft: 4 }}>
            <option value="all">All</option>
            <option value="todo">Todo</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
        </label>
        <label>
          Status:
          <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} style={{ marginLeft: 4 }}>
            <option value="">All</option>
            <option value="todo">Todo</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
        </label>
        <label>
          Queue:
          <select value={queueFilter} onChange={e => setQueueFilter(e.target.value)} style={{ marginLeft: 4 }}>
            <option value="">All</option>
            {queues.map(q => (
              <option key={q} value={q}>{q}</option>
            ))}
          </select>
        </label>
        <label>
          Search:
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} style={{ marginLeft: 4 }} />
        </label>
        <label style={{ marginLeft: 'auto' }}>
          Page size:
          <select value={pageSize} onChange={handlePageSizeChange} style={{ marginLeft: 4 }}>
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
          </select>
        </label>
      </div>
      <table style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Status</th>
            <th>Queue</th>
          </tr>
        </thead>
        <tbody>
          {pagedTasks.map(task => (
            <tr key={task.id}>
              <td>{task.id}</td>
              <td>{task.title}</td>
              <td>{task.status}</td>
              <td>{task.id ? task.id.split('-')[0] : 'N/A'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div style={{ marginTop: 8 }}>
        <button onClick={handlePrev} disabled={page === 0} style={{ marginRight: 8 }}>
          Previous
        </button>
        <span style={{ marginRight: 8 }}>
          Page {page + 1} of {pageCount}
        </span>
        <button onClick={handleNext} disabled={page >= pageCount - 1}>
          Next
        </button>
      </div>
    </div>
  )
}
