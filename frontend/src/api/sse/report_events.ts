import { EDA_SERVICE_URL } from '../config'
import type { ReportSseEvent } from '../../types/api'

function parseBlock(block: string): ReportSseEvent | null {
  for (const line of block.split('\n')) {
    if (!line.startsWith('data:')) continue
    const raw = line.slice(5).trim()
    if (!raw) continue
    try {
      const o = JSON.parse(raw) as Record<string, unknown>
      if (typeof o.event !== 'string') continue

      const rid = o.report_id
      const reportId =
        typeof rid === 'number' ? rid : typeof rid === 'string' ? Number(rid) : NaN
      if (!Number.isFinite(reportId)) continue

      if (o.event === 'report_ready' && typeof o.report_url === 'string') {
        return { event: 'report_ready', report_id: reportId, report_url: o.report_url }
      }
      if (o.event === 'report_failed') {
        const err = typeof o.error_message === 'string' ? o.error_message : 'неизвестная ошибка'
        return { event: 'report_failed', report_id: reportId, error_message: err }
      }
      if (o.event === 'report_deleting') {
        return { event: 'report_deleting', report_id: reportId }
      }
      if (o.event === 'report_deleted') {
        return { event: 'report_deleted', report_id: reportId }
      }
    } catch {
    }
  }
  return null
}

export async function connectReportEventsStream(
  accessToken: string,
  signal: AbortSignal,
  onEvent: (e: ReportSseEvent) => void,
) {
  const res = await fetch(`${EDA_SERVICE_URL}/api/reports/events`, {
    method: 'GET',
    headers: {
      Accept: 'text/event-stream',
      Authorization: `Bearer ${accessToken}`,
    },
    signal,
  })
  if (!res.ok || !res.body) return

  const reader = res.body.getReader()
  const dec = new TextDecoder()
  let buf = ''

  try {
    while (!signal.aborted) {
      const { done, value } = await reader.read()
      if (done) break
      buf += dec.decode(value, { stream: true })
      const chunks = buf.split('\n\n')
      buf = chunks.pop() ?? ''
      for (const ch of chunks) {
        const ev = parseBlock(ch)
        if (ev) onEvent(ev)
      }
    }
  } catch (e) {
    if (!signal.aborted) console.warn('SSE stream error', e)
  } finally {
    try {
      reader.releaseLock()
    } catch {
    }
  }
}