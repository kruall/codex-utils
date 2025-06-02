import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'

export interface AuthContextType {
  token: string | null
  login: () => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType>({
  token: null,
  login: () => {},
  logout: () => {}
})

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    const stored = typeof window !== 'undefined' ? sessionStorage.getItem('githubToken') : null
    if (stored) {
      setToken(stored)
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
        sessionStorage.setItem('githubToken', token.trim())
        setToken(token.trim())
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
    setToken(null)
  }

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  return useContext(AuthContext)
}
