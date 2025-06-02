import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'

export interface AuthContextType {
  token: string | null
  login: () => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType>({
  token: null,
  login: async () => {},
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
  }, [])

  const login = async (): Promise<void> => {
    const clientId = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID
    if (!clientId) {
      alert('GitHub OAuth client ID not configured')
      return
    }

    const res = await fetch('https://github.com/login/device/code', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ client_id: clientId, scope: 'repo' })
    })
    const data = await res.json()

    alert(`Open ${data.verification_uri} and enter code ${data.user_code}`)

    const start = Date.now()
    while (Date.now() - start < data.expires_in * 1000) {
      await new Promise(r => setTimeout(r, data.interval * 1000))
      const tokenRes = await fetch('https://github.com/login/oauth/access_token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({
          client_id: clientId,
          device_code: data.device_code,
          grant_type: 'urn:ietf:params:oauth:grant-type:device_code'
        })
      })
      const tokenData = await tokenRes.json()
      if (tokenData.error === 'authorization_pending') {
        continue
      }
      if (tokenData.access_token) {
        sessionStorage.setItem('githubToken', tokenData.access_token)
        setToken(tokenData.access_token)
        return
      } else {
        break
      }
    }
    alert('Login failed')
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
