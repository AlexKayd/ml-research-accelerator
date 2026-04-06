import { userApiFetch } from './client'
import { parseApiError } from '../utils/errors'
import type {
  DatasetNonDataFiles,
  DatasetWithFiles,
  TokenResponse,
  UserResponse,
  UserReportListItem,
} from '../types/api'

export class UserServiceError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.name = 'UserServiceError'
    this.status = status
  }
}

function toQuery(obj: Record<string, string | number | string[] | undefined | null>) {
  const sp = new URLSearchParams()
  for (const [k, v] of Object.entries(obj)) {
    if (v === undefined || v === null || v === '') continue
    if (Array.isArray(v)) {
      for (const x of v) sp.append(k, x)
    } else {
      sp.set(k, String(v))
    }
  }
  return sp
}

async function needOk(res: Response) {
  if (!res.ok) {
    throw new UserServiceError(res.status, await parseApiError(res))
  }
}

async function readJson<T>(res: Response): Promise<T> {
  await needOk(res)
  return res.json() as T
}

export async function registerUser(login: string, password: string) {
  const res = await userApiFetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ login, password }),
  })
  await needOk(res)
}

export async function loginUser(login: string, password: string) {
  const res = await userApiFetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ login, password }),
  })
  return readJson<TokenResponse>(res)
}

export async function getProfile() {
  const res = await userApiFetch('/api/users/me')
  return readJson<UserResponse>(res)
}

export async function searchDatasets(p: {
  query?: string
  sources?: string[]
  file_formats?: string[]
  max_size_mb?: number
  tags?: string[]
  limit?: number
  offset?: number
}) {
  const sp = toQuery({
    query: p.query,
    sources: p.sources,
    file_formats: p.file_formats,
    max_size_mb: p.max_size_mb,
    tags: p.tags,
    limit: p.limit,
    offset: p.offset ?? 0,
  })
  const q = sp.toString()
  const res = await userApiFetch(`/api/datasets${q ? `?${q}` : ''}`)
  return readJson<DatasetWithFiles[]>(res)
}

export async function getDatasetNonDataFiles(datasetId: number) {
  const res = await userApiFetch(`/api/datasets/${datasetId}`)
  return readJson<DatasetNonDataFiles>(res)
}

export async function addFavorite(datasetId: number) {
  const res = await userApiFetch('/api/users/favorites/' + datasetId, { method: 'POST' })
  await needOk(res)
}

export async function listFavorites() {
  const res = await userApiFetch('/api/users/favorites')
  return readJson<DatasetWithFiles[]>(res)
}

export async function removeFavorite(datasetId: number) {
  const res = await userApiFetch(`/api/users/favorites/${datasetId}`, { method: 'DELETE' })
  await needOk(res)
}

export async function listReports() {
  const res = await userApiFetch('/api/users/reports')
  return readJson<UserReportListItem[]>(res)
}

export async function deleteReport(reportId: number) {
  const res = await userApiFetch(`/api/users/reports/${reportId}`, { method: 'DELETE' })
  await needOk(res)
}