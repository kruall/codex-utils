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
          📊 Dashboard
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