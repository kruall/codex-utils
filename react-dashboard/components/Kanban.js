import React from 'react'
import styles from './Kanban.module.css'

function Column({ title, tasks }) {
  return (
    <div className={styles.column}>
      <h3>{title}</h3>
      <ul className={styles.list}>
        {tasks.map(t => (
          <li key={t.id} className={styles.item}>
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
    <div className={styles.container}>
      <Column title="Todo" tasks={columns.todo} />
      <Column title="In Progress" tasks={columns.in_progress} />
      <Column title="Done" tasks={columns.done} />
    </div>
  )
}
