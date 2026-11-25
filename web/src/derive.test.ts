import { describe, expect, it } from 'vitest'
import type { Point, Series } from './data'
import { DataError, parseDashboard } from './data'
import { direction, formatChange, geometry, latestChange, windowed } from './derive'

const base = { group: 'fx', name: { th: 'ก', en: 'A' }, sub: { th: 'ข', en: 'B' }, decimals: 2 }
const mk = (over: Partial<Series> & { points: Point[] }): Series =>
  ({ id: 'x', unit: '', frequency: 'daily', ...base, ...over }) as Series

describe('latestChange', () => {
  it('reports a level as a percent change', () => {
    const c = latestChange(mk({ points: [['2026-01-01', 40], ['2026-01-02', 41]] }))
    expect(formatChange(c)).toBe('+2.50%')
  })

  it('reports a rate as a points difference with no percent sign', () => {
    const c = latestChange(mk({ unit: '%', frequency: 'monthly', points: [['2026-01-01', 1.0], ['2026-02-01', 0.75]] }))
    expect(formatChange(c)).toBe('−0.25')
    expect(direction(c)).toBe('down')
  })

  it('reports a decision series by its last decision, not by the carried-forward point', () => {
    const c = latestChange(mk({
      unit: '%', frequency: 'event',
      points: [['2024-01-01', 2.5], ['2025-06-01', 2.25], ['2025-11-01', 2.0], ['2026-11-25', 2.0]],
    }))
    expect(formatChange(c)).toBe('−0.25')
  })

  it('calls a change that rounds to zero flat', () => {
    expect(direction({ value: 0.001, kind: 'pct' })).toBe('flat')
  })
})

describe('windowed', () => {
  it('keeps the policy rate in force at the start of the window', () => {
    const s = mk({ unit: '%', frequency: 'event', points: [['2023-01-01', 2.5], ['2026-01-10', 2.25], ['2026-11-25', 2.25]] })
    const pts = windowed(s, '6M')
    expect(pts[0]).toEqual(['2026-05-27', 2.25])
    expect(pts.at(-1)).toEqual(['2026-11-25', 2.25])
  })

  it('drops daily points older than the range', () => {
    const s = mk({ points: [['2025-01-01', 1], ['2026-06-01', 2], ['2026-11-25', 3]] })
    expect(windowed(s, '6M').map(([d]) => d)).toEqual(['2026-06-01', '2026-11-25'])
  })
})

describe('geometry', () => {
  it('places points by date, so a gap in time is a gap on the chart', () => {
    const g = geometry([['2026-01-01', 1], ['2026-01-02', 2], ['2026-01-11', 3]], 100, 50, 0, false)
    const xs = g.line.split(' ').map((p) => Number(p.split(',')[0]))
    expect(xs).toEqual([0, 10, 100])
  })
})

describe('parseDashboard', () => {
  const good = {
    generated: '2026-11-25T18:00:00+07:00', source: 'bot',
    groups: [{ id: 'fx', name: { th: 'ค่าเงิน', en: 'FX' } }],
    series: [{ id: 'usd_thb', ...base, unit: '', frequency: 'daily', points: [['2026-11-24', 32.7], ['2026-11-25', 32.74]] }],
  }

  it('accepts the file build_data.py writes', () => {
    expect(parseDashboard(good).series[0]!.points).toHaveLength(2)
  })

  it('names the field when the shape is wrong', () => {
    const bad = structuredClone(good)
    bad.series[0]!.points[1] = ['2026-11-25', 'n/a'] as never
    expect(() => parseDashboard(bad)).toThrow(new DataError('data.series[0].points[1][1] is not a number'))
  })

  it('rejects points out of date order', () => {
    const bad = structuredClone(good)
    bad.series[0]!.points.reverse()
    expect(() => parseDashboard(bad)).toThrow(/is not after the point before it/)
  })
})
