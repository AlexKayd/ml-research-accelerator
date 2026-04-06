import { edaApiFetch } from './client'
import { parseApiError } from '../utils/errors'
import type { GenerateReportResponse } from '../types/api'

export class EdaServiceError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.name = 'EdaServiceError'
    this.status = status
  }
}

async function readJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    throw new EdaServiceError(res.status, await parseApiError(res))
  }
  return res.json() as T
}

export async function generateReport(fileId: number) {
  const res = await edaApiFetch('/api/reports/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_id: fileId }),
  })
  return readJson<GenerateReportResponse>(res)
}

export async function getReportStatus(reportId: number) {
  const res = await edaApiFetch(`/api/reports/status/${reportId}`, { method: 'GET' })
  return readJson<GenerateReportResponse>(res)
}