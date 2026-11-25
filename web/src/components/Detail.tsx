import type { ReactNode } from 'react'
import type { Dashboard, Lang, Series } from '../data'
import type { Range } from '../derive'
import { RANGES, direction, formatChange, formatValue, geometry, last, latestChange, rangeChange, windowed } from '../derive'
import type { Strings } from '../i18n'
import { formatDate } from '../i18n'

interface Props {
  data: Dashboard
  series: Series
  lang: Lang
  t: Strings
  range: Range
  onRange: (r: Range) => void
  onBack: () => void
  langButton: ReactNode
}

const W = 358
const H = 220

export function Detail({ data, series: s, lang, t, range, onRange, onBack, langButton }: Props) {
  const pts = windowed(s, range)
  const ch = rangeChange(s, pts)
  const tone = direction(ch)
  const g = geometry(pts, W, H, 8, s.frequency === 'event')
  const values = pts.map(([, v]) => v)
  const move = latestChange(s)
  const group = data.groups.find((x) => x.id === s.group)
  const lastPoint = last(s)
  return (
    <main className="screen">
      <div className="toolbar">
        <button className="back" onClick={onBack}>
          <svg width="12" height="20" viewBox="0 0 12 20" aria-hidden="true"><path d="M10 2 2 10l8 8" /></svg>
          {t.back}
        </button>
        {langButton}
      </div>
      <header className="detail-title">
        {group && <p className={`eyebrow tint-${s.group}`}>{group.name[lang]}</p>}
        <h1>{s.name[lang]}</h1>
        <p className="meta">{s.sub[lang]}</p>
      </header>
      <div className="headline">
        <span className="big">{formatValue(s, lastPoint[1])}</span>
        <span className={`fg-${tone}`}>{formatChange(ch)} {t.over} {range}</span>
      </div>
      <div className="segmented" role="group" aria-label={t.range}>
        {(Object.keys(RANGES) as Range[]).map((r) => (
          <button key={r} aria-pressed={r === range} onClick={() => onRange(r)}>{r}</button>
        ))}
      </div>
      <svg className="chart" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" role="img"
        aria-label={`${s.name[lang]} ${formatChange(ch)} ${t.over} ${range}`}>
        <line className="baseline" x1="0" x2={W} y1={g.baseY} y2={g.baseY} />
        <polygon className={`area fill-${tone}`} points={g.area} />
        <polyline className={`stroke-${tone}`} points={g.line} />
      </svg>
      <dl className="card stats">
        <div><dt>{t.latest}</dt><dd>{formatValue(s, lastPoint[1])}</dd></div>
        <div><dt>{t.lastMove}</dt><dd className={`fg-${direction(move)}`}>{formatChange(move)}</dd></div>
        <div><dt>{t.high}</dt><dd>{formatValue(s, Math.max(...values))}</dd></div>
        <div><dt>{t.low}</dt><dd>{formatValue(s, Math.min(...values))}</dd></div>
      </dl>
      <p className="footnote">
        {t.asOf} {formatDate(lastPoint[0], lang)} · {data.source === 'sample' ? t.sampleSource : `${t.sourceLabel} ${s.source[lang]}`}
      </p>
    </main>
  )
}
