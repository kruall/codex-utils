import React from 'react'
import Link from 'next/link'

export default function Navigation() {
  return (
    <nav style={{ 
      padding: '16px 0', 
      borderBottom: '1px solid #eee', 
      marginBottom: '16px' 
    }}>
      <div style={{ display: 'flex', gap: '16px' }}>
        <Link href="/" style={{
          color: '#0070f3',
          textDecoration: 'none',
          fontWeight: 'bold'
        }}>
          🏠 Home
        </Link>
        <Link href="/table" style={{
          color: '#0070f3',
          textDecoration: 'none',
          fontWeight: 'bold'
        }}>
          📋 Task List
        </Link>
        <Link href="/kanban" style={{
          color: '#0070f3',
          textDecoration: 'none',
          fontWeight: 'bold'
        }}>
          🗂 Kanban Board
        </Link>
        <Link href="/todo" style={{
          color: '#0070f3',
          textDecoration: 'none',
          fontWeight: 'bold'
        }}>
          ✅ TODO Tasks
        </Link>
      </div>
    </nav>
  )
} 