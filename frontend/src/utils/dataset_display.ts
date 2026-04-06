function dropDupParagraphs(s: string): string {
  const paras = s
    .split(/\n\s*\n/)
    .map((x) => x.trim())
    .filter(Boolean)
  const out: string[] = []
  for (const p of paras) {
    if (out.length && out[out.length - 1] === p) continue
    out.push(p)
  }
  return out.join('\n\n')
}

function halfIfDoubled(s: string): string {
  const t = s.trim()
  if (t.length < 8 || t.length % 2 !== 0) return t
  const h = t.length / 2
  return t.slice(0, h) === t.slice(h) ? t.slice(0, h).trim() : t
}

function norm(s: string): string {
  return s.replace(/\s+/g, ' ').trim().toLowerCase()
}

export function formatDatasetDescription(title: string, description: string | null | undefined): string {
  if (description == null) return '—'
  let d = description.trim()
  if (!d) return '—'

  d = halfIfDoubled(d)
  d = dropDupParagraphs(d)

  const ttl = title.trim()
  if (ttl) {
    const nTitle = norm(ttl)
    if (norm(d) === nTitle) return '—'

    for (let i = 0; i < 3; i++) {
      if (!d.toLowerCase().startsWith(ttl.toLowerCase())) break
      let rest = d.slice(ttl.length).trim()
      rest = rest.replace(/^[\s:.\-–—|]+/, '').trim()
      if (!rest || norm(rest) === nTitle) return '—'
      d = rest
    }
  }

  d = dropDupParagraphs(d)
  d = halfIfDoubled(d)

  return d.trim() || '—'
}