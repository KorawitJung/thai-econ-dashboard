import { describe, expect, it } from 'vitest'
import type { Point, Series } from './data'
import { DataError, parseDashboard } from './data'
import { direction, formatChange, geometry, latestChange, windowed } from './derive'

const base = { group: 'fx', name: { th: 'ก', en: 'A' }, sub: { th: 'ข', en: 'B' }, source: { th: 'ค', en: 'C' }, decimals: 2 }
const mk = (over: Partial<Series> & { points: Point[] }): Series =>
  ({ id: 'x', unit: '', frequency: 'daily', change: 'pct', ...base, ...over }) as Series

describe('latestChange', () => {
  it('reports a level as a percent change', () => {
    const c = latestChange(mk({ points: [['2026-01-01', 40], ['2026-01-02', 41]] }))
    expect(formatChange(c)).toBe('+2.50%')
  })

  it('reports a rate as a points difference with no percent sign', () => {
    const c = latestChange(mk({ unit: '%', change: 'diff', frequency: 'monthly', points: [['2026-01-01', 1.0], ['2026-02-01', 0.75]] }))
    expect(formatChange(c)).toBe('−0.25')
    expect(direction(c)).toBe('down')
  })

  it('reports a decision series by its last decision, not by the carried-forward point', () => {
    const c = latestChange(mk({
      unit: '%', change: 'diff', frequency: 'event',
      points: [['2024-01-01', 2.5], ['2025-06-01', 2.25], ['2025-11-01', 2.0], ['2026-11-25', 2.0]],
    }))
    expect(formatChange(c)).toBe('−0.25')
  })

  it('reports a balance that crosses zero as a difference, since a percent of a deficit means nothing', () => {
    const c = latestChange(mk({ change: 'diff', frequency: 'monthly', points: [['2026-08-01', -0.4], ['2026-09-01', 1.1]] }))
    expect(formatChange(c)).toBe('+1.50')
    expect(direction(c)).toBe('up')
  })

  it('calls a change that rounds to zero flat', () => {
    expect(direction({ value: 0.001, kind: 'pct' })).toBe('flat')
  })
})

describe('windowed', () => {
  it('keeps the policy rate in force at the start of the window', () => {
    const s = mk({ unit: '%', change: 'diff', frequency: 'event', points: [['2023-01-01', 2.5], ['2026-01-10', 2.25], ['2026-11-25', 2.25]] })
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
    generated: '2026-11-25T18:00:00+07:00', source: 'live',
    groups: [{ id: 'fx', name: { th: 'ค่าเงิน', en: 'FX' } }],
    series: [{ id: 'usd_thb', ...base, unit: '', frequency: 'daily', change: 'pct', points: [['2026-11-24', 32.7], ['2026-11-25', 32.74]] }],
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

  const meeting = { date: '2026-10-28', decision: { th: 'คงอัตรา', en: 'Held the rate' } }

  it('keeps the last meeting when a series has one, and leaves it out otherwise', () => {
    const withMeeting = { ...good, series: [{ ...good.series[0]!, meeting }] }
    expect(parseDashboard(withMeeting).series[0]!.meeting).toEqual(meeting)
    expect(parseDashboard(good).series[0]).not.toHaveProperty('meeting')
  })

  it('rejects a meeting date that is not YYYY-MM-DD, or a meeting with no decision text', () => {
    const badDate = { ...good, series: [{ ...good.series[0]!, meeting: { ...meeting, date: '2026/10/28' } }] }
    expect(() => parseDashboard(badDate)).toThrow(new DataError('data.series[0].meeting.date is not a YYYY-MM-DD date'))
    const noText = { ...good, series: [{ ...good.series[0]!, meeting: { date: '2026-10-28' } }] }
    expect(() => parseDashboard(noText)).toThrow(new DataError('data.series[0].meeting.decision is not an object'))
  })

  it('rejects a series that does not say how to measure its change', () => {
    const bad = { ...good, series: [{ ...good.series[0]!, change: 'pp' }] }
    expect(() => parseDashboard(bad)).toThrow(new DataError('data.series[0].change "pp" is unknown'))
  })
})

describe('parseDashboard source', () => {
  it('requires each series to say where its data came from', () => {
    const bad = {
      generated: '2026-11-25T18:00:00+07:00', source: 'live',
      groups: [{ id: 'fx', name: { th: 'ค่าเงิน', en: 'FX' } }],
      series: [{ id: 'usd_thb', group: 'fx', name: { th: 'ก', en: 'A' }, sub: { th: 'ข', en: 'B' }, decimals: 2, unit: '', frequency: 'daily', change: 'pct', points: [['2026-11-24', 1], ['2026-11-25', 2]] }],
    }
    expect(() => parseDashboard(bad)).toThrow(new DataError('data.series[0].source is not an object'))
  })
})
