import type { ChangeKind, Point, Series } from './data'

export const RANGES = { '6M': 182, '1Y': 365, '3Y': 1095 } as const
export type Range = keyof typeof RANGES

const DAY = 86_400_000
const time = (d: string) => Date.parse(`${d}T00:00:00Z`)
const shift = (d: string, days: number) => new Date(time(d) - days * DAY).toISOString().slice(0, 10)

export function last(s: Series): Point {
  return s.points[s.points.length - 1]!
}

export interface Change {
  value: number
  kind: ChangeKind
}

function diff(s: Series, from: number, to: number): Change {
  return s.change === 'diff' ? { value: to - from, kind: 'diff' } : { value: (to / from - 1) * 100, kind: 'pct' }
}

/** The latest move is the last point against the one before. For a decision series it is the last decision against the one it replaced. */
export function latestChange(s: Series): Change {
  const p = s.points
  if (s.frequency === 'event') {
    for (let i = p.length - 1; i > 0; i--) {
      if (p[i]![1] !== p[i - 1]![1]) return diff(s, p[i - 1]![1], p[i]![1])
    }
    return { value: 0, kind: s.change }
  }
  return diff(s, p[p.length - 2]![1], p[p.length - 1]![1])
}

/** Points inside the range ending at the last point. A decision series also keeps the value in force at the window start. */
export function windowed(s: Series, range: Range): Point[] {
  const cutoff = shift(last(s)[0], RANGES[range])
  const inside = s.points.filter(([d]) => d >= cutoff)
  if (s.frequency === 'event') {
    const before = s.points.filter(([d]) => d < cutoff).at(-1)
    if (before && inside[0]?.[0] !== cutoff) inside.unshift([cutoff, before[1]])
  }
  return inside.length >= 2 ? inside : s.points.slice(-2)
}

export function sparkPoints(s: Series): Point[] {
  if (s.frequency === 'daily') return s.points.slice(-30)
  if (s.frequency === 'monthly') return s.points.slice(-12)
  return windowed(s, '1Y')
}

export function rangeChange(s: Series, pts: Point[]): Change {
  return diff(s, pts[0]![1], pts[pts.length - 1]![1])
}

export interface Geometry {
  line: string
  area: string
  baseY: number
}

/** SVG coordinates for points placed by date. `stepped` draws a decision series as flat runs between decisions. */
export function geometry(pts: Point[], w: number, h: number, pad: number, stepped: boolean): Geometry {
  const t0 = time(pts[0]![0])
  const span = time(pts[pts.length - 1]![0]) - t0 || 1
  const values = pts.map(([, v]) => v)
  const lo = Math.min(...values)
  const hi = Math.max(...values)
  const k = hi - lo || 1
  const x = (d: string) => pad + ((time(d) - t0) / span) * (w - 2 * pad)
  const y = (v: number) => pad + (h - 2 * pad) * (1 - (v - lo) / k)
  const xy: [number, number][] = []
  pts.forEach(([d, v], i) => {
    if (stepped && i > 0) xy.push([x(d), y(pts[i - 1]![1])])
    xy.push([x(d), y(v)])
  })
  const line = xy.map(([a, b]) => `${a.toFixed(1)},${b.toFixed(1)}`).join(' ')
  const area = `${line} ${xy.at(-1)![0].toFixed(1)},${h} ${xy[0]![0].toFixed(1)},${h}`
  return { line, area, baseY: y(pts[0]![1]) }
}

export function formatValue(s: Series, v: number): string {
  return v.toFixed(s.decimals) + s.unit
}

export function formatChange(c: Change, decimals = 2): string {
  const sign = c.value > 0 ? '+' : c.value < 0 ? '−' : ''
  return sign + Math.abs(c.value).toFixed(decimals) + (c.kind === 'pct' ? '%' : '')
}

export function direction(c: Change): 'up' | 'down' | 'flat' {
  const shown = Number(Math.abs(c.value).toFixed(2))
  return shown === 0 ? 'flat' : c.value > 0 ? 'up' : 'down'
}
