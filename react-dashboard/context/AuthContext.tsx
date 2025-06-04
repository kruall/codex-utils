import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'

export interface AuthContextType {
  token: string | null
  csrfToken: string | null
  login: () => void
  logout: () => void
  refreshToken: () => void
}

const AuthContext = createContext<AuthContextType>({
  token: null,
  csrfToken: null,
  login: () => {},
  logout: () => {},
  refreshToken: () => {}
})

interface AuthProviderProps {
  children: ReactNode
}

const EXPIRY_MS = 60 * 60 * 1000 // 1 hour

export function AuthProvider({ children }: AuthProviderProps) {
  const [token, setToken] = useState<string | null>(null)
  const [csrfToken, setCsrfToken] = useState<string | null>(null)

  useEffect(() => {
    const storedRaw = typeof window !== 'undefined' ? sessionStorage.getItem('githubToken') : null
    const expiry = typeof window !== 'undefined' ? Number(sessionStorage.getItem('githubTokenExpiry')) : 0
    const csrf = typeof window !== 'undefined' ? sessionStorage.getItem('csrfToken') : null
    const stored = storedRaw && expiry > Date.now() ? storedRaw : null
    if (stored) {
      setToken(stored)
      if (csrf) {
        setCsrfToken(csrf)
        document.cookie = `csrfToken=${csrf}; path=/`
      }
    } else {
      sessionStorage.removeItem('githubToken')
      sessionStorage.removeItem('githubTokenExpiry')
    }

    // Check for OAuth callback with code parameter
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search)
      const code = urlParams.get('code')
      
      if (code && !stored) {
        // For static sites, we can't exchange the code for a token directly
        // Instead, we'll show instructions to the user
        alert('GitHub OAuth callback received. For static sites, you need to manually create a Personal Access Token.\n\nGo to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic) > Generate new token\n\nSelect "repo" scope and copy the token.')
        
        // Clear the code from URL
        window.history.replaceState({}, document.title, window.location.pathname)
      }
    }
    const interval = setInterval(() => {
      const expiryTime = Number(sessionStorage.getItem('githubTokenExpiry'))
      if (expiryTime && expiryTime <= Date.now()) {
        logout()
      }
    }, 60000)

    return () => clearInterval(interval)
  }, [])

  const login = (): void => {
    const clientId = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID
    if (!clientId) {
      alert('GitHub OAuth client ID not configured')
      return
    }

    // For static sites, we'll provide two options:
    // 1. OAuth flow (which will require manual token creation)
    // 2. Direct Personal Access Token input
    
    const usePersonalToken = confirm(
      'Choose authentication method:\n\n' +
      'OK = Use Personal Access Token (recommended for static sites)\n' +
      'Cancel = Use OAuth flow (requires manual token creation)\n\n' +
      'Personal Access Token is easier and more secure for static sites.'
    )

    if (usePersonalToken) {
      const token = prompt(
        'Enter your GitHub Personal Access Token:\n\n' +
        '1. Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)\n' +
        '2. Click "Generate new token (classic)"\n' +
        '3. Select "repo" scope\n' +
        '4. Copy and paste the token here:'
      )
      
      if (token && token.trim()) {
        const clean = token.trim()
        const expiry = Date.now() + EXPIRY_MS
        const csrf = (crypto as any).randomUUID ? (crypto as any).randomUUID() : Math.random().toString(36).slice(2)
        sessionStorage.setItem('githubToken', clean)
        sessionStorage.setItem('githubTokenExpiry', expiry.toString())
        sessionStorage.setItem('csrfToken', csrf)
        document.cookie = `csrfToken=${csrf}; path=/`
        setCsrfToken(csrf)
        setToken(clean)
        alert('Successfully logged in!')
      }
    } else {
      // Redirect to GitHub OAuth
      const redirectUri = window.location.origin + window.location.pathname
      const scope = 'repo'
      const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${scope}`

      window.location.href = githubAuthUrl
    }
  }

  const logout = (): void => {
    sessionStorage.removeItem('githubToken')
    sessionStorage.removeItem('githubTokenExpiry')
    sessionStorage.removeItem('csrfToken')
    document.cookie = 'csrfToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT'
    setToken(null)
    setCsrfToken(null)
  }

  const refreshToken = (): void => {
    logout()
    login()
  }

  return (
    <AuthContext.Provider value={{ token, csrfToken, login, logout, refreshToken }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  return useContext(AuthContext)
}
