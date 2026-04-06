function isObj(x: unknown): x is Record<string, unknown> {
  return typeof x === 'object' && x !== null
}

function trimDot(s: string): string {
  return s.replace(/\.\s*$/, '')
}

function formatBackendError(body: Record<string, unknown>): string | null {
  if (body.status !== 'error') return null
  const parts: string[] = []
  if (typeof body.message === 'string' && body.message.trim()) {
    parts.push(trimDot(body.message.trim()))
  }
  const det = body.details
  if (isObj(det) && Array.isArray(det.errors)) {
    for (const err of det.errors) {
      if (isObj(err) && typeof err.msg === 'string' && err.msg.trim()) {
        parts.push(trimDot(err.msg.trim()))
      }
    }
  }
  if (parts.length === 0) return null
  return parts.join('. ') + '.'
}

function withDot(msg: string): string {
  const t = msg.trim()
  return t.endsWith('.') ? t : t + '.'
}

export async function parseApiError(response: Response): Promise<string> {
  const text = await response.text()
  if (!text) return response.statusText || `Ошибка ${response.status}`

  try {
    const body = JSON.parse(text) as unknown
    if (!isObj(body)) return text

    const fromBackend = formatBackendError(body)
    if (fromBackend != null) return fromBackend

    const detail = body.detail
    if (typeof detail === 'string') return detail

    if (Array.isArray(detail)) {
      const msgs: string[] = []
      for (const item of detail) {
        if (isObj(item) && typeof item.msg === 'string') msgs.push(item.msg)
      }
      if (msgs.length > 0) {
        return msgs.map(trimDot).join('. ') + '.'
      }
    }

    if (detail != null && typeof detail === 'object' && !Array.isArray(detail)) {
      const d = detail as Record<string, unknown>
      if (typeof d.message === 'string' && d.message.trim()) {
        const nested = formatBackendError({ ...d, status: d.status ?? 'error' })
        if (nested) return nested
        return withDot(d.message)
      }
    }

    if (typeof body.message === 'string' && body.message.trim()) {
      return withDot(body.message)
    }

    return text
  } catch {
    return text
  }
}