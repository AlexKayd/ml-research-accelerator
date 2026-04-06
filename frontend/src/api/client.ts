import { USER_SERVICE_URL, EDA_SERVICE_URL } from './config'
import type { TokenResponse } from '../types/api'

type Cfg = {
  getAccessToken: () => string | null
  getRefreshToken: () => string | null
  setTokens: (access: string, refresh: string) => void
  onClearSession: () => void
}

let cfg: Cfg | null = null
let refreshing: Promise<boolean> | null = null

export function configureApiClient(next: Cfg) {
  cfg = next
}

async function tryRefresh(): Promise<boolean> {
  if (!cfg) return false
  const rt = cfg.getRefreshToken()
  if (!rt) return false
  try {
    const res = await fetch(`${USER_SERVICE_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ refresh_token: rt }),
    })
    if (!res.ok) return false
    const data = (await res.json()) as TokenResponse
    cfg.setTokens(data.access_token, data.refresh_token)
    return true
  } catch {
    return false
  }
}

async function refreshOnce(): Promise<boolean> {
  if (refreshing) return refreshing
  refreshing = tryRefresh().finally(() => {
    refreshing = null
  })
  return refreshing
}

async function request(
  base: string,
  path: string,
  init: RequestInit | undefined,
  alreadyRetried: boolean,
): Promise<Response> {
  if (!cfg) throw new Error('API client не сконфигурирован')
  const url = `${base}${path}`
  const h = new Headers(init?.headers)
  const t = cfg.getAccessToken()
  if (t) h.set('Authorization', `Bearer ${t}`)
  if (!h.has('Accept')) h.set('Accept', 'application/json')

  const res = await fetch(url, { ...init, headers: h })

  if (res.status === 401 && !alreadyRetried) {
    const ok = await refreshOnce()
    if (ok) return request(base, path, init, true)
    cfg.onClearSession()
  }
  return res
}

export function userApiFetch(path: string, init?: RequestInit) {
  return request(USER_SERVICE_URL, path, init, false)
}

export function edaApiFetch(path: string, init?: RequestInit) {
  return request(EDA_SERVICE_URL, path, init, false)
}