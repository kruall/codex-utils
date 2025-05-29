import React from 'react'

function Column({ title, tasks }) {
  return (
    <div style={{ flex: 1, padding: '0 8px' }}>
      <h3>{title}</h3>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {tasks.map(t => (
          <li key={t.id} style={{ border: '1px solid #ccc', marginBottom: 4, padding: 4 }}>
            {t.title}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function Kanban({ tasks }) {
  const columns = {
    todo: tasks.filter(t => t.status === 'todo'),
    in_progress: tasks.filter(t => t.status === 'in_progress'),
    done: tasks.filter(t => t.status === 'done')
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
      <Column title="Todo" tasks={columns.todo} />
      <Column title="In Progress" tasks={columns.in_progress} />
      <Column title="Done" tasks={columns.done} />
    </div>
  )
}
