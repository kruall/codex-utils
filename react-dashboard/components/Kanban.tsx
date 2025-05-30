import React from 'react'
import useTasks from '../hooks/useTasks'
import styles from './Kanban.module.css'
import { KanbanColumnProps, Task } from '../types'

function Column({ title, tasks }: KanbanColumnProps) {
  return (
    <div className={styles.column}>
      <h3>{title}</h3>
      <ul className={styles.list}>
        {tasks.map((t: Task) => (
          <li key={t.id} className={styles.item}>
            {t.title}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function Kanban() {
  const tasks = useTasks()
  const columns = {
    todo: tasks.filter((t: Task) => t.status === 'todo'),
    in_progress: tasks.filter((t: Task) => t.status === 'in_progress'),
    done: tasks.filter((t: Task) => t.status === 'done')
  }

  return (
    <div className={styles.container}>
      <Column title="Todo" tasks={columns.todo} />
      <Column title="In Progress" tasks={columns.in_progress} />
      <Column title="Done" tasks={columns.done} />
    </div>
  )
} 