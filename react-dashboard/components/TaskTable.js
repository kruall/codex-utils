import React from 'react'

export default function TaskTable({ tasks }) {
  return (
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
        {tasks.map(task => (
          <tr key={task.id}>
            <td>{task.id}</td>
            <td>{task.title}</td>
            <td>{task.status}</td>
            <td>{task.id ? task.id.split('-')[0] : 'N/A'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
