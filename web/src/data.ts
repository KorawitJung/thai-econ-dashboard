export type Lang = 'th' | 'en'
export type Text = Record<Lang, string>
export type Frequency = 'daily' | 'monthly' | 'event'
export type Point = readonly [date: string, value: number]

export interface Series {
  id: string
  group: string
  name: Text
  sub: Text
  unit: string
  decimals: number
  frequency: Frequency
  points: Point[]
}

export interface Group {
  id: string
  name: Text
}

export interface Dashboard {
  generated: string
  source: 'bot' | 'sample'
  groups: Group[]
  series: Series[]
}

export class DataError extends Error {}

type Obj = Record<string, unknown>

function obj(x: unknown, at: string): Obj {
  if (typeof x !== 'object' || x === null || Array.isArray(x)) throw new DataError(`${at} is not an object`)
  return x as Obj
}

function str(o: Obj, key: string, at: string): string {
  const v = o[key]
  if (typeof v !== 'string') throw new DataError(`${at}.${key} is not a string`)
  return v
}

function list(o: Obj, key: string, at: string): unknown[] {
  const v = o[key]
  if (!Array.isArray(v)) throw new DataError(`${at}.${key} is not a list`)
  return v
}

function text(o: Obj, key: string, at: string): Text {
  const t = obj(o[key], `${at}.${key}`)
  return { th: str(t, 'th', `${at}.${key}`), en: str(t, 'en', `${at}.${key}`) }
}

const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/
const FREQUENCIES: readonly Frequency[] = ['daily', 'monthly', 'event']

function point(x: unknown, at: string): Point {
  if (!Array.isArray(x) || x.length !== 2) throw new DataError(`${at} is not a [date, value] pair`)
  const [d, v] = x
  if (typeof d !== 'string' || !ISO_DATE.test(d)) throw new DataError(`${at}[0] is not a YYYY-MM-DD date`)
  if (typeof v !== 'number' || !Number.isFinite(v)) throw new DataError(`${at}[1] is not a number`)
  return [d, v]
}

function series(x: unknown, at: string, groupIds: Set<string>): Series {
  const o = obj(x, at)
  const frequency = str(o, 'frequency', at)
  if (!FREQUENCIES.includes(frequency as Frequency)) throw new DataError(`${at}.frequency "${frequency}" is unknown`)
  const group = str(o, 'group', at)
  if (!groupIds.has(group)) throw new DataError(`${at}.group "${group}" is not in groups`)
  const decimals = o.decimals
  if (typeof decimals !== 'number' || !Number.isInteger(decimals) || decimals < 0) throw new DataError(`${at}.decimals is not a whole number`)
  const points = list(o, 'points', at).map((p, i) => point(p, `${at}.points[${i}]`))
  if (points.length < 2) throw new DataError(`${at}.points has fewer than 2 points`)
  for (let i = 1; i < points.length; i++) {
    if (points[i]![0] <= points[i - 1]![0]) throw new DataError(`${at}.points[${i}] is not after the point before it`)
  }
  return {
    id: str(o, 'id', at), group, name: text(o, 'name', at), sub: text(o, 'sub', at),
    unit: str(o, 'unit', at), decimals, frequency: frequency as Frequency, points,
  }
}

export function parseDashboard(x: unknown): Dashboard {
  const o = obj(x, 'data')
  const source = str(o, 'source', 'data')
  if (source !== 'bot' && source !== 'sample') throw new DataError(`data.source "${source}" is unknown`)
  const groups = list(o, 'groups', 'data').map((g, i) => {
    const at = `data.groups[${i}]`
    const go = obj(g, at)
    return { id: str(go, 'id', at), name: text(go, 'name', at) }
  })
  const groupIds = new Set(groups.map((g) => g.id))
  return {
    generated: str(o, 'generated', 'data'),
    source,
    groups,
    series: list(o, 'series', 'data').map((s, i) => series(s, `data.series[${i}]`, groupIds)),
  }
}
