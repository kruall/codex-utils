import React from 'react'
import Link from 'next/link'
import styles from './Navigation.module.css'

export default function Navigation() {
  return (
    <nav className={styles.nav}>
      <div className={styles.links}>
        <Link href="/" className={styles.link}>
          🏠 Home
        </Link>
        <Link href="/table" className={styles.link}>
          📋 Task List
        </Link>
      </div>
    </nav>
  )
} 
