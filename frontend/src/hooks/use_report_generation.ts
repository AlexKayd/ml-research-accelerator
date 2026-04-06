import { useCallback } from 'react'
import { generateReport, getReportStatus } from '../api/eda_service'
import { useReportSse } from '../app/ReportSseContext'

const DEFAULT_TIMEOUT_MS = 30 * 60 * 1000
const POLL_INTERVAL_MS = 2000

type GenerationResult =
  | { ok: true; reportUrl: string }
  | { ok: false; error: string }

function errText(e: unknown): string {
  if (e instanceof Error && e.message.trim()) return e.message
  return 'Не удалось запустить или дождаться отчёта'
}

export function useReportGeneration() {
  const { subscribe } = useReportSse()

  const startGeneration = useCallback(
    async (fileId: number, timeoutMs = DEFAULT_TIMEOUT_MS): Promise<GenerationResult> => {
      let gen: Awaited<ReturnType<typeof generateReport>>
      try {
        gen = await generateReport(fileId)
      } catch (e) {
        return { ok: false, error: errText(e) }
      }

      if (gen.status === 'completed' && gen.report_url) {
        return { ok: true, reportUrl: gen.report_url }
      }
      if (gen.status === 'failed') {
        return { ok: false, error: gen.error_message ?? 'Генерация завершилась с ошибкой' }
      }

      const reportId = gen.report_id

      try {
        return await new Promise<GenerationResult>((resolve) => {
          let settled = false
          let unsub: (() => void) | null = null
          const poll = { id: undefined as number | undefined }

          const done = (r: GenerationResult) => {
            if (settled) return
            settled = true
            clearTimeout(timeout)
            if (poll.id !== undefined) window.clearInterval(poll.id)
            unsub?.()
            resolve(r)
          }

          const timeout = window.setTimeout(() => {
            done({ ok: false, error: 'Превышено время ожидания готовности отчёта' })
          }, timeoutMs)

          const tryPoll = async () => {
            if (settled) return
            try {
              const s = await getReportStatus(reportId)
              if (s.status === 'completed' && s.report_url) {
                done({ ok: true, reportUrl: s.report_url })
                return
              }
              if (s.status === 'failed') {
                done({ ok: false, error: s.error_message ?? 'Генерация завершилась с ошибкой' })
              }
            } catch {
            }
          }

          unsub = subscribe(reportId, (ev) => {
            if (ev.report_id !== reportId) return
            if (ev.event === 'report_ready') {
              done({ ok: true, reportUrl: ev.report_url })
            }
            if (ev.event === 'report_failed') {
              done({ ok: false, error: ev.error_message })
            }
          })

          void tryPoll()
          poll.id = window.setInterval(() => void tryPoll(), POLL_INTERVAL_MS)
        })
      } catch (e) {
        return { ok: false, error: errText(e) }
      }
    },
    [subscribe],
  )

  return { startGeneration }
}