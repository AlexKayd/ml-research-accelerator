export function parseJwtExp(accessToken: string): number | null {
  try {
    const middle = accessToken.split('.')[1]
    if (!middle) return null
    let b64 = middle.replace(/-/g, '+').replace(/_/g, '/')
    while (b64.length % 4) b64 += '='
    const json = atob(b64)
    const p = JSON.parse(json) as { exp?: number }
    return typeof p.exp === 'number' ? p.exp : null
  } catch {
    return null
  }
}