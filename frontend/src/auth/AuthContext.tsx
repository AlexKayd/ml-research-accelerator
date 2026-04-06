import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from 'react'
import { configureApiClient } from '../api/client'
import { USER_SERVICE_URL } from '../api/config'
import type { UserResponse } from '../types/api'
import { parseJwtExp } from '../utils/jwt'

const KEY = 'mlra_refresh_token'

type Ctx = {
  accessToken: string | null
  user: UserResponse | null
  isAuthenticated: boolean
  login: (access: string, refresh: string, user: UserResponse) => void
}

const AuthContext = createContext<Ctx | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null)
  const [user, setUser] = useState<UserResponse | null>(null)
  const accessRef = useRef<string | null>(null)
  const bootDone = useRef(false)

  useEffect(() => {
    accessRef.current = accessToken
  }, [accessToken])

  const refreshAccess = useCallback(async (): Promise<boolean> => {
    const refresh = sessionStorage.getItem(KEY)
    if (!refresh) return false
    try {
      const res = await fetch(`${USER_SERVICE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ refresh_token: refresh }),
      })
      if (!res.ok) return false
      const data = (await res.json()) as {
        access_token: string
        refresh_token: string
        user: UserResponse
      }
      sessionStorage.setItem(KEY, data.refresh_token)
      setAccessToken(data.access_token)
      setUser(data.user)
      return true
    } catch {
      return false
    }
  }, [])

  useEffect(() => {
    configureApiClient({
      getAccessToken: () => accessRef.current,
      getRefreshToken: () => sessionStorage.getItem(KEY),
      setTokens(access, refresh) {
        sessionStorage.setItem(KEY, refresh)
        setAccessToken(access)
      },
      onClearSession() {
        bootDone.current = false
        sessionStorage.removeItem(KEY)
        setAccessToken(null)
        setUser(null)
      },
    })
  }, [])

  useEffect(() => {
    if (bootDone.current) return
    if (!sessionStorage.getItem(KEY)) return
    bootDone.current = true
    void (async () => {
      const ok = await refreshAccess()
      if (!ok) {
        bootDone.current = false
        sessionStorage.removeItem(KEY)
      }
    })()
  }, [refreshAccess])

  useEffect(() => {
    if (!accessToken) return
    const exp = parseJwtExp(accessToken)
    if (exp == null) return
    const ms = exp * 1000 - Date.now() - 90_000
    if (ms < 2000) {
      void refreshAccess()
      return
    }
    const t = window.setTimeout(() => void refreshAccess(), ms)
    return () => window.clearTimeout(t)
  }, [accessToken, refreshAccess])

  useEffect(() => {
    function onTab() {
      if (document.visibilityState !== 'visible') return
      const token = accessRef.current
      if (!token) return
      const exp = parseJwtExp(token)
      if (exp == null) return
      if (exp * 1000 - Date.now() < 120_000) void refreshAccess()
    }
    document.addEventListener('visibilitychange', onTab)
    return () => document.removeEventListener('visibilitychange', onTab)
  }, [refreshAccess])

  function login(access: string, refresh: string, u: UserResponse) {
    sessionStorage.setItem(KEY, refresh)
    setAccessToken(access)
    setUser(u)
  }

  return (
    <AuthContext.Provider
      value={{
        accessToken,
        user,
        isAuthenticated: Boolean(accessToken && user),
        login,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth вне AuthProvider')
  return ctx
}