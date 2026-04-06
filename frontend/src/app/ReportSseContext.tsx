import { createContext, useCallback, useContext, useEffect, useRef, type ReactNode } from 'react'
import { connectReportEventsStream } from '../api/sse/report_events'
import { useAuth } from '../auth/AuthContext'
import type { ReportSseEvent } from '../types/api'

type OnEvent = (e: ReportSseEvent) => void

const Ctx = createContext<{ subscribe: (reportId: number, fn: OnEvent) => () => void } | null>(null)

export function ReportSseProvider({ children }: { children: ReactNode }) {
  const { accessToken, isAuthenticated } = useAuth()
  const byReport = useRef<Map<number, Set<OnEvent>>>(new Map())
  const abort = useRef<AbortController | null>(null)

  const subscribe = useCallback((reportId: number, fn: OnEvent) => {
    const m = byReport.current
    let bag = m.get(reportId)
    if (!bag) {
      bag = new Set()
      m.set(reportId, bag)
    }
    bag.add(fn)
    return () => {
      const b = m.get(reportId)
      if (!b) return
      b.delete(fn)
      if (b.size === 0) m.delete(reportId)
    }
  }, [])

  useEffect(() => {
    if (!isAuthenticated || !accessToken) {
      abort.current?.abort()
      abort.current = null
      return
    }

    abort.current?.abort()
    const ac = new AbortController()
    abort.current = ac

    function send(ev: ReportSseEvent) {
      const subs = byReport.current.get(ev.report_id)
      subs?.forEach((fn) => {
        try {
          fn(ev)
        } catch (e) {
          console.warn('SSE listener', e)
        }
      })
    }

    void connectReportEventsStream(accessToken, ac.signal, send)

    return () => {
      ac.abort()
    }
  }, [accessToken, isAuthenticated])

  return <Ctx.Provider value={{ subscribe }}>{children}</Ctx.Provider>
}

export function useReportSse() {
  const x = useContext(Ctx)
  if (!x) throw new Error('useReportSse вне ReportSseProvider')
  return x
}