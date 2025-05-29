import React, { useState, useMemo, useEffect } from 'react'
import Link from 'next/link'
import useTasks from '../hooks/useTasks'
import styles from './TaskTable.module.css'


export default function TaskTable({ tasks: tasksProp }) {
  const tasks = tasksProp ?? useTasks()
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
      <div className={styles.filterControls}>
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
          }} className={styles.inline}>
            <option value="all">All</option>
            <option value="todo">Todo</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
        </label>
        <label>
          Status:
          <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className={styles.inline}>
            <option value="">All</option>
            <option value="todo">Todo</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
        </label>
        <label>
          Queue:
          <select value={queueFilter} onChange={e => setQueueFilter(e.target.value)} className={styles.inline}>
            <option value="">All</option>
            {queues.map(q => (
              <option key={q} value={q}>{q}</option>
            ))}
          </select>
        </label>
        <label>
          Search:
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} className={styles.inline} />
        </label>
        <label className={styles.pageSize}>
          Page size:
          <select value={pageSize} onChange={handlePageSizeChange} className={styles.inline}>
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
          </select>
        </label>
      </div>
      <table className={styles.table}>
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
                <Link href={`/task/${task.id}`} className={styles.link}>
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
      <div className={styles.pagination}>
        <button onClick={handlePrev} disabled={page === 0} className={styles.marginRight}>
          Previous
        </button>
        <span className={styles.marginRight}>
          Page {page + 1} of {pageCount}
        </span>
        <button onClick={handleNext} disabled={page >= pageCount - 1}>
          Next
        </button>
      </div>
    </div>
  )
}
