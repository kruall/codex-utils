import React, { useState } from 'react'
import Link from 'next/link'

export default function TaskTable({ tasks }) {
  const [pageSize, setPageSize] = useState(10)
  const [page, setPage] = useState(0)

  const pageCount = Math.ceil(tasks.length / pageSize)
  const start = page * pageSize
  const pagedTasks = tasks.slice(start, start + pageSize)

  const handlePrev = () => setPage(p => Math.max(0, p - 1))
  const handleNext = () => setPage(p => Math.min(pageCount - 1, p + 1))
  const handlePageSizeChange = e => {
    setPageSize(Number(e.target.value))
    setPage(0)
  }

  return (
    <div>
      <div style={{ marginBottom: 8 }}>
        <label>
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
              <td>
                <Link href={`/task/${task.id}`} style={{ color: '#0070f3' }}>
                  {task.id}
                </Link>
              </td>
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
