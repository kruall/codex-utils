import React from 'react'
import Link from 'next/link'
import styles from './Navigation.module.css'
import { useAuth } from '../context/AuthContext'

export default function Navigation() {
  const { token, logout } = useAuth()
  return (
    <nav className={styles.nav}>
      <div className={styles.links}>
        <Link href="/" className={styles.link}>
          🏠 Home
        </Link>
        <Link href="/table" className={styles.link}>
          📋 Task List
        </Link>
        <Link href="/task/new" className={styles.link}>
          ➕ New Task
        </Link>
        <Link href="/epics" className={styles.link}>
          📂 Epics
        </Link>
        <Link href="/repos" className={styles.link}>
          📦 Repos
        </Link>
        <Link href="/workflows" className={styles.link}>
          🚀 Workflows
        </Link>
        {token ? (
          <button onClick={logout} className={styles.button}>
            🔒 Logout
          </button>
        ) : (
          <Link href="/login" className={styles.link}>
            🔑 Login
          </Link>
        )}
      </div>
    </nav>
  )
}
